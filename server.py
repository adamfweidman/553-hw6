#!/usr/bin/env python

import os
import socket
import struct
import sys
from threading import Lock, Thread
import pickle 

from time import sleep 


QUEUE_LENGTH = 10
SEND_BUFFER = 2047

songNameToData = {}


# per-client struct
class Client:
    def __init__(self, sock):
        self.lock = Lock()
        self.songRequest = ""
        self.currentCommand = ""
        self.s = sock 
        self.songLoc = 0
        self.quit = False 
        self.songNum = None 
        self.playing = False
        self.onceList = 0

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
    while True:
        command = client.getCommand()
        song = client.getCurrentSong()
        if command == "list" and client.onceList == 1:
            data = struct.pack('1si',b'l',int(song))
            data += pickle.dumps((list(songNameToData.keys())), protocol=2)
            data += b"0" * (2049 - len(data))
            client.s.sendall(data)
            client.onceList = 0 
            # print(data)
        elif command == "play":
            # while command == "play": 
                # command = client.getCommand()
                # if command != "stop" and not client.quit: 
            hdr = struct.pack('1s',b'p')
            pos_end_range = min(len(songNameToData[song])-1, client.songLoc+SEND_BUFFER)
            song_data = songNameToData[song][client.songLoc:pos_end_range]
            client.s.sendall(hdr+song_data)
            client.songLoc = pos_end_range
                #print("sent:", song_data)
        
        elif command == "quit":
            return

            

    # data = songNameToData[song]
    # client.s.send(data)

# TODO: Thread that receives commands from the client.  All recv() calls should
# be contained in this function.
def client_read(client, addr):
    while True: 
        command, song = pickle.loads(client.s.recv(2048))
        if command in ["list", "l"]:
            print("List Command recieved")
            client.setCommand("list")
            client.onceList = 1

        elif command in ['p', 'play']:
            if int(song) in range(len(songNameToData)):
                client.setCommand("play")
                if client.songNum != song: 
                    client.songLoc = 0 
                client.songNum = song 
                client.setSong(list(songNameToData.keys())[int(song)])
            else:
                print("This song number is not a possibility")
                

        elif command in ['s', 'stop']: 
            client.setCommand("stop")

        elif command in ['quit', 'q', 'exit']:
            client.quit = True 
            client.s.close() 
            print("Client Closed {}".format(addr))
            return    

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
        #print(songNameToData)

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
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            # with conn: 
            print("Connection from ", addr)
            # TODO: create a socket and accept incoming connections
            # while True:
            client = Client(conn)
            t = Thread(target=client_read, args=[client, addr])
            threads.append(t)
            t.start()
            t = Thread(target=client_write, args=[(client)])
            threads.append(t)
            t.start()
        s.close()


if __name__ == "__main__":
    main()