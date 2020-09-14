#!/usr/bin/python3

import errno
import os
import random
import select
import socket
import sys
from datetime import datetime
from pathlib import Path

# GLOBAL VARIABLES
HEADER_LENGTH = 64
ADDR_LIST = socket.gethostbyname_ex(socket.gethostname())[2]
HOST = ADDR_LIST[len(ADDR_LIST)-1] #last address from list
PORT = 5051
ADDR = (HOST,PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
PATH = '\\AppData\\Local\\Temp'
UID = ''


def calculate_last_login(current_datetime, last_datetime):
	"""
	Function that calculates the last user login given two datetime
	"""
	if current_datetime.year != last_datetime.year:
		#year difference
		diff = abs(current_datetime.month - last_datetime.month)
		if diff >= 11:
			last_login = str(abs(current_datetime.year - last_datetime.year)) + " year(s) ago."
		else:
			last_login = str(abs(current_datetime.year - last_datetime.year)) + " years and " + diff + " month(s) ago." 
	else:
		#same year
		if current_datetime.month != last_datetime.month:
			#month difference
			day_diff = abs(current_datetime.day - last_datetime.day)
			if diff > 25:
				last_login = str(abs(current_datetime.month - last_datetime.month)) + " month(s) ago."
			else:
				last_login = day_diff + " day(s) ago."
		else:
			#same month
			day_diff = abs(current_datetime.day - last_datetime.day)
			if day_diff == 0:
				last_login = " today."
			else:
				last_login = str(day_diff) + " day(s) ago."
	return last_login


def check_user_file():
	"""
	Function that checks the existence of a local file for the user
	"""
	global UID
	try:
		usr_file = Path(str(Path.home()) + PATH + '\\python_chatroom.txt')
		if os.path.exists(usr_file):
			#user exists, read file
			f = open(usr_file, "r")
			lines = f.readlines()
			f.close()

			UID = lines[0].strip('\n')
			previous_username = lines[1]
			aux = ' '.join(lines[2].split()[2:])
			dt = datetime.strptime(aux, '%Y-%m-%d %H:%M:%S')
			dt_today = datetime.now()

			#get last login
			last_login = calculate_last_login(dt_today, dt)
					
			print('Welcome back!\nYour previous username: ', previous_username)
			print("Your last login was: {}\n\n".format(last_login))
		else:
			#user does not exist, create file with user info
			f = open(usr_file, "w")
			UID = str(random.randint(1000000,9999999))
			f.write(f'{UID}\n{my_username}\nCreation date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
			f.close()
			return 0

	except FileExistsError as e:
			print(e)
	except OSError as e:
		print(e)
	except Exception as e:
		print(e)


def handle_session():
	"""
	Handle the chat session for the client
	"""
	while True:
		#read user input
		message = input(f'{my_username} > ')

		if message:
			message = message.encode(FORMAT)
			message_header = f'{len(message):<{HEADER_LENGTH}}'.encode(FORMAT)
			client_socket.send(message_header + message)

		try:
			while True:
				#receive communication
				username_header = client_socket.recv(HEADER_LENGTH)

				if not len(username_header):
					print("Connection closed by the server.")
					sys.exit()

				#get username from received message
				username_length = int(username_header.decode(FORMAT).strip())
				username = client_socket.recv(username_length).decode(FORMAT)
				aux = username.split(" ")
				username = ' '.join(aux[:len(aux)-1])
				
				#get the rest of the message
				message_header = client_socket.recv(HEADER_LENGTH)
				message_length = int(message_header.decode(FORMAT).strip())
				message = client_socket.recv(message_length).decode(FORMAT)

				print(f'{username} > {message}')

		except IOError as e:
			#ignore common irrelevant errors
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print('Error: {}'.format(str(e)))
				sys.exit()

			continue

		except KeyboardInterrupt:
			print("Connection closed by Keyboard.")

		except Exception as e:
			print('General error: {}'.format(str(e)))
			sys.exit()


if __name__ == "__main__":
	#request username beforehand
	my_username = input("Please insert a username: ")

	#identification
	check_user_file()

	#create socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(ADDR)
	client_socket.setblocking(False) #set recv method to not block

	#send the username and user id on the header before the actual communication
	client_id = f'{my_username} {UID}'
	initial_data = client_id.encode(FORMAT)
	username_header = f'{len(initial_data):<{HEADER_LENGTH}}'.encode(FORMAT)
	client_socket.send(username_header + initial_data)

	#start session
	handle_session()