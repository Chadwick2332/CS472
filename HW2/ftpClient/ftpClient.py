#!/usr/bin/python3

# CS 472 - Homework #2
# Chad Dotson-Jones
# ftpClient.py


# ----------------------------------------------------
# |                     FTPClient     		     |
# ----------------------------------------------------
# Client takes in an address and port and connects to 
# any FTP server. 
# 
# Command-line input will let you send command to the
# commands to the server.
#
import time
import datetime
import socket
import struct
import sys


class FTPClient:

    def __init__(self, debug=False, port=21, host="10.246.251.93", sock=None, log="" ):
        self.DEBUG    = debug
        self.PORT     = port  
        self.FTP_HOST = host
	self.SOCK     = sock
	self.LOG      = log

    def createConnection(self):

    	print("Connecting to FTP Server at " + self.FTP_HOST + ":" + str(self.PORT))

	try:
	    # create an INET, STREAMing socket
    	    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
	
    	    sock.connect((self.FTP_HOST, self.PORT))
        
	    print("Connected to " + self.FTP_HOST + " at " + str(self.PORT))
	    
	    self.SOCK = sock
	except KeyboardInterrupt:
	    self.closeConnection()

    def closeConnection(self):
	print("Connection terminated. Closing FTPClient...")
	self.SOCK.close()

    def log(self, logMessage):

	ts = time.time()

	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S.%f')

	f = open(self.LOG, "a+")

	f.write(timestamp + " " + logMessage)

	if self.DEBUG:
	   print("DEBUG-LOG:" + timestamp + " " + logMessage)



    def sendMessage(self, message):
	"""Sends message to server connect to socket. """
        self.SOCK.send(message)

	self.log("Sent: " + message)

    def receiveMessage(self, sock_file):
	"""Takes log file generated but socket, and reads the first line. This will be empty
	unless the server as sent a message.
	"""

	# I attempted to use recv but was unable to getting an response besides the the banner
	# I instead choose to use the Socket makefile() 
        # receivedMessage = sock.recv(1024)
           
	file_line = sock_file.readline()

	self.log("Received: " + file_line)

        if self.DEBUG:
	   print("DEBUG - REPLY: " + file_line)

	return file_line
 

    def getCode(self, reply):
	"""Parses out the reply code function groups.
		Ex:
			200 Command okay.
			220 Service ready for new user.
	"""

	# If the file is empty
	if not reply:
	   return 'EOF'

	reply_code = reply[:3]


	if self.DEBUG:
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

	    # Some commands don't require values
            command = user_token[0]
	    value = ""

	    # Splitting the string before sending it to the server was not nessicarry in the end
	    # but I keep this functionality just incase.
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
	self.createConnection()


    	#  Socket file for server responses
    	socket_file = self.SOCK.makefile('r')


	while True:
	    reply = self.receiveMessage(socket_file)
	    print(reply)

	    reply_code = self.getCode(reply)

	    # If server connection is terminating (hard error)
	    if reply_code in ('221', '421', '426', 'EOF'):
		self.closeConnection()
		break

	    # User Input
	    command = ""
	    value = ""
	    command, value = self.getUserCommand()

	    if command != "":
		message = command + (1 if len(value) >= 1 else 0)*(" " + value)
		if self.DEBUG:
		   print("DEBUG - SEND :" + message)

	    	self.sendMessage(message + "\r\n")
	    else:
		break
	

def main():


    if len(sys.argv) == 1:
	print("No arguements given. Usage: python FTPClient.py <hostname> <logfile>")
	
    if len(sys.argv) == 2 and isinstance(sys.argv[1], str):
	print("Using address " + sys.argv[1] + ". No log file given.")

    	# FTP Client
    	ftp = FTPClient(host=sys.argv[1])

	ftp.mainLoop()
	
    if len(sys.argv) == 3 and isinstance(sys.argv[2], str):
    	print("Using address " + sys.argv[1] + ". Logging interaction at " + sys.argv[2])
	
	# FTP Client
    	ftp = FTPClient(host=sys.argv[1], log=sys.argv[2], debug=True)

	ftp.mainLoop()


    if len(sys.argv) >= 4:
	print("Too many arguments.")
	exit(1)

    # now connect to the web server on port 9223, which we've made our server listen to
    # change the hostname if not on the same server

    

if __name__ == "__main__":
    main()
