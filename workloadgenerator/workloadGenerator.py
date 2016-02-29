import io
import socket
import sys
import string
import Queue
from threading import Thread, current_thread

#workload generator aims for however many transaction servers are set in the list below, all looking on port 44422 
tx_server_address = ['b132.seng.uvic.ca', 'b133.seng.uvic.ca', 'b134.seng.uvic.ca', 'b134.seng.uvic.ca']
NUM_WORKER_THREADS = len(tx_server_address)
# tx_server_address = 'localhost'
# Port list, in case things are run on same machine
# 44421	Audit
# 44422 Transaction port

web_server_port = 44422

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


q = Queue.Queue()

def make_request(pid, transaction_id, command, user=None, stock_id=None, amount=None, filename=None):
	data = {
		'transaction_id': transaction_id,
		'command': command,
	}

	if user:
		data['user'] = user

	if stock_id:
		data['stock_id'] = stock_id

	if amount:
		data['amount'] = amount
	
	if filename:
		data['filename'] = filename

	print str(data)
		
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (tx_server_address[pid], web_server_port)
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

def processWorkloadFile(sourceDir, targetDir, workloadFile):
	fileDict = {}
	userList = []
	f = open (workloadFile, 'r')
	for line in f:
		tokens = line.split(' ')
		commandInfo = tokens[1].split(',')
		user = commandInfo[1]

		#need to decide what to do with the dump command
		if commandInfo[0]==DUMPLOG:
			fileDict['last']=line
		else:
			if user not in userList:
				userList.append(user)
			if user in fileDict:
				fileDict[user] += line
			else:
				fileDict[user] = line
	f.close()
	for user in userList:
		f = open ((targetDir+ user + '.txt'), 'w')
		f.write(fileDict[user])
		f.close()
	return userList



def sendWorkload(user, pid):
	bad_chars = '[]'

	f = open('./seperatedWorkload/' + user + '.txt', 'r')
	for line in f:

		tokens = line.split(' ')

		transaction_id = tokens[0]
		transaction_id = transaction_id.translate(None, bad_chars)

		request = tokens[1].split(',')

		command = request[0]

		if command == ADD:
			user = request[1]
			amount = request[2]
			make_request(pid, transaction_id, command, user, amount=amount)

		elif command == QUOTE:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transaction_id, command, user, stock_id)

		elif command == BUY:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)

		elif command == COMMIT_BUY:
			user = request[1]
			make_request(pid, transaction_id, command, user)
			
		elif command == CANCEL_BUY:
			user = request[1]
			make_request(pid, transaction_id, command, user)
			
		elif command == SELL:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)

		elif command == COMMIT_SELL:
			user = request[1]
			make_request(pid, transaction_id, command, user)

		elif command == CANCEL_SELL:
			user = request[1]
			make_request(pid, transaction_id, command, user)

		elif command == SET_BUY_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)
			
		elif command == CANCEL_SET_BUY:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transaction_id, command, user, stock_id)
			
		elif command == SET_BUY_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)
			
		elif command == SET_SELL_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)
			
		elif command == SET_SELL_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transaction_id, command, user, stock_id, amount)
			
		elif command == CANCEL_SET_SELL:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transaction_id, command, user, stock_id)
			
		elif command == DUMPLOG:
			if len(request) == 2:
				#filename
				filename = request[1]
				make_request(pid, transaction_id, command, filename=filename)
			elif len(request) == 3:
				#userid, filename
				user = request[1]
				filename = request[2]
				make_request(pid, transaction_id, command, user, filename=filename)

		elif command == DISPLAY_SUMMARY:
			user = request[1]
			make_request(pid, transaction_id, command, user)

		else:
			# INVALID REQUEST
			print "invalid request: " + request[0]


def worker(id):
	while True:
	    user = q.get()
	    process = id
	    sendWorkload(user, process)
	    q.task_done()

def main():
	userList = processWorkloadFile('/','./seperatedWorkload/','10User_testWorkLoad.txt')


	for i in range(NUM_WORKER_THREADS):
		t = Thread(target=worker, args=(i,))
		t.daemon = True
		t.start()

	for item in userList:
	    q.put(item)

	q.join() #blocks until everything is done
	#then send last command
	sendWorkload("last", 0)



if __name__ == "__main__":
    main()
