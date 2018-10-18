#!/usr/bin/python3

# based on https://docs.python.org/3/howto/sockets.html

import socket
import struct
import sys

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

def main() :
	if len(sys.argv) != 2 or not sys.argv[1].isdigit() :
		print("Usage: " + str(sys.argv[0]) + " <int>")
		exit(1)

	# create an INET, STREAMing socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# now connect to the web server on port 9223, which we've made our server listen to
	# change the hostname if not on the same server
	sock.connect((socket.gethostname(), 9223)) 
	doProtocol(sock)
	sock.close()

if __name__ == "__main__" :
	main()
