#!/usr/bin/python3


# Homework 4
# This part of the assignment is to modify your server to implement reading in a config.conf file
# when you initialize the server. The config.conf file should be in a relative location (it should
# get it out of the current directory at a fixed name (for example ftpserverd.conf). This
# config.conf file should be of a few (“attribute” = “value” pairs). It should ignore any lines
# which begin with a pound sign (“#”).
# You should modify your server to restrict PORT (and EPRT) and PASV (and EPSV) by the
# config.conf file.
#  # port_mode supported (default = no)
#  port_mode = NO
#  # pasv_mode supported (default = yes)
#  pasv_mode = YES
# It is possible to set both of these attributes to YES. If both are set to NO, then it is a fatal error
# and the server should print an error message and exit. You should test via a client using both
# modes and ensure that the correct error messages are returned.


class config:

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

		#Remove return
		line = line[:-1]
		tokens = [value.strip() for value in line.split('=')]
		#if tokenized_line as a length less than 2
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




config_file = "config.conf"
conf = config()
conf.load(config_file)
