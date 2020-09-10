import socket 
import select #grants OS interoperability for the sockets
import random
import os
import re
from glob import glob
from pathlib import Path
from datetime import datetime
from threading import Thread

###SERVER CONFIGURATION###
HEADER_LENGTH = 64
HOST = '192.168.1.80'
PORT = 5051
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

clients = {}
messages = []
users = []


class Message:

	location_dir =  f'{os.getcwd()}\\userdata\\messages\\'
	messages_dict = {}


	def __init__(self, uid="", datestamp="", date="", message=""):
		self.uid = uid
		self.location = f'{self.location_dir}{uid}'
		self.date = date
		if message != "":
			self.messages_dict[datestamp] = message
	
	#private method to check if user file exists
	#returns true or false
	def __search_user_file(self, username):
		file_list = [file for file in glob(self.location + "*", recursive=False)]
		for f in file_list:
			res = [re.findall(r'(\w+?)(\d+)', f)[0]]
			if res:
				self.uid = str(res[0][0]) + str(res[0][1])
				return 1
			else:
				return -1


	#saves messages locally
	def save_messages(self):
		try:
			path = self.location
			directory = Path(path)
			directory.mkdir(exist_ok=True)
			f = open(f'{self.location}\\{self.date}', "a")
			for dtstamp, msg in self.messages_dict.items():
				f.write(f'\n\n#{dtstamp}\n{msg}')
		except FileExistsError as e:
			print(e)
		except OSError as e:
			print(e)
		except Exception as e:
			print(e)
		else:
			f.close()

	#obtains messages from a corresponding file
	def get_messages(self, username):
		if self.__search_user_file(username) == 1:
			file_list = [file for file in glob(self.location + "*", recursive=False)]
			for f in file_list:
				s = open(f, "r")
				print(s)
				s.close()


	#Special methods
	#def __del__(self): #use if save on deletion
		#self.save_messages()

	#TO-DO: CREATE A METHOD FOR CLOUD BACKUP ON AWS


class User(Message):
	
	def __init__(self, uid=0, username=""):
		Message.__init__(self)
		self.uid = uid
		self.username = username
		self.get_messages(username)


#set the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #stream socket of Internet domain
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow to reconnect

server_socket.bind(ADDR)
server_socket.listen()

sockets_list = [server_socket]

print(f'Listening for connections on {HOST}:{PORT}...')


"""Function that handles received messages"""
def receive_message(client_socket):
	try:
		message_header = client_socket.recv(HEADER_LENGTH)

		if not len(message_header):
			return False

		message_length = int(message_header.decode(FORMAT).strip())
		return {"header": message_header, "data": client_socket.recv(message_length)}
	except:
		return False


#establish communication
while True:
	#blocking call
	read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

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
			#TO DO: Use classes to handle users and create cookies stored on the client side
			username = user['data'].decode(FORMAT)
			user_obj = User()
			if username not in users:
				if user_obj.uid == 0:
					uid = username + str(random.randint(100000,999999))
					users.append({uid, username})
				else:
					uid = user_obj.uid
					users.append({uid, username})
				

			print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode(FORMAT)))

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
			msg = message['data'].decode(FORMAT)
			msg_obj = Message(uid,dt,date,message)
			msg_obj.save_messages()

			print(f"Received message from {username}: {msg}")

			for client_socket in clients:
				if client_socket != notified_socket:
					client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]

	#TO-DO: USE THREADS INSTEAD TO SAVE FROM TIME TO TIME