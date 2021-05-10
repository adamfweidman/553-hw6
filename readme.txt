"""""""""""""""
"  README.TXT "
"""""""""""""""

Group #15
Authors: Micah Weitzman and Adam Weidman 


TO USE

Client side: 
Run: 
    ./client.py [server_ip] [server_port]

Commands:
    l/list      - get list of songs 
    p/play XX   - play song number XX (make sure to include 2 digits. Eg: p 01)
    s/stop      - stop current song
    q/quit/exit - exit current instance 


Server side:
Run:
    python3 server.py [port] [musicdir] [local ip]

Details:
    Upload to EC2 isntance as described in README.md 