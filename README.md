# DeathStar
Python webserver that receives shell connections from remote devices. 

Remote devices can be managed from the DeathStar webpage.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP labs. #Hobbies

# Web page
<img width="1162" alt="Screenshot 2024-12-21 at 1 03 20 AM" src="https://github.com/user-attachments/assets/9145dc13-14d0-440c-9d00-9a60f547bbc5" />

# Download DeathStar

```git clone github.com/bwithe/deathstar```

# Web C2 server 
1. Start the server
    - `python3 deathstar.py`

2. Open link in web browser
    - `firefox 127.0.0.1:8000`

3. Modify `<DEATHSTAR_IP>` in `client.py`

4. Have CLIENT connect to C2
    - Linux / MacOS
      - `python3 client.py`
    - Windows
        - `powershell -bypass client.ps1`
