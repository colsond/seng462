import requests
import io

WEB_SERVER_URL = 'http://localhost:8000/'
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

	r = requests.post(WEB_SERVER_URL, data)

	print r.text

	if r.status_code:
		print "success"
		return
	else:
		print "failure"
		return

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


