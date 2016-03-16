import io
import socket
import sys
import string
import ast

target_server_address = 'b132.seng.uvic.ca'
target_server_port = 44420


def make_request(data):

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (target_server_address, target_server_port)
	
	sock.connect(server_address)
	sock.sendall(str(data))
	response = sock.recv(1024)
	response = ast.literal_eval(response)
	if __debug__:
		print "Transaction number: " + data['transactionNum'] + "\n"
		print "Req: " + data['user'] + "," + data['stock_id'] + " - " + data['command'] + "\n"
		print "Recv: " + response['user'] + "," + response['stock_id'] + " - " + response['price'] + " [" + response['timestamp'] + "]\n\n"
	sock.close()

	return

def main():

	bad_chars = '[]'

	f = open("activeWorkLoad.txt", 'r')
	for line in f:

		tokens = line.split(' ')

		transaction_id = tokens[0]
		transaction_id = transaction_id.translate(None, bad_chars)

		request = tokens[1].split(',')

		request_type = request[0].upper()

		if request_type == 'QUOTE' or request_type == 'BUY' or request_type == 'SELL':
			request_d = {
				'user' : request[1],
				'stock_id' : request[2],
				'transactionNum' : transaction_id,
				'command' : request_type
			}
			make_request(request_d)

		else:
			# INVALID REQUEST
			#print "invalid request: " + request[0]
			pass


if __name__ == "__main__":
    main()
