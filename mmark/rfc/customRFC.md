%%%
Title = "Custom Protocol to Implement Server/Client Music Streaming"
abbrev = "Custom Protocol to Implement Server/Client Music Streaming"
ipr= "trust200902"
area = "Internet"
workgroup = "CIS553 final project group"
submissiontype = "IETF"
keyword = [""]
#date = 2021-04-20T00:00:00Z

[seriesInfo]
name = "customRFC"
value = "5111"
stream = "IETF"
status = "informational"

[[author]]
initials="A."
surname="Weidman"
fullname="Adam Weidman"
organization = "UPenn"
  [author.address]
  email = "adambis@sas.upenn.edu"

[[author]]
initials="M."
surname="Weitzman"
fullname="Micah Weitzman"
organization = "UPenn"
  [author.address]
  email = "wmicah@seas.upenn.edu"
%%%

.# Abstract

This document proposes a custom protocol to implement Server/Client music Ssreaming

{mainmatter}

# Introduction

This is a protocol designed by Adam Weidman and Micah Weitzman in order to implement a music 
streaming server/client behavior that is outlined in hw6 of CIS553 (<https://bitbucket.org/penncis553/553-hw6/src/master/setup/>)

# Types of Messages

- list: The client will request the list of songs with: "list\n" at which point the server will respond by sending the current dictionary (song -> ID), in string format.
- play [song number]: The client will request to play a song number with: "play *\n", where * is a song number. If this is a valid song number the server will open a new port from which the audio will be sent. This port number will be send to the client.
- stop: Client will request for the current song being played/sent to be stopped with "stop\n". Once the server stops sending the song, it will respond with "stopped\n"

# Message Format and Framing

- The message issue by the client will be a string (one of three outlined in "types of messages"). The end of each prompt by the client will end with the (python )new line character "\n".
- The music being sent will be sent in binary (similar to udp)

# State

## State Stored by Server per-Client
The Server will store the socket used to currently stream music to each client. In addition must keep track of sending audio to the correct client that requested it. 

## Client states
Client will maintain the current song, and command. 

# Message transitions from server/client
- Server will keep track of which client is connected to which socket, with function from socket class: socket.getpeername()
- Will then find the command issued along that socket to the server with the receive() function

