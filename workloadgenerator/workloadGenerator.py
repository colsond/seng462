import io
import socket
import sys
import string

web_server_address = 'b142.seng.uvic.ca'
web_server_port = 44421

ADD = "ADD"
QUOTE = "QUOTE"
BUY = "BUY"
COMMIT_BUY = "COMMIT_BUY"
CANCEL_BUY = "CANCEL_BUY"
SELL = "SELL"
COMMIT_SELL = "COMMIT_SELL"
CANCEL_SELL = "CANCEL_SELL"
SET_BUY_AMOUNT = "SET_BUY_AMOUNT"
CANCEL_SET_BUY = "CANCEL_SET_BUY"
SET_BUY_TRIGGER = "SET_BUY_TRIGGER"
SET_SELL_AMOUNT = "SET_SELL_AMOUNT"
SET_SELL_TRIGGER = "SET_SELL_TRIGGER"
CANCEL_SET_SELL = "CANCEL_SET_SELL"
DUMPLOG = "DUMPLOG"
DISPLAY_SUMMARY = "DISPLAY_SUMMARY"


def make_request(transaction_id, request_type, user, stock_id=None, amount=None):
	data = {
		'transaction_id': transaction_id,
		'request_type': request_type,
		'user': user
	}

	if stock_id:
		data['stock_id'] = stock_id

	if amount:
		data['amount'] = amount

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (web_server_address, web_server_port)
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)


	try:
			# Send data
			message = str(data)
			sock.sendall(message)
			print >>sys.stderr, 'sent "%s"' % message
			response = sock.recv(1024)
			print >>sys.stderr, 'received "%s"' % response
			response = ' '

	    # Look for the response
#	    amount_expected = len(message)
#	    response = ""

#	    while response[-1:] != "\n":
#	        response_data = sock.recv(16)
#	        response += response_data

	finally:
	    print >>sys.stderr, 'closing socket'
	    sock.close()

	return response

def main():

	bad_chars = '[]'

	f = open("1userWorkLoad", 'r')
	for line in f:

		# partition returns a 3-tuple: part before seperator, seperator, 
		# part after seperator - if it fails: original string, empty, empty
		tokens = line.partition(' ')
		#tokens = line.split()

		transaction_id = tokens[0]
		# quick way to nuke the brackets
		transaction_id = transaction_id.translate(None, bad_chars)

		request = tokens[2].split(',')

		request_type = request[0]

		if request_type == ADD:
			user = request[1]
			amount = request[2]
			make_request(transaction_id, request_type, user, amount)

		elif request_type == QUOTE:
			user = request[1]
			stock_id = request[2]
			make_request(transaction_id, request_type, user, stock_id)

		elif request_type == BUY:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)

		elif request_type == COMMIT_BUY:
			user = request[1]
			make_request(transaction_id, request_type, user)
			
		elif request_type == CANCEL_BUY:
			user = request[1]
			make_request(transaction_id, request_type, user)
			
		elif request_type == SELL:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)

		elif request_type == COMMIT_SELL:
			user = request[1]
			make_request(transaction_id, request_type, user)

		elif request_type == CANCEL_SELL:
			user = request[1]
			make_request(transaction_id, request_type, user)

		elif request_type == SET_BUY_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)
			
		elif request_type == CANCEL_SET_BUY:
			user = request[1]
			stock_id = request[2]
			make_request(transaction_id, request_type, user, stock_id)
			
		elif request_type == SET_BUY_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)
			
		elif request_type == SET_SELL_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)
			
		elif request_type == SET_SELL_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(transaction_id, request_type, user, stock_id, amount)
			
		elif request_type == CANCEL_SET_SELL:
			user = request[1]
			stock_id = request[2]
			make_request(transaction_id, request_type, user, stock_id)
			
		elif request_type == DUMPLOG:
			if len(request) == 3:
				make_request(transaction_id, request_type, request[3])
			elif len(request) == 4:
				make_request(transaction_id, request_type, request[3], request[4])

		elif request_type == DISPLAY_SUMMARY:
			user = request[1]
			make_request(transaction_id, request_type, user)

		else:
			# INVALID REQUEST
			print "invalid request: " + request[0]


if __name__ == "__main__":
    main()
