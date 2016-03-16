#1:22
#10:15am
#
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

incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

MAX_INCOMING_CONN_BUFFER = 10

MAX_THREADS = 50	# always one for the connection handler

QUOTE_REFRESH_TIME = 5000	# update records older than this many milliseconds

cache = {}

subcache_lock = threading.Semaphore(1)
subcache = {}
subcache_updated = 0		# dirty flag

audit_server_address = 'b142.seng.uvic.ca'
audit_server_port = 44421

cache_server_address = 'b143.seng.uvic.ca'
cache_server_port = 44420

#-----------------------------------------------------------------------------
# now
# Returns server time in milliseconds
def now():
	return int(time.time() * 1000)

# Request a Quote from the quote server
# Values returned from function in the order the quote server provides
#	Input/Output
#	Expecting str(dict) with the following keys
#		stock_id, user, transactionNum, command
#	Responds with str(dict) with the following keys
#		stock_id, user, transactionNum, price, timestamp, cryptokey, cacheexpire
#
# Note: function returns price in cents
#returns price of stock, doesnt do any checking.
# target_server_address and target_server_port need to be set globally or the function must be modified to receive these values
def get_quote(data):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = (cache_server_address, cache_server_port)
    
    sock.connect(server_address)
    sock.sendall(str(data))
    response = sock.recv(1024)
    response = ast.literal_eval(response)
    sock.close()
    return  response
	
def subcache_update(data):

	subcache_lock.acquire()
	subcache[data.get(user)] = {
		'command':data.get('command'),
		'stock_id':data.get('stock_id'),
		'transactionNum':data.get('transactionNum'),
		'trigger':data.get('trigger'),
		'amount':data.get('amount'),
		'cacheexpire':quote.get('cacheexpire')
	}
	subcache_updated += 1
	subcache_lock.release()
			
# --------
# thread_conn_handler(connection)
#
#	connection : a accepted connection from init_listen
#
# Read data from incoming connection. Exists in a thread.
# Special incoming command to show cache contents for debugging
# {command: 'DUMP', stock_id: ANY, user: ANY, transactionNum: ANY}
#
def thread_conn_handler(connection):
	data = connection.recv(1024)
	data = ast.literal_eval(data)
	
	if data.get('command') == 'DUMP':
		print cache
	else:
		#process incoming data
		temp = {data.get('user'):{data.get('stock_id'):{'price':data.get('price'),'trigger':data.get('trigger'),'command':data.get('command')}}}
		
		#get a quote from the quote cache and see if the trigger can be cleared
		cache_check(temp,data.get('user'),data.get('stock_id'))
		if temp.get('user',None) is None:
			#trigger already completed
			pass
		else:
			#add trigger to cache
			subcache_update(temp)
			
	connection.close()
			
# --------
# init_listen()
#
# Set up socket and process incoming connections
#	Incoming connection passed to a new thread to accept and process data
#
# Future: set up a queue and have a consumer thread to control the number of threads created
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
		t_incoming = threading.Thread(target=thread_conn_handler, args=(conn,))
		t_incoming.start()

	
def cache_check(cache, user, stock):#, values):
	
	if (cache[user][stock].get('expiration') - now()) < QUOTE_REFRESH_TIME:
		tx_data = {'stock_id':stock,'user':user,'transactionNum':cache[user][stock]['transactionNum'],'command':'TRIGGER'}
		quote = get_quote(tx_data)
		#stock_id, user, transactionNum, price, timestamp, cryptokey, cacheexpire
		
		if cache[user][stock].get('command') == 'BUY':
		
			if quote.get('price') <= cache[user][stock].get('trigger'):
				#give the stock
				del cache[user][stock]
				cache_updated += 1
				
			else:
				cache[user][stock]['price'] = quote.get('price')
				cache[user][stock]['cacheexpire'] = quote.get('cacheexpire')
				
		elif cache[user][stock].get('command') == 'SELL':
		
			if quote.get('price') >= cache[user][stock].get('trigger'):
				#give the money
				del cache[user][stock]
				cache_updated += 1
				
			else:
				cache[user][stock]['price'] = quote.get('price')
				cache[user][stock]['cacheexpire'] = quote.get('cacheexpire')
				
		else:
			pass
	return cache_updated

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
	if __debug__:
		print "Setting port [" + str(PORT) + "]\n"
	
	t = threading.Thread(target=init_listen, args=())
	t.start()
	
	cache_updated = 0
	
	while True:
		for user,triggers in cache.iteritems():
			for stock,values in triggers.iteritems():
				if subcache_updated > 0:
					break
				
				if user is not None:
					cache_updated = thread_cache_check(user, stock, values)
					
				if cache_updated > 0:
					break
				# while threading.active_count() > MAX_THREADS:
					# pass
				# t_check = threading.Thread(target=thread_cache_check, args=(user, stock, values,))
				# t_check.start()

			if cache_updated > 0:
				break
				
			if subcache_updated > 0:
				break
				
		# entry removed from cache - restart scan - no action required
		if cache_updated > 0:
			cache_updated = 0
			
		# new triggers have been received - add to cache
		if subcache_updated > 0:
			subcache_lock.acquire()
			for user,trigger in subcache.iteritems():
				for stock,values in triggers.iteritems():
					cache[user][stock] = values
			subcache={}
			subcache_lock.release()
	

if __name__ == "__main__":
	main(sys.argv[1:])

