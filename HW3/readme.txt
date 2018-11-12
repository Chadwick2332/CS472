This file includes the main FTPServer class aswell as
a Client class which is inniated when a client connects 
to the server.

Use the following convention for starting the server:
      python ftpServer.py LOG PORT [debug]

  LOG: log file for recording
  PORT: the port number that you would like to open
       (if is in use another will be selected at random)
  DEBUG: Prints the debug messeage for the developer

  Example:
      python ftpServer.py log.txt 4813 true 


Authentication is done by parsing a text file with the convention
{username} {password}. This file is aptly titled superSecretPasswords.
You may add your own username and password to this file or use example user.
  Ex.
      USER: cjd329
      PASS: 12345

Several commands have no been implement correctly. The command LIST and STOR
do not return there output on the client side.

The commands ESPV and RETR hav not been implemented
