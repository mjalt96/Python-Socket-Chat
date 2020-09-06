import socket
import select 
import errno 
import sys

###configure here along the server
HEADER_LENGTH = 64
PORT = 5051
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
HOST = "192.168.1.80"

my_username = input("Please insert a username: ")

#create socket and connect
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))
client_socket.setblocking(False) #set recv method to not block

#set username and send it on the header
username = my_username.encode(FORMAT)
username_header = f'{len(username):<{HEADER_LENGTH}}'.encode(FORMAT)
client_socket.send(username_header + username)

while True:
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

			username_length = int(username_header.decode(FORMAT).strip())
			username = client_socket.recv(username_length).decode(FORMAT)

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

	#any other exception
	except Exception as e:
		print('General error: {}'.format(str(e)))
		sys.exit()

# def send(msg):
# 	message = msg.encode(FORMAT)
# 	msg_length = len(message)
# 	send_length = str(msg_length).encode(FORMAT)

# 	#pad the message to the header length with byte 'space'
# 	send_length += b' ' * (HEADER - len(send_length))

# 	client_socket.send(send_length)
# 	client_socket.send(message)

#send(input("Message: "))