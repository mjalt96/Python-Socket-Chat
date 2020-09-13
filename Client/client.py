#!/usr/bin/python3

import socket
import select 
import errno 
import random
import sys

# GLOBAL VARIABLES
HEADER_LENGTH = 64
ADDR_LIST = socket.gethostbyname_ex(socket.gethostname())[2]
HOST = ADDR_LIST[len(ADDR_LIST)-1] #last address from list
PORT = 5051
ADDR = (HOST,PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

#request username beforehand
my_username = input("Please insert a username: ")

#identification
users = my_username # change to read from file
if my_username not in users:
	uid = my_username + str(random.randint(100000,999999))
else:
	uid = "834423" #read from file

#create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)
client_socket.setblocking(False) #set recv method to not block

#send the username and user id on the header before the actual communication
client_id = f'{my_username} {uid}'
initial_data = client_id.encode(FORMAT)
username_header = f'{len(initial_data):<{HEADER_LENGTH}}'.encode(FORMAT)
client_socket.send(username_header + initial_data)


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