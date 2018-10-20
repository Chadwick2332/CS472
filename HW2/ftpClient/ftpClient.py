#!/usr/bin/python3

# based on https://docs.python.org/3/howto/sockets.html

# ----------------------------------------------------
#                       FTPClient
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

def doProtocol(sock) :
	value = int(sys.argv[1])

	# pack and send our argument
	data = struct.pack("i", value)
	sock.send(data)

	# get back a response and unpack it
	receivedMessage = sock.recv(4)
	chunk = struct.unpack("i", receivedMessage)
	# take the first int only
	message = chunk[0]

	print("client received: " + str(message))

def commandLoop(sock):
	""""This function is the user interface that parses a users desired command and value."""
	while True:
		user_input = input("ftpclient>")
		user_token = user_input.split(" ")

		# value = int(sys.argv[1])

		# pack and send our argument
		data = struct.pack("s", user_input)
		sock.send(data)

		command = user_token[0]
		value = user_token[1]

		if DEBUG:
			print("Command:", command)
			print("Value:", value)



def main() :
	# if len(sys.argv) != 2 or not sys.argv[1].isdigit() :
	# 	print("Usage: " + str(sys.argv[0]) + " <int>")
	# 	exit(1)

	# create an INET, STREAMing socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# now connect to the web server on port 9223, which we've made our server listen to
	# change the hostname if not on the same server
	print("Connecting to FTP " + FTP_HOST + " at port " + str(PORT))
	sock.connect((FTP_HOST, PORT))
	# doProtocol(sock)
	commandLoop(sock)
	sock.close()

if __name__ == "__main__" :
	main()
