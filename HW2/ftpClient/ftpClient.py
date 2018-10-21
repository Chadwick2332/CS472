#!/usr/bin/python3

# based on https://docs.python.org/3/howto/sockets.html

# CS 472 - Homework #2
# Chad Dotson-Jones
# ftpClient.py


# ----------------------------------------------------
# |                     FTPClient     		     |
# ----------------------------------------------------
#
# Contains the main run loop of the script
#
#


import socket
import struct
import sys

# ---------------
#	Default		|
# ---------------

DEBUG = True
PORT = 21
FTP_HOST = "10.246.251.93"

class FTPClient:

    def __init__(self):
        self.DEBUG    = True
        self.PORT     = 21
        self.FTP_HOST = "10.246.251.93"

    def sendMessage(self, sock, message):
        # From Example
        # value = int(sys.argv[1])
        #
        # # pack and send our argument
        # data = struct.pack("i", value)
        # sock.send(data)

        sock.send(message)

    def receiveMessage(self, sock_file):
        # From Example
        # # get back a response and unpack it
        # receivedMessage = sock.recv(4)
        # chunk = struct.unpack("i", receivedMessage)
        # # take the first int only
        # message = chunk[0]

	# I attempted to use recv but was unable to getting an response besides the the banner
	# I instead choose to use the Socket makefile() 
        # receivedMessage = sock.recv(1024)
           
	file_line = sock_file.readline()


        if self.DEBUG:
	   print("DEBUG - REPLY: " + file_line)

	return file_line
 

    def getCode(self, reply):
	"""Reads through the reply file generate by socket. and parses out the reply code function groups.
		Ex:
			200 Command okay.
			220 Service ready for new user.
	"""

	# If the file is empty
	if not reply:
	   return 'EOF'

	reply_code = reply[:3]


	if DEBUG:
	    print("DEBUG - CODE: " + reply_code)

	return reply_code


    def getUserCommand(self):
        """"This function is the user interface that parses a users desired command and value.
	    Possible Commands:
		USER, PASS, CWD, QUIT, PWD, SYST, LIST, HELP

	    Data Transfer Command:
		PASV, EPSV, PORT, EPRT, RETR, STOR
		
	
	"""
	user_input = ""	

	
	while True:

	    	     
            user_input = raw_input("ftpclient>")

            user_token = user_input.split(" ")
        # value = int(sys.argv[1])
	    # Some commands don't require values
            command = user_token[0]
	    value = ""

	    
	    if(len(user_token) == 2) and (command.upper() in ("USER", "PASS", "PORT")):

        	value = user_token[1]
		
		return command, value

	    elif(len(user_token) == 1) and (command.upper() in ("CWD","PWD", "LIST", "HELP", "QUIT")):
	
		return command, ""	
	    else:
		print("Invalid Command.")
		
	

        if DEBUG:
           print("Command:", command)
           print("Value:", value)

    def mainLoop(self):
	"""This is the main control loop of the protocol. Since FTP is a 'server speaks first' system
	   our loop will start by waiting for a reply from the server. 


	"""

	# create an INET, STREAMing socket
    	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    	# Socket file for server responses
    	socket_file = sock.makefile('r')


    	print("Connecting to FTP Server at " + self.FTP_HOST + ":" + str(self.PORT))
	
    	sock.connect((self.FTP_HOST, self.PORT))

	print("Connected to " + self.FTP_HOST + " at " + str(self.PORT))

	while True:
	    reply = self.receiveMessage(socket_file)

	    print(reply)

	    reply_code = self.getCode(reply)

	    # If server connection is terminating (hard error)
	    if reply_code in ('221', '421', '426', 'EOF'):
		print("Connection terminated. Closing FTPClient...")
		break

	    # User Input
	    command = ""
	    value = ""
	    command, value = self.getUserCommand()

	    if command != "":
		message = command + (1 if len(value) >= 1 else 0)*(" " + value)
		if self.DEBUG:
		   print("DEBUG - SEND :" + message)

	    	self.sendMessage(sock, message + "\r\n")
	    else:
		break
	    # If invalid command (soft error)
	
	sock.close()

def main():


    if len(sys.argv) == 1:
	print("Using default address and log file.")
	
    if len(sys.argv) == 2 and isinstance(sys.argv[1], str):
	print("Using address " + sys.argv[1] + ". No log file given.")
	
    if len(sys.argv) == 3 and isinstance(sys.argv[2], str):
    	print("Using address " + sys.argv[1] + ". Logging interaction at " + sys.argv[2])
	
    if len(sys.argv) >= 4:
	print("Too many arguments.")
	exit(1)

        # FTP Client
    ftp = FTPClient()
    # now connect to the web server on port 9223, which we've made our server listen to
    # change the hostname if not on the same server

    # FTP is a 'server speaks first' system so recive a 220 banner
    ftp.mainLoop()



if __name__ == "__main__":
    main()
