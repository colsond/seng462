import ast
import os
import socket
import string
import sys
import time
import threading

HOST = ''
PORT = 44420

MAX_INCOMING_CONN_BUFFER = 10

MY_NAME = 'Cache1'

QUOTE_SERVER_HOST = 'quoteserve.seng.uvic.ca'
QUOTE_SERVER_PORT = 4444
QUOTE_SERVER_RECV = 100

AUDIT_SERVER_ADDRESS = 'b142.seng.uvic.ca'
AUDIT_SERVER_PORT = 44421

QUOTE_LIFE = 30	# in seconds

MAX_THREADS = 100

incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cache_lock = threading.Semaphore(1)

cache = {
	"ABC" : {
		'quote': 0,
		'user': "",
		'timestamp': 0,
		'cryptokey': "",
		'cacheexpire': 0
	}
}

#incoming
#	stock_id, user, transactionNum, command
#outoging
#	stock_id, user, transactionNum, quote, timestamp, key

# cache = {
	# stock: {
		# quote: 0,
		# user: "",
		# timestamp: 0,
		# cryptokey: "",
		# cacheexpire: 0
	# }
#}

def now():
	return int(time.time())

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

	return 1

def get_quote(stock_id, user, transactionNum):

	outgoing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	outgoing_socket.connect((QUOTE_SERVER_HOST, QUOTE_SERVER_PORT))
	request = stock_id + "," + user + "\r"
	outgoing_socket.send(request)

	response = outgoing_socket.recv(QUOTE_SERVER_RECV)
	outgoing_socket.close()
	
	if __debug__:
		print response
	
	#quote server response format 
	#quote,sym,userid,timestamp,cryptokey
	response = response.split(',')
	response[4] = response[4].rstrip()		#cryptokey sent with trailing newline
	
	message = {
		"price" : response[0],
		"stock_id" : response[1],
		"user" : response[2],
		"timestamp" : response[3],
		"cryptokey" : response[4]
	}
	
	audit_event("quote",message["timestamp"],transactionNum,None,message["user"],message["stock_id"],message["price"],message["timestamp"],message["cryptokey"],None)
	
	if __debug__:
		print '[' + response[0] + ':' + response[1] + ':' + response [2] + ':' + response[3] + ':' + response[4] + ']\n'

	return message

def send_audit(message):

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (AUDIT_SERVER_ADDRESS, AUDIT_SERVER_PORT)
	
	if __debug__:
		print 'connecting to ' + AUDIT_SERVER_ADDRESS + ' port ' + AUDIT_SERVER_PORT + '\n'
		
	sock.connect(server_address)

	try:
		sock.sendall(str(message))
		response = sock.recv(1024)
		
		if __debug__:
			print >>sys.stderr, 'sent "%s"\n' % message
			print >>sys.stderr, 'received "%s"\n' % response

	finally:
		if __debug__:
			print >>sys.stderr, 'closing socket'
		sock.close()

	return
	
def audit_event(
		type,
		timestamp,
		transactionNum, 
		command, 
		username, 
		stockSymbol,
		amount,
		quoteServerTime,
		cryptokey,
		errorMessage):
	
	message["server"] = MY_NAME

	if type == "incoming":
		message = {
			"logType": "SystemEventType",
			"timestamp": timestamp,
			"server" : MY_NAME,
			"transactionNum" : transactionNum,
			"command" : command,
			"username" : username,
			"stockSymbol" : stockSymbol
		}
	
	elif type == "quote":
		message = {
			"logType": "QuoteServerType",
			"timestamp": timestamp,
			"server" : MY_NAME,
			"transactionNum" : transactionNum,
			"price" : amount,
			"stockSymbol" : stockSymbol,
			"username" : username,
			"quoteServerTime": quoteServerTime,
			"cryptokey": cryptokey
		}
	
	else: #error message
		message = {
			"logType": "ErrorEventType",
			"timestamp": timestamp,
			"server" : MY_NAME,
			"transactionNum" : transactionNum,
			"command" : command,
			"username" : username,
			"stockSymbol" : stockSymbol,
			"funds" : amount,
			"errorMessage" : errorMessage
		}
	
	# send_audit(str(message))
	
	return
	
def scan_cache(stock_id):

	cache_lock.acquire()
	
	if stock_id in cache:
		if cache[stock_id]["cacheexpire"] >= now():
			message = {
				"status" : "success",
				"quote" : cache[stock_id]["quote"],
				"stock_id" : stock_id,
				"user" : cache[stock_id]["user"],
				"timestamp" : cache[stock_id]["timestamp"],
				"cryptokey": cache[stock_id]["cryptokey"]
			}
		else:
			message = {
				"status" : "expired"
			}
	else:
		message = {
			"status" : "unknown"
		}

	cache_lock.release()
	
	return message

def update_cache(quote):

	cache_lock.acquire()
	
	cache[quote.get("stock_id")] = {
		"quote" : quote["quote"],
		"user" : quote["user"],
		"timestamp" : quote["timestamp"],
		"cryptokey" : quote["cryptokey"],
		"cacheexpire" : now() + QUOTE_LIFE
	}
	
	cache_lock.release()
	
	return

def error_quote():	
	quote = {
		"price" : 0,
		"stock_id" : "Error",
		"user" : "Error",
		"timestamp" : 0,
		"cryptokey" : "Error"
	}
	
	return quote

def thread_conn_handler(conn):
	data = conn.recv(1024)
	
	data = ast.literal_eval(data)
	if data.get("command") == "BUY" or data.get("command") == "SELL":
		quote = get_quote(data.get("stock_id"),data.get("user"),data.get("transactionNum"))
		update_cache(quote)
	elif data.get(command) == "QUOTE":
		quote = scan_cache(data.get("stock_id"))
		if quote["status"] != "success":
			quote = get_quote(data.get("stock_id"),data.get("user"),data.get("transactionNum"))
			update_cache(quote)
	else:
		quote = error_quote()
		
	conn.send(str(quote))
	conn.close()
	return

def main():

	if init_listen():
		while 1:
			conn, addr = incoming_socket.accept()
			
			if __debug__:
				print 'Connection from ' + addr[0] + '\n'
			
			while threading.active_count() > MAX_THREADS:
				pass
			t = threading.Thread(target=thread_conn_handler, args=(conn))
			t.start()
			

if __name__ == "__main__":
	main()