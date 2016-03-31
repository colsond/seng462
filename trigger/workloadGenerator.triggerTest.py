import io
import socket
import sys
import string
import ast

target_server_address = 'b146.seng.uvic.ca'
target_server_addressA = 'b140.seng.uvic.ca'
target_server_addressB = 'b141.seng.uvic.ca'
target_server_addressC = 'b142.seng.uvic.ca'
target_server_addressD = 'b143.seng.uvic.ca'
target_server_addressE = 'b144.seng.uvic.ca'
target_server_addressF = 'b145.seng.uvic.ca'
target_server_port = 44421


def make_request(data):

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	#if data.get('stock_id') < "D":
	#	server_address = (target_server_addressA, target_server_port)
	#elif data.get('stock_id') < "H":
	#	server_address = (target_server_addressB, target_server_port)
	#elif data.get('stock_id') < "M":
	#	server_address = (target_server_addressC, target_server_port)
	#elif data.get('stock_id') < "Q":
	#	server_address = (target_server_addressD, target_server_port)
	#elif data.get('stock_id') < "U":
	#	server_address = (target_server_addressE, target_server_port)
	#else:
	#	server_address = (target_server_addressF, target_server_port)
	server_address = (target_server_address, target_server_port)
	
	sock.connect(server_address)
	sock.sendall(str(data))
#	response = sock.recv(1024)
#	response = ast.literal_eval(response)
#	if __debug__:
#		print "Transaction number: " + data['transactionNum'] + "\n"
#		print "Req: " + data['user'] + "," + data['stock_id'] + " - " + data['command'] + "\n"
#		print "Recv: " + response['user'] + "," + response['stock_id'] + " - " + response['price'] + " [" + response['timestamp'] + "]\n\n"
	sock.close()

	return

def main():

	bad_chars = '[]'

	f = open("activeWorkLoad.txt", 'r')
	for line in f:

		line = line.rstrip()

		tokens = line.split(' ')

		transaction_id = tokens[0]
		transaction_id = transaction_id.translate(None, bad_chars)

		print transaction_id

		request = tokens[1].split(',')

		request_type = request[0].upper()

		#print str(transaction_id) + ' ' + str(request_type)

		if request_type == 'SET_BUY_TRIGGER':
			if request[1].isalnum():
				if len(request[1]) <= 10:
					if request[2].isalnum():
						if len(request[2]) <= 3:
							try:
								trigger = float(request[3])
							except:
								if __debug__:
									print 'request[3] is not floatable, see: ' + str(request[3])
							else:
								if trigger > 0:
									request_d = {
										'user' : request[1],
										'stock_id' : request[2],
										'trigger' : trigger,
										'transactionNum' : transaction_id,
										'command' : 'BUY',
										'amount' : 100.00		#arbitrary - would have been set with previous command
									}
									make_request(request_d)

								else:
									if __debug__:
										print 'request[3] is not > 0, see: ' + str(request[3])
						else:
							if __debug__:
								print 'request[2] is not len <= 3, see: ' + str(len(request[2])) + ' ' + str(request[2])
					else:
						if __debug__:
							print 'request[2] is not alnum, see: ' + str(request[2])
				else:
					if __debug__:
						print 'request[1] is not len <= 10, see: ' + str(len(request[1])) + ' ' + str(request[1])
			else:
				if __debug__:
					print 'request[1] is not alnum, see: ' + str(request[1])
			
		elif request_type == 'SET_SELL_TRIGGER':
			if request[1].isalnum():
				if len(request[1]) <= 10:
					if request[2].isalnum():
						if len(request[2]) <= 3:
							try:
								trigger = float(request[3])
							except:
								if __debug__:
									print 'request[3] is not floatable, see: ' + str(request[3])
							else:
								if trigger > 0:
									request_d = {
										'user' : request[1],
										'stock_id' : request[2],
										'trigger' : trigger,
										'transactionNum' : transaction_id,
										'command' : 'SELL',
										'amount' : 100.00		#arbitrary - would have been set with previous command
									}
									make_request(request_d)

								else:
									if __debug__:
										print 'request[3] is not > 0, see: ' + str(request[3])
						else:
							if __debug__:
								print 'request[2] is not len <= 3, see: ' + str(len(request[2])) + ' ' + str(request[2])
					else:
						if __debug__:
							print 'request[2] is not alnum, see: ' + str(request[2])
				else:
					if __debug__:
						print 'request[1] is not len <= 10, see: ' + str(len(request[1])) + ' ' + str(request[1])
			else:
				if __debug__:
					print 'request[1] is not alnum, see: ' + str(request[1])
			
		elif request_type == 'DUMPLOG':
			request_d = { 'command' : 'DUMPLOG' }
			make_request(request_d)

		else:
			# INVALID REQUEST
			#print "invalid request: " + request[0]
			pass


if __name__ == "__main__":
    main()
