import socket 

HEADER = 64
PORT = 5051
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
IP = "192.168.1.80"

#create socket and connect
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP,PORT))

def send(msg):
	message = msg.encode(FORMAT)
	msg_length = len(message)
	send_length = str(msg_length).encode(FORMAT)

	#pad the message to the header length with byte 'space'
	send_length += b' ' * (HEADER - len(send_length))

	client.send(send_length)
	client.send(message)

send("Hello World")