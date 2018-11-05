#!/usr/bin/python3

# CS 472 - Homework #3
# Chad Dotson-Jones
# ftpClient.py


# ----------------------------------------------------
# |                     FTPServer     		     |
# ----------------------------------------------------
# Client takes in an address and port and connects to 
# any FTP server. 
# 
# Command-line input will let you send command to the
# commands to the server.
#
import random
import time
import datetime
import socket
import struct
import sys

MAX_USER_LEN = 50

class Client:

    def __init__(self, socket, address, logfile, debug):
        self.SOCKET = socket
        self.ADDR   = address
        self.LOG    = logfile
        self.DEBUG  = debug

        self.user = ""
        self.isAuth = False

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

        if len(mess_list) >= 2:
            if command == "USER":
                return self.doUser(mess_list[1])
            elif command == "PASS":
                return ""
            elif command == "CWD":
                return""
            elif command == "CDUP":
                return""
            elif command == "PASV":
                return""
            elif command == "EPSV":
                return""
            elif command == "PORT":
                return""
            elif command == "RETR":
                return""
            elif command == "STOR":
                return""
            elif command == "PWD":
                return""
            elif command == "SYST":
                return""
            elif command == "LIST":
                return""
            elif command == "HELP":
                return""
            elif command == "QUIT":
                return""


    def log(self, logMessage):
        print("log")
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S.%f')

        f = open(self.LOG, "a+")
        f.write(timestamp + " " + logMessage)

        if self.DEBUG:
            print("DEBUG-LOG:" + timestamp + " " + logMessage)

    # COMMAND FUNCTIONS

    def doUser(self, user):
        if len(user) < MAX_USER_LENGTH:
            return "331 Please enter your password"
        else:
            self.user = user
            return "501 Username is too long"

    def doPass(self, passw, database):
        if self.user == "":
            return ""
        else:
            creds = self.user + " " + passw

            if creds in database:
                self.isAuth = True
                return "230 You have logged in!"
            else:
                return "530 Not Logged in"



class FTPServer:

    def __init__(self, debug=False, port=2121, sock=None, log="" ):
        self.DEBUG    = debug
        self.PORT     = port
        self.SOCK     = sock
        self.LOG      = log
        self.DATABASE = []

        self.MAXCONNECT = 10

    def createConnection(self, host, port):
        """This function is used to create a socket connection to machine that just connected to the port.
        It also binds the server to public host on start up."""


        try:
            # create an INET, STREAMing socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if(host == 'public'):
                sock.bind((socket.gethostname(), port))
                print("Starting FTP Server at port: " + str(self.PORT))
            else:
                sock.connect((host, port))
                print("Connected to " + host + " at " + str(port))

            self.SOCK = sock
        except KeyboardInterrupt:
            self.closeConnection()
        except socket.error:
            print("Port "+ str(self.PORT) +" already in use.")
            self.createConnection(host, self.randomPort())

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
 
    def handleConnection(self, client) :

        client.sendMess("220 Welcome to Chad's FTP Server!")

        while True:
            mess = client.recvMess()
            print("Received: " + mess)

            resp = client.parseCommand(mess, self.DATABASE)
            client.sendMess(resp)

            if self.DEBUG:
                print("DEBUG SERVER-REPLY:" + resp)

    def mainLoop(self):
        """This is the main control loop of the protocol. Since FTP is a 'server speaks first' system
       our loop will start by waiting for a reply from the server. """

        # Open port for listening on public host
        self.createConnection('public', self.PORT)

        # Load in our database of users and passwords
        self.loadUsers()

        self.SOCK.listen(self.MAXCONNECT)


        while True:
                # accept connections from outside
                (clientsocket, address) = self.SOCK.accept()

                client = Client(clientsocket, address, self.LOG, self.DEBUG)
                self.handleConnection(client)
                clientsocket.close()



def main():

    print("Hostname: " + socket.gethostname())


    if len(sys.argv) < 2 :
        print("No/not enough arguements given. Usage: python FTPServer.py <logfile> <port>")

    if len(sys.argv) >= 3 and not sys.argv[1].isdigit() and sys.argv[2].isdigit():

        logfile = sys.argv[1]
        port = sys.argv[2]

        print("Logging interactions in " + logfile)

        if len(sys.argv) == 4 and sys.argv[3].lower() == "true": #DEBUG is enabled
            # FTP Client
            print("--- DEBUG MODE ENABLED ---")
            ftp = FTPServer(log=str(sys.argv[1]), port=int(sys.argv[2]), debug=True)
        else:
            #FTP Server without debug
            ftp = FTPServer(log=str(sys.argv[1]), port=int(sys.argv[2]))

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
