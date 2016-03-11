# trigger.py
##
# new
##
# 
#cache = {
#	user : {
#		transaction_id: 0,
#		stock_id : 'zyx',
#		expiration: time,
#		trigger: 0,
#		amount: 0,
#		type: 'BUY'|'SELL'
#	}
#}
#
# thread to recv incoming triggers filtered by transaction server
#	get quote
#	if trigger is already satisfied, apply result
#	otherwise put in cache with quote expiry
#
# thread to grind at cache, looking for expiring quotes
#	if quote expires, get new one
#		if trigger satisfied, apply
#		otherwise update expiry
#
#	Command line options
#	-h			help
#	-p portnum	set the port number to bind to
#
#	Input/Output
#	Expecting str(dict) with the following keys
#		stock_id, user, transactionNum, command, trigger, amount
#	Responds with 

#
##
# old
##
# Database stores triggers
# Get list of upcoming quote expirations on triggers
# get quotes for each one
# check against trigger price
# complete trigger if price met
#
# Every 5 seconds:
# get upcoming expirations
# 	connect to db
# 	request records
# get quotes for each
# 	connect to quote cache
# 	request quotes, ttl
# check against trigger
# 	compare quote against trigger val
# complete
# 	if buy
# 		if quote <= trigger, give stock, erase trigger
# 		else update ttl
# 	if sell
# 		if quote >= trigger, give money, erase trigger
# 		else update ttl

import ast
import os
import socket
import string
import sys
import time
import threading
import getopt

HOST = ''
PORT = 44420
MIN_PORT = 44420
MAX_PORT = 44429


DB_HOST = "b133.seng.uvic.ca"
DB_PORT = "44429"

MAX_THREADS = 10	# always one for the connection handler

QUOTE_REFRESH_TIME = 5000	# update records older than this many milliseconds

cache_lock = threading.Semaphore(1)

#-----------------------------------------------------------------------------
# now
# Returns server time in milliseconds
def now():
	return int(time.time() * 1000)

def cache_update(data):

	cache_lock.acquire()
	cache[data.get(user)] = {
		'command':data.get('command'),
		'stock_id':data.get('stock_id'),
		'transactionNum':data.get('transactionNum'),
		'trigger':data.get('trigger'),
		'amount':data.get('amount'),
		'cacheexpire':quote.get('cacheexpire')
	}
	cache_lock.release()
	
# 
def thread_conn_handler(connection):
	data = connection.recv(1024)
	data = ast.literal_eval(data)
		
	quote = get_quote(data['stock_id'])
	
	if data['command'] == 'BUY':
		if quote['price'] <= data['trigger']:
			give em the stock
		else:
			cache_update(data)
		connection.send('0')
	elif data['command'] == 'SELL':
		if quote['price'] >= data['trigger']:
			give em the cash
		else:
			cache_update(data)
		connection.send('0')
	else:
		connection.send('INVALID COMMAND')

def init_listen():

	try:
		incoming_socket.bind((HOST, PORT))
	except socket.error , msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		return 0
	
	if __debug__:
		print 'Socket bind complete'
		
	incoming_socket.listen(MAX_INCOMING_CONN_BUFFER)
	
	if __debug__:
		print 'Socket now listening'
		
	while 1:
		conn, addr = incoming_socket.accept()
		
		if __debug__:
			print 'Connection from ' + addr[0] + '\n'
		
		while threading.active_count() > MAX_THREADS:
			pass
		t = threading.Thread(target=thread_conn_handler, args=(conn,))
		t.start()

	return 1

def main(argv):
	global PORT
	
	try:
		cmdline_options, args = getopt.getopt(argv,'hp:')
	
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) + '\n'# will print something like "option -a not recognized"
		print 'Use -p [port number] to set port. Valid range is 44420 to 44429\n'
		usage()
		sys.exit(2)

	for o, a in cmdline_options:
		if o == "-p":
			a = int(a)
			if a >= MIN_PORT and a <= MAX_PORT:
				PORT = a
			else:
				print "Invalid port (" + str(a) + ") specified. Valid range: " + str(MAX_PORT) + " - " + str(MIN_PORT) + "\n"
				sys.exit(2)
		if o == "-h":
			print "Use -p to set port number. Valid range: " + str(MAX_PORT) + " - " + str(MIN_PORT) + "\n"
			sys.exit(2)
	print "Setting port [" + str(PORT) + "]\n"
	
	while True:
		for user,trigger in cache.iteritems():
			if trigger['expiration'] - now() < QUOTE_REFRESH_TIME:
				quote = get_quote(trigger['stock_id'])
				check_trigger(cache,quote)


	

if __name__ == "__main__":
	main(sys.argv[1:])

