#!/usr/bin/python3

# CS 472 - Homework #3
# Chad Dotson-Jones
# ftpClient.py


# ----------------------------------------------------
# |                     FTPServer     		     |
# ----------------------------------------------------
# This file includes the main FTPServer class aswell as
# a Client class which is inniated when a client connects 
# to the server.
#
# Use the following convention for starting the server:
#       python ftpServer.py LOG PORT [debug]
#
#   LOG: log file for recording
#   PORT: the port number that you would like to open
#        (if is in use another will be selected at random)
#   DEBUG: Prints the debug messeage for the developer
#
#   Example:
#       python ftpServer.py log.txt 4813 true 
#
#
# Authentication is done by parsing a text file with the convention
# {username} {password}. This file is aptly titled superSecretPasswords.
# You may add your own username and password to this file or use example user.
#   Ex.
#       USER: cjd329
#       PASS: 12345
#
# Several commands have no been implement correctly. The command LIST and STOR
# do not return there output on the client side.
#
# The commands ESPV and RETR hav not been implemented

import random
import time
import datetime
import socket
import struct
import sys
import os


class Config:
	def __init__(self, file_loc="", params={}):
		self.file_loc = file_loc
		self.params = params

	def load(self, file_loc):
		try:
			with open(file_loc) as file:
				line = file.readline()
				while line:
					if not self.isComment(line):
						self.evaluate(line)
						line = file.readline()
		except FileNotFoundError:
			print("No such file : {} exists.".format(file_loc))

	def evaluate(self, line):
		"""
		1. Split using '='
		2. Remove leading and trailing spaces
		3. Evaluate Yes or No (Convert to lower case)
		4. Add to dictionary
		"""

		# Remove return
		line = line[:-1]
		tokens = [value.strip() for value in line.split('=')]
		# if tokenized_line as a length less than 2
		if len(tokens) == 2:

			if tokens[1].lower() is 'yes' or 'y':
				self.params[tokens[0]] = True
			elif tokens[1].lower() is 'no' or 'n':
				self.params[tokens[0]] = False
			else:
				print("Value of {} must be either YES or NO (Y or N)".format(tokens[0]))
		else:
			print("Line does not contain an equals")

	def isComment(self, line):
		"""Checks if the first character in a line is '#'. If so,
		then returns True, returns False for all else. """
		for char in line:
			if char is '#':
				return True
			elif char is ' ':
				continue
			else:
				return False


class Client:

	def __init__(self, socket, address, logfile, debug):
		self.SOCKET = socket
		self.ADDR = address
		self.LOG = logfile
		self.DEBUG = debug

		self.MAX_USER_LEN = 50

		# States
		self.isAuth = False
		self.isDataPort = False
		self.isPassive = False

		# varibles
		self.user = ""
		self.cwd = os.getcwd()
		self.homewd = os.getcwd()
		self.datasock = None
		self.dataAddr = None
		self.dataPort = None

		self.serversock = None
		self.serverAddr = None
		self.serverPort = None

		print("Create connection at " + self.ADDR[0])

	def sendMess(self, mess):
		"""Sends message to server connect to socket. """
		self.SOCKET.send(mess + "\r\n")

		mess = "Sent: " + mess

		self.log(mess)

	def recvMess(self):
		return self.SOCKET.recv(1024)

	def parseCommand(self, mess, database):
		"""This is used to parse through a users reply and command word and data. This will link to functions
		to handle each command. It also takes the database of the server as an input so that we can validate the user.
		List of commands:USER, PASS, CWD, CDUP, QUIT, PASV, EPSV, PORT, EPRT, RETR, STOR, PWD,
		SYST, LIST, HELP"""

		mess_list = mess.split()
		command = mess_list[0].upper()

		# TODO Validate that param length is less than

		# DEBUG
		if self.DEBUG:
			print("DEBUG PARSE-COMMAND:", command)

		try:
			if command == "USER":
				return self.doUser(mess_list[1])
			elif command == "PASS":
				return self.doPass(mess_list[1], database)
			elif command == "CWD":
				return self.doCwd(mess_list)
			elif command == "CDUP":
				return self.doCdup()
			elif command == "PASV":
				return self.doPasv()
			elif command == "EPSV":
				return "202 EPSV not implemented"
			elif command == "PORT":
				return self.doPort(mess_list[1])
			elif command == "RETR":
				return "202 RETR not implemented "
			elif command == "STOR":
				return self.doStor(mess_list)
			elif command == "LIST":
				if len(mess_list) == 2:
					return self.doList(mess_list[1])
				else:
					return self.doList("")
			elif command == "SYST":
				return self.doSyst()
			elif command == "HELP":
				return self.doHelp()
			elif command == "PWD":
				return self.doPwd(mess_list)
			elif command == "QUIT":
				return self.doQuit()
			else:
				return "500 Command unrecognized."

		except IndexError:
			return "501 No arguements given."

	def log(self, logMessage):
		ts = time.time()
		timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S.%f')

		f = open(self.LOG, "a+")
		f.write(timestamp + " " + logMessage)

		if self.DEBUG:
			print("DEBUG-LOG:" + timestamp + " " + logMessage)

	def createDatasock(self, port, addr=None):
		""" Creates a data socket to the client to be used once per command. The function
		returns the reply and the socket if it was created successfully."""

		if addr is None:
			addr = self.ADDR[0]
		if not self.isPassive:
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((addr, port))

				# save socket
				self.datasock = sock
				self.isDataPort = True

				return "200 Data connection established."

			except socket.error:
				return "501 Unable to create dataport at given address"

		else:
			self.datasock, _ = self.serversock.accept()

			return "225 Data connection is open."

	def closeDatasock(self):

		self.datasock.close()
		self.datasock = None
		self.isDataPort = False

		self.debug("datasock", "Closing..")

	def debug(self, prefix, data):
		"""Prints out a debug log if debug is enabled in the system."""
		# TODO Fix  all the old debug statements
		if self.DEBUG:
			if data is not list:
				print("DEBUG - " + prefix.upper() + ": " + str(data))
			else:
				for datum in data:
					print("DEBUG - " + prefix.upper() + ": " + str(datum))

	# COMMAND FUNCTIONS

	def doPasv(self):
		""" Changes the dataport connection mode to from active to passive."""
		if not self.isAuth:
			return "530 User is not logged in."

		try:
			self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.serversock.bind((self.ADDR[0], 0))
			self.serversock.listen(1)

			self.isPassive = True

			addr, port = self.serversock.getsockname()

			hi = port >> 8
			lo = port & 255

			self.serverAddr = addr
			self.serverPort = port

			return "227 Enter Passive Mode (" + ",".join(addr.split(".")) + "," + str(hi) + "," + str(lo) + ")"
		except socket.error:
			return "500 Unable to enter passive mode"

	def doPwd(self, params):
		""" Prints the working directory of the given input. If no input is given than
		assumes current working directory """

		if len(params) == 1:
			return "257 " + self.cwd
		elif len(params) == 2:
			new_dir = params[1]

			if new_dir == ".":
				cwd = self.cwd + '/'
			else:
				cwd = self.cwd + '/' + new_dir

			return "257 " + cwd
		else:
			return "501 invalid p arameters"

	def doCdup(self):
		"""if current working directory is same as base dir then do nothing. But if not
		then step up one directory"""

		if not self.isAuth:
			return "530 User is not logged in."
		if not self.cwd == self.homewd or self.cwd in self.homewd:
			cwd = self.cwd
			cwd = cwd[:cwd.rfind("/")]

			# If CWD is subset of home
			if cwd not in self.homewd:
				self.cwd = cwd
				return "200 Move UP in directory"
			else:
				return "551 directory is already at home. "
		else:
			return "551 Directory is already at home."

	def doCwd(self, params):
		""" Returns the current working directory"""
		if not self.isAuth:
			return "530 User is not logged in."

		if len(params) == 2:
			new_dir = params[1]

			if new_dir == "/":
				self.cwd = self.homewd
			else:
				self.cwd = self.cwd + "/" + new_dir

			self.debug("CWD", self.cwd)

			return "250 Updated current working directory"
		else:
			return "501 Argument needed for CWD"

	def doUser(self, user):
		""" Does validation on the user name and saves
			it to client variable user for later use. """

		if len(user) < self.MAX_USER_LEN:
			self.user = user
			return "331 Please enter your password"
		else:
			return "501 Username is too long"

	def doPass(self, passw, database):
		""" Takes the giving password and compares it to creds in the database. If login is
		successful than set isAuth to true. """
		if self.user == "":
			return "530 Must use USER first"
		else:
			print("doPass")

			creds = self.user + " " + passw

			if creds in database:
				self.isAuth = True
				return "230 You have logged in!"
			else:
				return "530 Not Logged in"

	def doSyst(self):
		""" Returns information of the operating system. """
		return "215 UNIX 8.0"

	def doHelp(self):
		return "214 List of Commands: USER, PASS, CWD, CDUP, QUIT, PASV, EPSV, PORT, EPRT, RETR, STOR, PWD, SYST, LIST, HELP"

	def doStor(self, params):
		if not self.isAuth:
			return "530 User is not logged in."

		if len(params) == 2:
			new_dir = params[1]

			if new_dir == ".":
				path = self.cwd
			else:
				path = self.cwd + "/" + new_dir

			try:
				store_file = open(path, "w")

				while 1:
					data = self.datasock.recv(1024)
					if not data:
						self.debug("stor", "No more data")
						break
					else:
						store_file.write(data)

				store_file.close()

				self.closeDatasock()

				return "226 Completed data transfer successfully"
			except IOError:
				return "500 Unable to create path"
			except socket.error:
				return "500 Unable to read from socket"
			except:
				return "500 Unknown error"

			self.debug("CWD", self.cwd)

	def doList(self, directory):
		""" Triggers the ls unix command in the current working directory. The ls command
		is implemented in the python package os. """

		# TODO
		# Check is var is directory

		if not self.isAuth:
			return "530 User is not logged in."

		if directory != "":
			dirs = os.listdir(directory)
		else:
			self.debug("dirs - cwd", self.cwd)
			dirs = os.listdir(self.cwd)

		self.debug("list directories", dirs)

		# TODO get full dir

		# Sending directory
		# try:
		for direct in dirs:
			mess = self.cwd + "/" + direct + "\r\n"
			self.datasock.send(mess)

		self.log("Sent: LIST of directories in " + self.cwd + directory + "\n")

		self.closeDatasock()

		return "226 Directories sent."

	# except socket.error:
	# return "425 Couldn't open data connection"

	def doPort(self, param):
		"""Takes the the input string (h1,h2,h3,h4,p1,p2). Validate that the input is formatted correctly.
		Validate that the input has right number of inputs. Validate that the values are within the correct ranges """

		if not self.isAuth:
			return "530 User is not logged in."

		# TODO Check if value are integers

		params = param.split(",")
		addr = ""

		if len(params) == 6:
			for arg in params[:4]:
				# Validate Address
				self.debug("PORT - PARAM", arg)
				if int(arg) < 0 or int(arg) > 255:
					return "501 Address is invalid"
				else:
					addr += str(arg) + "."

			addr = addr[:-1]

			p1 = int(params[4])
			p2 = int(params[5])

			# TODO Check if this is a valid port

			dataport = (p1 * 256) + p2

			self.debug("port - address", addr)
			self.debug("port - dataport", dataport)

			self.dataAddr = addr
			self.dataPort = dataport

			self.createDatasock(dataport, addr=addr)

			# return self.createDatasock(dataport, addr=addr)
			return "200 Port Command."
		else:
			return "501 Invalid arguement"

	def doQuit(self):
		return "221 Goodbye!"


class FTPServer:

	def __init__(self, debug=False, port=2121, sock=None, log="", config={}):
		self.DEBUG = debug
		self.PORT = port
		self.SOCK = sock
		self.LOG = log
		self.DATABASE = []

		self.CONFIG = config
		self.PORT_MODE = False
		self.PASV_MODE = True

		self.MAXCONNECT = 10

		if self.CONFIG:  # Config exists
			#  Always assumes default when not specified

			if 'port_mode' in self.CONFIG.keys():
				self.PORT_MODE = self.CONFIG['port_mode']
				print('PORT MODE: {}', self.PORT_MODE)
			if 'port_mode' in self.CONFIG.keys():
				self.PASV_MODE = self.CONFIG['pasv_mode']
				print('PASV MODE: {}', self.PASV_MODE)

			if self.PORT_MODE is False and self.PASV_MODE is False:
				print("Invalid Server Configuration: Mode can be PORT and/or PASV but can't be either.")
				exit(1)


def createConnection(self, host, port):
	"""This function is used to create a socket connection to machine that just connected to the port.
	It also binds the server to public host on start up."""

	try:
		# create an INET, STREAMing socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		if (host == 'public'):
			sock.bind((socket.gethostname(), port))
			print("Starting FTP Server at port: " + str(self.PORT))
		else:
			sock.connect((host, port))
			print("Connected to " + host + " at " + str(port))

		self.SOCK = sock
	except KeyboardInterrupt:
		self.closeConnection()
	except socket.error:
		print("Port " + str(self.PORT) + " already in use.")
		self.createConnection(host, self.randomPort())


def closeConnection(self):
	print("Connection terminated. Closing FTPClient...")
	self.SOCK.close()


def log(self, logMessage):
	ts = time.time()

	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S.%f')

	f = open(self.LOG, "a+")

	f.write(timestamp + " " + logMessage + "\n")

	if self.DEBUG:
		print("DEBUG-LOG:" + timestamp + " " + logMessage)


def randomPort(self):
	new_port = random.randint(1024, 10000)
	self.PORT = new_port

	if self.DEBUG:
		print("DEBUG - RANDOMPORT: " + str(self.PORT))
	return new_port


def loadUsers(self):
	with open('superSecretPasswords') as f:
		self.DATABASE = f.read().splitlines()


def sendMessage(self, message):
	"""Sends message to server connect to socket. """
	self.SOCK.send(message + "\r\n")

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


def handleConnection(self, client):
	client.sendMess("220 Welcome to Chad's FTP Server!")

	# Until resp is QUIT
	while True:
		mess = client.recvMess()

		# check null
		if len(mess) > 0:
			print("Received: " + mess)

			resp = client.parseCommand(mess, self.DATABASE)
			client.sendMess(resp)

		# Quit
		if resp[:3] == "221":
			print("Closing connection.")
			break

		if self.DEBUG:
			print("DEBUG SERVER-REPLY:" + resp)
			print("DEBUG SERVER-CODE:" + resp[:3])


def mainLoop(self):
	"""This is the main control loop of the protocol. Since FTP is a 'server speaks first' system
   our loop will start by waiting for a reply from the server. """

	# Open port for listening on public host
	self.createConnection('public', self.PORT)

	# Load in our database of users and passwords
	self.loadUsers()

	self.SOCK.listen(self.MAXCONNECT)

	while True:
		try:
			# accept connections from outside
			(clientsocket, address) = self.SOCK.accept()

			client = Client(clientsocket, address, self.LOG, self.DEBUG)
			self.handleConnection(client)
			clientsocket.close()
		except KeyboardInterrupt:
			exit(1)


def main():
	print("Hostname: " + socket.gethostname())

	if len(sys.argv) < 2:
		print(
			"No/not enough arguements given. Usage: python FTPServer.py <logfile> <port> [-d|--debug] [-c|--config <file> ]")

	if len(sys.argv) >= 3 and not sys.argv[1].isdigit() and sys.argv[2].isdigit():

		logfile = sys.argv[1]
		port = sys.argv[2]

		print("Logging interactions in " + logfile)

		# Checking for optional parameters
		# Two optional --debug or --config
		# 1. Check for '--'
		# 2. Check type

		# Start of optional is always 3
		ind = 3
		debug = False
		config_dict = {}
		while (len(sys.argv) - ind > 0):
			if (sys.argv[ind][0] is '-'):
				if (sys.argv[ind].lower() is '-d' or '--debug'):
					debug = True
				elif (sys.argv[ind].lower() is '-c' or '--config'):
					try:
						config_file = sys.argv[ind + 1]
			# Make sure this isn't next argument
			if config_file[0] is '-':
				print("No configuration file given.")
			else:
				# Load configuration file
				conf = Config()
				config_dict = conf.load(config_file)
			except IndexError:
			print("No configuration file given.")
		else:
			print("{} is not a valid optional argument. ".format(sys.argv[ind]))
		else:
		print("Invalid optional argument given.")


ind += 1

ftp = FTPServer(log=str(sys.argv[1]), port=int(sys.argv[2]), debug=debug, config=config_dict)

ftp.mainLoop()

elif sys.argv[1].isdigit():
print("Invalid log file provided. Must be name of log file.")
elif not sys.argv[2].isdigit():
print("Invalid port provided. Input is not an integer.")

if len(sys.argv) > 3:
	print("Too many arguments.")
exit(1)

# now connect to the web server on port 9223, which we've made our server listen to
# change the hostname if not on the same server


if __name__ == "__main__":
	main()
