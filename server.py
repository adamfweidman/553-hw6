#!/usr/bin/env python

import os
import socket
import struct
import sys
from threading import Lock, Thread


QUEUE_LENGTH = 10
SEND_BUFFER = 4096

songNameToData = {}


# per-client struct
class Client:
    def __init__(self, sock):
        self.lock = Lock()
        self.songRequest = ""
        self.currentCommand = ""
        self.s = sock 

    def setSong(self, songName):
        self.songRequest = songName
    def getCurrentSong(self):
        return self.songRequest
    def setCommand(self, command):
        self.currentCommand = command
    def getCommand(self):
        return self.currentCommand

# TODO: Thread that sends music and lists to the client.  All send() calls
# should be contained in this function.  Control signals from client_read could
# be passed to this thread through the associated Client object.  Make sure you
# use locks or similar synchronization tools to ensure that the two threads play
# nice with one another!
def client_write(client):
    command = client.getCommand()
    song = client.getCurrentSong()
    
    if(command == "list"):
        data=struct.pack(songNameToData.keys())
        client.s.sendall(data)
    elif(command == "play"):
        relData = songNameToData[song]
        client.s.sendall(relData)

    # data = songNameToData[song]
    # client.s.send(data)

# TODO: Thread that receives commands from the client.  All recv() calls should
# be contained in this function.
def client_read(client):
    # command, song = client.s.recv(2048)
    command= client.s.recv(2048)
    if command in ["list", "l"]:
        client.setCommand("list")
        client_write(client)
    # elif(command == "play"):
    #     client.setCommand("play")
    #     client.setSong(song)
    #     client_write(client)
    # elif(command == "stop"): 
    #     client.setCommand("stop")
    #     client_write(client)
    else:
        print("Bye!")
        exit(0)

def get_mp3s(musicdir):
    print("Reading music files...")
    songs = []

    for filename in os.listdir(musicdir):
        if not filename.endswith(".mp3"):
            continue
        else: 
            curDir = os.getcwd() + "/" + musicdir + "/" + filename
            songFile =  open(curDir, 'rb')
            filedata = songFile.read()
            songName = filename.split(".mp3")[0]
            songNameToData[songName] = filedata
            songs.append(songName)
        # TODO: Store song metadata for future use.  You may also want to build
        # the song list once and send to any clients that need it.

    print("Found {0} song(s)!".format(len(songs)))
    return songs 

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [port] [musicdir]")
    if not os.path.isdir(sys.argv[2]):
        sys.exit("Directory '{0}' does not exist".format(sys.argv[2]))

    port = int(sys.argv[1])
    #songs, songlist = get_mp3s(sys.argv[2])
    songs = get_mp3s(sys.argv[2])
    threads = []

    HOST = '172.31.32.221'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn: 
            print("Connection from ", addr)
            # TODO: create a socket and accept incoming connections
            # while True:
            client = Client(conn)
            t = Thread(target=client_read, args=[(client)])
            threads.append(t)
            t.start()
            t = Thread(target=client_write, args=[(client)])
            threads.append(t)
            t.start()
            while True:
                pass 
    s.close()


if __name__ == "__main__":
    main()