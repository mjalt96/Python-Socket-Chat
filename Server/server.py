import socket 
import select #grants OS operations with interoperability between operating systems
import random
from threading import Thread

###SERVER CONFIGURATION###
HEADER_LENGTH = 64
HOST = '192.168.1.80'
PORT = 5051
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

clients = {}
messages = {}
user_messages = []

class Message:

	location_folder = "./userdata/messages/"

	def __init__(self, uid, datestamp, date, message):
		self.uid = uid
		self.location = f'{self.location_folder}/{uid}/{date}.txt'
		self.messages = {datestamp:message} #dictionary
	
	def add_message(self, datestamp, message):
		self.messages.update({datestamp,message})
	
	def save_messages(self, messages):
		try:
			f = open(self.location, "a")
			for dtstamp, msg in self.messages.items():
				f.write(f'\n\n#{dtstamp}\n{msg}')
		except OSError as e:
			print(e)
		except Exception as e:
			print(e)
		else:
			f.close()


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

			print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode(FORMAT)))

		else:
			message = receive_message(notified_socket)

			if message is False:
				print(f"Closed connection from {clients[notified_socket]['data'].decode(FORMAT)}")	
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			#handle message data
			user = clients[notified_socket]
			msg = message['data'].decode(FORMAT)
			username = user['data'].decode(FORMAT)
			#TO DO: VERIFY IF UID EXISTS
			uid = username + str(random.randint(100000,999999))
			user_messages.append(msg)
			messages[uid] = user_messages.copy()

			print(f"Received message from {username}: {msg}")

			for client_socket in clients:
				if client_socket != notified_socket:
					client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]				
