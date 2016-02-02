import requests
import io
import socket
import sys

WEB_SERVER_URL = 'http://requestb.in/yc78qnyc'
ADD = "ADD"
QUOTE = "QUOTE"
BUY = "BUY"
COMMIT_BUY = "COMMIT_BUY"
COMMIT_SELL = "COMMIT_SELL"
DISPLAY_SUMMARY = "DISPLAY_SUMMARY"
CANCEL_BUY = "CANCEL_BUY"
CANCEL_SET_BUY = "CANCEL_SET_BUY"
SET_BUY_AMOUNT = "SET_BUY_AMOUNT"
SELL = "SELL"
CANCEL_SET_SELL = "CANCEL_SET_SELL"
SET_SELL_TRIGGER = "SET_SELL_TRIGGER"
SET_SELL_AMOUNT = "SET_SELL_AMOUNT"
DUMPLOG = "DUMPLOG"


def make_request(request_type, user, stock_id=None, amount=None):
	data = {
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
	server_address = ('b150.seng.uvic.ca', 44421)
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)


	try:
	    # Send data
	    message = str(data)
	    print >>sys.stderr, 'sending "%s"' % message
	    sock.sendall(message)

	    # Look for the response
	    amount_received = 0
	    amount_expected = len(message)
	    response = ""

	    while amount_received < amount_expected:
	        response_data = sock.recv(16)
	        amount_received += len(response_data)
	        response += response_data
	        print >>sys.stderr, 'received "%s"' % data

	finally:
	    print >>sys.stderr, 'closing socket'
	    sock.close()

	return response

f = open("1userWorkLoad", 'r')
for line in f:
	tokens = line.split()
	cmdNum = tokens[0]
	request = tokens[1].split(',')

	request_type = request[0]
	user = request[1]

	if request_type == ADD:
		amount = request[2]
		make_request(request_type, user, amount)
		

	elif request_type == QUOTE:
		stock_id = request[2]
		make_request(request_type, user, stock_id)
		

	elif request_type == BUY:
		stock_id = request[2]
		amount = request[3]
		make_request(request_type, user, stock_id, amount)
		

	elif request_type == COMMIT_BUY:
		make_request(request_type, user)
		

	elif request_type == COMMIT_SELL:
		make_request(request_type, user)
		

	elif request_type == DISPLAY_SUMMARY:
		make_request(request_type, user)
		

	elif request_type == CANCEL_BUY:
		make_request(request_type, user)
		
		
	elif request_type == CANCEL_SET_BUY:
		make_request(request_type, user)
		
		
	elif request_type == SET_SELL_AMOUNT:
		make_request(request_type, user)
		
		
	elif request_type == SELL:
		make_request(request_type, user)
		
		
	elif request_type == CANCEL_SET_SELL:
		make_request(request_type, user)
		
		
	elif request_type == SET_SELL_TRIGGER:
		make_request(request_type, user)
		
		
	elif request_type == SET_SELL_AMOUNT:
		make_request(request_type, user)
		
		
	elif request_type == DUMPLOG:
		make_request(request_type, user)
		

	else:
		# INVALID REQUEST
		print "invalid request: " + request[0]


