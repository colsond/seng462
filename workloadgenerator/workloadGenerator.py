import requests
import io

BASE_URL = 'http://requestb.in/1g5erwn1'
ADD_REQUEST = "add"
QUOTE_REQUEST = "quote"
BUY_REQUEST = "buy"
COMMIT_BUY_REQUEST = "commit_buy"
COMMIT_SELL_REQUEST = "commit_sell"
DISPLAY_SUMMARY_REQUEST = "display_summary"
CANCEL_BUY_REQUEST = "cancel_buy"
CANCEL_SET_BUY_REQUEST = "cancel_set_buy"
SET_BUY_AMOUNT_REQUEST = "set_buy_amount"
SELL_REQUEST = "sell"
CANCEL_SET_SELL_REQUEST = "cancel_set_sell"
SET_SELL_TRIGGER_REQUEST = "set_sell_trigger"
SET_SELL_AMOUNT_REQUEST = "set_sell_amount"
DUMPLOG_REQUEST = "dumplog"

		
def request_add(user, amount):
	data = {
		'user': user,
		'amount': amount
	}
	url = BASE_URL
	print url
	r = requests.post(BASE_URL, data)

	if 1 == 1:
		print r.text
		print "success"
		return

def request_quote(user, stock_id):
	data = {
		'user': user,
		'stock_id': stock_id
	}

	r = requests.post(BASE_URL + QUOTE_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_buy(user, stock_id, amount):
	data = {
		'user': user,
		'stock_id': stock_id,
		'amount': amount
	}

	r = requests.post(BASE_URL + BUY_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_commit_buy(user):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + COMMIT_BUY_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_commit_sell(user):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + COMMIT_SELL_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_display_summary(user):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + DISPLAY_SUMMARY_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_cancel_buy(user):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + CANCEL_BUY_REQUEST, data)

	if 1 == 1:
		print "success"
		return

def request_set_buy_amount(user, stock_id=None, amount=None):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + SET_BUY_AMOUNT_REQUEST, data)

	if 1 == 1:
		print "success"
		return
	
def request_sell(user, stock_id=None, amount=None):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + SELL_REQUEST, data)

	if 1 == 1:
		print "success"
		return
	
def request_cancel_set_sell(user, stock_id=None):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + CANCEL_SET_SELL_REQUEST, data)

	if 1 == 1:
		print "success"
		return
	
def request_set_sell_trigger(user, stock_id=None, amount=None):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + SET_SELL_TRIGGER_REQUEST, data)

	if 1 == 1:
		print "success"
		return
	
def request_set_sell_amount(user, stock_id=None, amount=None):
	data = {
		'user': user,
		'stock_id': stock_id,
		'amount': amount
	}

	r = requests.post(BASE_URL + SET_SELL_AMOUNT_REQUEST, data)

	if 1 == 1:
		print "success"
		return
	
def request_dumplog(filename, user=None):
	data = {
		'user': user
	}

	r = requests.post(BASE_URL + DUMPLOG_REQUEST, data)

	if 1 == 1:
		print "success"
		return

f = open("1userWorkLoad", 'r')
for line in f:
	tokens = line.split()
	cmdNum = tokens[0]
	request = tokens[1].split(',')

	if request[0].lower() == ADD_REQUEST:
		user = request[1]
		amount = request[2]
		request_add(user, amount)
		print request[0]

	elif request[0].lower() == QUOTE_REQUEST:
		user = request[1]
		stock_id = request[2]
		request_quote(user, stock_id)
		print request[0]

	elif request[0].lower() == BUY_REQUEST:
		user = request[1]
		stock_id = request[2]
		amount = request[3]
		request_buy(user, stock_id, amount)
		print request[0]

	elif request[0].lower() == COMMIT_BUY_REQUEST:
		user = request[1]
		request_commit_buy(user)
		print request[0]

	elif request[0].lower() == COMMIT_SELL_REQUEST:
		user = request[1]
		request_commit_sell(user)
		print request[0]

	elif request[0].lower() == DISPLAY_SUMMARY_REQUEST:
		user = request[1]
		request_display_summary(user)
		print request[0]

	elif request[0].lower() == CANCEL_BUY_REQUEST:
		user = request[1]
		request_cancel_buy(user)
		print request[0]
		
	elif request[0].lower() == CANCEL_SET_BUY_REQUEST:
		user = request[1]
		request_cancel_set_sell(user)
		print request[0]
		
	elif request[0].lower() == SET_SELL_AMOUNT_REQUEST:
		user = request[1]
		request_set_sell_amount(user)
		print request[0]
		
	elif request[0].lower() == SELL_REQUEST:
		user = request[1]
		request_sell(user)
		print request[0]
		
	elif request[0].lower() == CANCEL_SET_SELL_REQUEST:
		user = request[1]
		request_cancel_set_sell(user)
		print request[0]
		
	elif request[0].lower() == SET_SELL_TRIGGER_REQUEST:
		user = request[1]
		request_set_sell_trigger(user)
		print request[0]
		
	elif request[0].lower() == SET_SELL_AMOUNT_REQUEST:
		user = request[1]
		request_set_sell_amount(user)
		print request[0]
		
	elif request[0].lower() == DUMPLOG_REQUEST:
		user = request[1]
		request_dumplog(user)
		print request[0]

	else:
		# INVALID REQUEST
		print "invalid request: " + request[0]


