#!/usr/bin/env python

import pickle
import ao
import mad
import readline
import socket
import struct
import sys
import threading
from time import sleep

# The Mad audio library we're using expects to be given a file object, but
# we're not dealing with files, we're reading audio data over the network.  We
# use this object to trick it.  All it really wants from the file object is the
# read() method, so we create this wrapper with a read() method for it to
# call, and it won't know the difference.
# NOTE: You probably don't need to modify this class.
class mywrapper(object):
    def __init__(self):
        self.mf = None
        self.data = ""
        self.ready = False 
        self.slow_start = False 
        self.stopped = False 

    # When it asks to read a specific size, give it that many bytes, and
    # update our remaining data.
    def read(self, size):
        result = self.data[:size]
        self.data = self.data[size:]
        return result


# Receive messages.  If they're responses to info/list, print
# the results for the user to see.  If they contain song data, the
# data needs to be added to the wrapper object.  Be sure to protect
# the wrapper with synchronization, since the other thread is using
# it too!
def recv_thread_func(wrap, cond_filled, sock):
    while True:
        recv_data = sock.recv(2049) # test value 
        if recv_data == "":
            continue
        command = struct.unpack("1s", recv_data[0])
        if command[0] != "p": 
            print(command)
        if command[0] == "l": 
            data = pickle.loads(recv_data[1:])
            print("\n")
            for song in range(len(data)):
                print "%d) %s" % (song, data[song]) 

        if command[0] == "p":
            data = recv_data[1:]
            cond_filled.acquire()
            wrap.data += data
            wrap.ready = True 
            wrap.slow_start = True 
            cond_filled.release()

        else: 
            continue
        sleep(0.01)
        


# If there is song data stored in the wrapper object, play it!
# Otherwise, wait until there is.  Be sure to protect your accesses
# to the wrapper with synchronization, since the other thread is
# using it too!
def play_thread_func(wrap, cond_filled, dev):
    wrap.mf = mad.MadFile(wrap)
    # sleep(10)
    while True:
        if wrap.slow_start: 
            sleep(5)
            cond_filled.acquire()
            wrap.slow_start = False 
            cond_filled.release()
        while wrap.ready and not wrap.stopped: 
            cond_filled.acquire()
            buf = wrap.mf.read()
            cond_filled.release()
            if buf is None:  # eof
                continue  
            dev.play(buffer(buf), len(buf))
        
        """
        TODO
        example usage of dev and wrap (see mp3-example.py for a full example):
        buf = wrap.mf.read()
        dev.play(buffer(buf), len(buf))
        """

def main():
    if len(sys.argv) < 3:
        print 'Usage: %s <server name/ip> <server port>' % sys.argv[0]
        sys.exit(1)

    # Create a pseudo-file wrapper, condition variable, and socket.  These will
    # be passed to the thread we're about to create.
    wrap = mywrapper()

    # Create a condition variable to synchronize the receiver and player threads.
    # In python, this implicitly creates a mutex lock too.
    # See: https://docs.python.org/2/library/threading.html#condition-objects
    cond_filled = threading.Condition(threading.Lock())

    # Create a TCP socket and try connecting to the server.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))

    # Create a thread whose job is to receive messages from the server.
    recv_thread = threading.Thread(
        target=recv_thread_func,
        args=(wrap, cond_filled, sock)
    )
    recv_thread.daemon = True
    recv_thread.start()

    # Create a thread whose job is to play audio file data.
    dev = ao.AudioDevice('pulse')
    # play_thread = threading.Thread(
    #     target=play_thread_func,
    #     args=(wrap, cond_filled, dev)
    # )
    # play_thread.daemon = True
    # play_thread.start()

    # Enter our never-ending user I/O loop.  Because we imported the readline
    # module above, raw_input gives us nice shell-like behavior (up-arrow to
    # go backwards, etc.).
    while True:
        line = raw_input('>> ')

        if ' ' in line:
            cmd, args = line.split(' ', 1)
        else:
            cmd = line

        # TODO: Send messages to the server when the user types things.
        if cmd in ['l', 'list']:
            print 'The user asked for list.'
            sock.sendall(pickle.dumps((cmd, None)))

        if cmd in ['p', 'play']:
            print 'The user asked to play:', args
            sock.sendall(pickle.dumps((cmd, args)))
            wrap.stopped = False  

        if cmd in ['s', 'stop']:
            wrap.stopped = True 
            print 'The user asked for stop.'
            sock.sendall(pickle.dumps((cmd, None)))


        if cmd in ['quit', 'q', 'exit']:
            sock.sendall(pickle.dumps((cmd, None)))
            sys.exit(0)
            

if __name__ == '__main__':
    main()
