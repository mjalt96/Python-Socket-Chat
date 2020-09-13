#!/usr/bin/python3

import socket 
import select #grants OS interoperability for the sockets
import random
import os
import re
from glob import glob
from pathlib import Path
from datetime import datetime
from threading import Thread

# GLOBAL VARIABLES
HEADER_LENGTH = 64
MAX_CONNECTIONS = 20
ADDR_LIST = socket.gethostbyname_ex(socket.gethostname())[2] #avoid getting wrong host
HOST = ADDR_LIST[len(ADDR_LIST)-1] #last address from list
PORT = 5051
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

clients = {}
messages = []
users = []


class Message:
	"""
	Class that represents a user message
	"""
	dir =  f'{os.getcwd()}\\messages\\'

	def __init__(self, uid="", datestamp="", date="", message=""):
		self.uid = uid
		self.path = f'{self.dir}{date}'
		self.date = date
		if message != "":
			self.message = message
			self.datestamp = datestamp
			self.__save_messages()


	def __save_messages(self):
		"""
		Private method that saves messages locally
		"""
		try:
			directory = Path(self.path)
			directory.mkdir(mode = 0o664, exist_ok=True)
			num_files = len([name for name in os.listdir(directory) 
			if os.path.isfile(name)])

			f = open(f'{self.path}\\{num_files + 1}.txt', "a+")
			f.write(f'\n\n#{self.datestamp}\n{self.uid}\n{self.message}')

		except FileExistsError as e:
			print(e)
		except OSError as e:
			print(e)
		except Exception as e:
			print(e)
		else:
			f.close()

	#TO-DO: CREATE A METHOD FOR CLOUD BACKUP ON AWS


class User(Message):
	"""
	Class that represents a user
	"""
	def __init__(self, uid=0, username=""):
		Message.__init__(self)
		self.uid = uid
		self.username = username


def check_directories():
	"""
	Function that checks for needed directories and files creating if needed
	"""
	#check if "messages" directory exists
	msg_dir = Path(f'{os.getcwd()}\\messages')
	if os.path.exists(msg_dir) == False:
		try:
			msg_dir.mkdir(mode = 0o664, exist_ok=True)	
		except FileExistsError as e:
			print(e)
		except OSError as e:
			print(e)
		except Exception as e:
			print(e)


def receive_message(client_socket):
	"""
	Function that handles received messages from a particular socket
	"""
	try:
		message_header = client_socket.recv(HEADER_LENGTH)

		if not len(message_header):
			return False

		message_length = int(message_header.decode(FORMAT).strip())

		return {"header": message_header, 
		"data": client_socket.recv(message_length)}
	except:
		return False


def handle_communication(server_socket, sockets_list):
	"""
	Function that handles the communication between server and clients
	"""
	#blocking call
	read_sockets, _, exception_sockets = select.select(sockets_list, [], 
	sockets_list)

	#handle users
	for notified_socket in read_sockets:

		if notified_socket == server_socket:
			#creates new socket for the client
			client_socket, client_address = server_socket.accept()

			user = receive_message(client_socket)
			if user is False:
				#disconnected user
				continue
			
			sockets_list.append(client_socket)
			clients[client_socket] = user

			#handle user
			initial_data = user['data'].decode(FORMAT)
			uid = (initial_data.split(" "))[-1]
			aux = initial_data.split(" ")
			username = ' '.join(aux[:len(aux)-1])
			user_obj = User()
			user_obj.uid = uid
			user_obj.username = username
			for u in users:
				if u.uid == user_obj.uid:
					user_obj.uid == u.uid
			users.append(user_obj)					

			print('Accepted new connection from {}:{}, username: {}'.format(
				*client_address, username))

		else:
			message = receive_message(notified_socket)

			if message is False:
				print(f"Closed connection from {clients[notified_socket]['data'].decode(FORMAT)}")	
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue
			else:
				dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				date = datetime.now().strftime('%Y_%m_%d')

			#handle message data
			user = clients[notified_socket]
			uid = (user['data'].decode(FORMAT).split(" "))[-1]
			msg = message['data'].decode(FORMAT)
			msg_obj = Message(uid,dt,date,msg)
			aux = user['data'].decode(FORMAT).split(" ")
			username = ' '.join(aux[:len(aux)-1])

			print(f"Received message from {username}: {msg}")

			for client_socket in clients:
				if client_socket != notified_socket:
					client_socket.send(user['header'] + 
					user['data'] + message['header'] + message['data'])

	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]

	#TO-DO: USE THREADS INSTEAD TO SAVE FROM TIME TO TIME


if __name__ == "__main__":
	check_directories()

	#set the server socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #stream socket of Internet domain
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow to reconnect
	server_socket.bind(ADDR)

	#start listening for connections
	server_socket.listen(MAX_CONNECTIONS)
	print(f'Listening for connections on {HOST}:{PORT}...')

	sockets_list = [server_socket]

	while True:
		#handle communications
		handle_communication(server_socket, sockets_list)