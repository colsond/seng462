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
#		cacheexpire: time,
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
#	-h	help
#	-p	portnum	set the port number to bind to
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
import Queue

HOST = ''
PORT = 44420
MIN_PORT = 44420
MAX_PORT = 44429

incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
incoming_socket.settimeout(1)

MAX_INCOMING_CONN_BUFFER = 10

NUM_LISTENER_THREADS = 10

MAX_THREADS = 50	# always one for the connection handler

QUOTE_REFRESH_TIME = 5000	# update records older than this many milliseconds

cache_lock = threading.Semaphore(1)
cache = {}

subcache_lock = threading.Semaphore(1)
subcache = {}
subcache_updated = 0		# dirty flag

audit_server_address = 'b142.seng.uvic.ca'
audit_server_port = 44421

cache_server_address = 'b143.seng.uvic.ca'
cache_server_port = 44420

shutdown = 0

q = Queue.Queue()

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
	#print '--Quote server fuel:\n' + str(data)
	#print '--Quote server reply:\n' + str(response)
	sock.close()

	return response
	
def subcache_update(data):
	global subcache_updated
	global subcache_lock
	global subcache

	subcache_lock.acquire()
	for i in data:
		if i not in subcache:
			subcache[i] = {}
		for j in data[i]:
			subcache[i][j] = data[i][j]
	subcache_lock.release()

	subcache_updated += 1

#-----------------------------------------------------------------------------
# thread_conn_handler(connection)
#
#	connection : a accepted connection from init_listen
#
# Read data from incoming connection. Exists in a thread.
# Special incoming command to show cache contents for debugging
# {command: 'DUMP', stock_id: ANY, user: ANY, transactionNum: ANY}
#
def thread_conn_handler():
	global shutdown
	global cache
	global subcache

	while True:
		#If the shutdown has been signalled, make sure the queue is empty before exiting
		if q.empty():

			if shutdown > 0:
				break
			else:
				pass

		else:

			connection = q.get()
			data = connection.recv(1024)
			data = ast.literal_eval(data)

			if __debug__:
				f = open('handle-' + str(data.get('transactionNum','no_transactionNum')),'a')
				f.write('Received from incoming connection from ' + str(connection.getpeername()) + '\n')
				f.write(str(data) + '\n')
				f.close()

			connection.close()

			if data.get('command') == 'DUMP':

				shutdown += 1
				q.task_done()

				if __debug__:
					print '\n----------------------------' + str(shutdown) + '------------------------------\n'
					print '\n----------------------------' + str(shutdown) + '------------------------------\n'

				break

			else:
				#process incoming data
				temp = {data.get('user','Error'):{data.get('stock_id'):{'cacheexpire':0,'amount':data.get('amount'),'trigger':data.get('trigger'),'transactionNum':data.get('transactionNum'),'command':data.get('command')}}}
				subcache_update(temp)

				#get a quote from the quote cache and see if the trigger can be cleared
				cache_check(subcache,data.get('user'),data.get('stock_id'))
				q.task_done()

#end thread_conn_handler

			
# --------
# init_listen()
#
# Set up socket and process incoming connections
#	Incoming connection passed to a new thread to accept and process data
#
# Future: set up a queue and have a consumer thread to control the number of threads created
def init_listen():
	global shutdown

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

	#Create consumer threads
	for i in range(NUM_LISTENER_THREADS):
		t = threading.Thread(target=thread_conn_handler, args=())
		t.daemon = True
		t.start()
	
	# Put incoming requests on a queue to be consumed
	while True:

		# flag set in the consumer threads when a 'DUMP' command is received
		if shutdown > 0:

			break

		else:

			try:
				conn, addr = incoming_socket.accept()
			except:
				pass
			else:
				if __debug__:
					#print 'Connection from ' + addr[0] + ' - shutdown = ' + str(shutdown) + '\n'
					pass

				q.put(conn)

	if __debug__:
		print 'Waiting for queue to empty\n'

	q.join()

	incoming_socket.close()
#end init_listen
	
def cache_check(cache, user, stock):#, values):
	global cache_updated

	if __debug__:
		print cache #### PROBLEM HERE
		f = open('handle-' + str(cache[user][stock].get('command')) + '-' + str(cache[user][stock].get('transactionNum','bad_cache_check')),'a')
		f.write('Function cache_check input:\n')
		f.write('User [' + str(user) + ']\n')
		f.write('Stock [' + str(stock) + ']\n')
		f.write('Cache [' + str(cache) + ']\n\n')

	if cache[user][stock].get('cacheexpire') is not None:

		if __debug__:
			f.write('Checking if transaction ' + str(cache[user][stock].get('transactionNum')) + ' needs to be refreshed\n')
			f.write('Using the following values\n')
			f.write(str(cache[user][stock].get('cacheexpire')) + ' - ' + str(now()) + ' = ' + str(cache[user][stock].get('cacheexpire') - now()) + ' < ' + str(QUOTE_REFRESH_TIME) + '\n\n')

		if (cache[user][stock].get('cacheexpire') - now()) < QUOTE_REFRESH_TIME:

			#assemble the quote request
			tx_data = {'stock_id':stock,'user':user,'transactionNum':cache[user][stock]['transactionNum'],'command':'TRIGGER'}

			if __debug__:
				f.write('Refresh required. Getting new quote for transaction ' + str(cache[user][stock].get('transactionNum')) + ' using:\n')
				f.write(str(tx_data) + '\n\n')

			#send quote request
			quote = get_quote(tx_data)
			#returns: stock_id, user, transactionNum, price, timestamp, cryptokey, cacheexpire
			
			#BUY trigger
			if cache[user][stock].get('command') == 'BUY':

				if __debug__:
					f.write('Buy quote value (' + str(quote.get('price')) + '), Trigger buy at (' + str(cache[user][stock].get('trigger')) + ')\n')			

				if quote.get('price') <= cache[user][stock].get('trigger'):

					if __debug__:
						f.write('Buy trigger activated on transaction ' + str(cache[user][stock].get('transactionNum')) + '\n\n')

					#give the stock
					del cache[user][stock]
					if any(cache[user]):
						if __debug__:
							f.write('User has remaining stock triggers - leaving user in cache\n')
					else:
						if __debug__:
							f.write('User has no remaining stock triggers - removing user from cache\n')
						del cache[user]
					
				else:

					if __debug__:
						f.write('Buy trigger not activated on transaction ' + str(cache[user][stock].get('transactionNum')) + '\n')
						f.write('Expiration updated\n')
						f.write('New expiration: ' + str(quote.get('cacheexpire')) + '\n\n')

					cache[user][stock]['cacheexpire'] = quote.get('cacheexpire')
			
			#SELL trigger
			elif cache[user][stock].get('command') == 'SELL':

				if __debug__:
					f.write('Sell quote value (' + str(quote.get('price')) + '), Trigger price (' + str(cache[user][stock].get('trigger')) + ')\n')
			
				if quote.get('price') >= cache[user][stock].get('trigger'):

					if __debug__:
						f.write('Sell trigger activated on transaction ' + str(cache[user][stock].get('transactionNum')) + '\n\n')

					#give the money

					if __debug__:
						f.write('Removing stock trigger from user\n')

					del cache[user][stock]

					if any(cache[user]):
						if __debug__:
							f.write('User has remaining stock triggers - leaving user in cache\n')
					else:
						if __debug__:
							f.write('User has no remaining stock triggers - removing user from cache\n')
						del cache[user]
					
				else:

					if __debug__:
						f.write('Trigger not activated on transaction ' + str(cache[user][stock].get('transactionNum')) + '\n')
						f.write('Expiration updated\n')
						f.write('New expiration: ' + str(quote.get('cacheexpire')) + '\n\n')

					cache[user][stock]['cacheexpire'] = quote.get('cacheexpire')
					
			else:
				if __debug__:
					f.write('Not a BUY or SELL trigger\n')
					f.write('User [' + str(user) + ']\n')
					f.write('Stock [' + str(stock) + ']\n')
					f.write('Cache [' + str(cache) + ']\n\n')
				pass

	if __debug__:
		f.write('Function cache_check output:\n')
		f.write('User [' + str(user) + ']\n')
		f.write('Stock [' + str(stock) + ']\n')
		f.write('Cache [' + str(cache) + ']\n\n')

	f.close
#end cache_check


def main(argv):
	global PORT
	global subcache
	global subcache_lock
	global subcache_updated
	global cache
	global shutdown

	print '-------------------------------------------------------------------'
	print 'STARTING'
	print '-------------------------------------------------------------------'

	try:
		cmdline_options, args = getopt.getopt(argv,'hp:')
	
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) + '\n'	# will print something like "option -a not recognized"
		print 'Use -p [port number] to set port. Valid range is ' + str(MIN_PORT) + ' to ' + str(MAX_PORT) + '\n'
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
	
	# Set up incoming socket, create consumer threads for incoming connections,
	# queue up incoming data for consumers
	t = threading.Thread(target=init_listen, args=())
	t.start()
	
	while True:
		subcache_lock.acquire()
		if subcache_updated > 0:
			for user,trigger in subcache.iteritems():
				if user not in cache:
					cache[user] = {}
				for stock,values in trigger.iteritems():
					cache[user][stock] = values
			subcache={}
			subcache_updated = 0

			if __debug__:
				print 'subcache emptied? ' + str(subcache)

		subcache_lock.release()
		if shutdown > 0:
			break

	t.join()
	cache_updated = 0

	if __debug__:
		print '\n---------------\n'
		print 'cache contents:\n'
		print str(cache)
		print '\n---------------\n'
		print 'subcache contents:\n'
		print str(subcache)	

if __name__ == "__main__":
	main(sys.argv[1:])

		# for user,triggers in cache.iteritems():
			# for stock,values in triggers.iteritems():

## Test if the keys actually exist

				# if subcache_updated > 0:
					# break
				
				# if user is not None:
					# cache_updated = thread_cache_check(user, stock, values)
					
				# if cache_updated > 0:
					# break
				# # while threading.active_count() > MAX_THREADS:
					# # pass
				# # t_check = threading.Thread(target=thread_cache_check, args=(user, stock, values,))
				# # t_check.start()

			# if cache_updated > 0:
				# break
				
			# if subcache_updated > 0:
				# break
				
		# # entry removed from cache - restart scan - no action required
		# if cache_updated > 0:
			# cache_updated = 0

			
		# # new triggers have been received - add to cache

