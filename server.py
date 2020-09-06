import socket 
import select #grants OS operations with interoperability between operating systems

###configure here 
HEADER_LENGTH = 64
HOST = '192.168.1.80'
PORT = 5051
FORMAT = 'utf-8'

#set the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #stream socket of Internet domain
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow to reconnect

server_socket.bind((HOST, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

print(f'Listening for connections on {HOST}:{PORT}...')

#handle received message
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
		#new connection
		if notified_socket == server_socket:
			client_socket, client_address = server_socket.accept()

			user = receive_message(client_socket)
			if user is False: #disconnected user
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

			user = clients[notified_socket]
			print(f"Received message from {user['data'].decode(FORMAT)}: {message['data'].decode(FORMAT)}")

			for client_socket in clients:
				if client_socket != notified_socket:
					client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]				