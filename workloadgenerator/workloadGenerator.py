import io
import socket
import sys
import string
import Queue
import os

from threading import Thread, current_thread

#this id is for running multiple generators, currently we only support 2
if(len(sys.argv)==2):
    workload_id = int(sys.argv[1])
else:
    workload_id = 0

workloadport = 44444
workloadadress = 'b130.seng.uvic.ca'
src_address = (workloadadress, workloadport)

#workload generator aims for however many transaction servers are set in the list below, all looking on port 44422 
tx_server_address = ['b131.seng.uvic.ca', 'b132.seng.uvic.ca', 'b133.seng.uvic.ca', 'b134.seng.uvic.ca', 'b135.seng.uvic.ca','b136.seng.uvic.ca', 'b137.seng.uvic.ca', 'b138.seng.uvic.ca', 'b139.seng.uvic.ca', 'b140.seng.uvic.ca']
tx_server_port = 44422

AUDIT_SERVER_ADDRESS = 'b149.seng.uvic.ca'
AUDIT_SERVER_PORT = 44421

NUM_WORKER_THREADS = 100

web_server_port = 44422
web_server_authenticate = 'http://127.0.0.1:5000/authenticate'

MY_NAME = "Workload"

workload_file = '1000User_testWorkLoad.txt'
working_dir = './separatedWorkload/'
user_count = 0

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


#-----------------------------------------------------------------------------
#
def make_request(pid, transactionNum, command, user=None, stock_id=None, amount=None, filename=None):
	data = {
		'transactionNum': transactionNum,
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

	#print str(data)
		
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#bind to source address so it doesnt use random ports
	sock.bind(src_address)

	# Connect the socket to the port where the server is listening
	server_address = (tx_server_address[pid%len(tx_server_address)], tx_server_port)
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)

	try:
			# Send data
			message = str(data)
			sock.sendall(message)
			#print >>sys.stderr, 'sent "%s"' % message
			response = sock.recv(1024)
			#print >>sys.stderr, 'received "%s"' % response
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


#-----------------------------------------------------------------------------
#
def processWorkloadFile(sourceDir, targetDir, workloadFile):
	global user_count
	fileDict = {}
	userList = []

	try:
		f = open (workloadFile, 'r')
	except IOError as err:
		if err[0] == 2:
			print "Workload file [" + workloadFile + "] does not exist. Exiting.\n"
			exit()

	for line in f:
		tokens = line.split(' ')
		commandInfo = tokens[1].split(',')
		user = commandInfo[1]

		#need to decide what to do with the dump command
		if commandInfo[0]==DUMPLOG:
			if 'last' in fileDict:
				fileDict['last']+=line
			else:
				fileDict['last']=line
		else:
			if user not in userList: 
				userList.append(user)
				user_count = user_count + 1
			if user in fileDict:
				fileDict[user] += line
			else:
				fileDict[user] = line

	f.close()

	try:
		f = open ("userRefList.txt", 'w')
	except IOError as err:
		   pass
	for user in userList:
		f.write(user)

	f.close()

	# try to make the target directory; if it errors for a reason other than 
	# the directory already exists, then raise an exception
	try:
		os.makedirs(targetDir)
	except OSError:
		if not os.path.isdir(targetDir):
				raise

	for user in userList:
		try:
			f = open ((targetDir + user + '.txt'), 'w')
		except IOError as err:
			print err

		f.write(fileDict[user])
		f.close()

	# Keep 'last' out of the userlist
	try:
		f = open ((targetDir + 'last.txt'), 'w')
	except IOError as err:
		print err

	f.write(fileDict['last'])
	f.close()

	return userList


#-----------------------------------------------------------------------------
#
def sendWorkload(user, pid):
	bad_chars = '[]'

	f = open(working_dir + user + '.txt', 'r')
	for line in f:

		tokens = line.split(' ')

		transactionNum = tokens[0]
		transactionNum = transactionNum.translate(None, bad_chars)

		request = tokens[1].split(',')

		command = request[0]

		if command == ADD:
			user = request[1]
			amount = request[2]
			make_request(pid, transactionNum, command, user, amount=amount)

		elif command == QUOTE:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transactionNum, command, user, stock_id)

		elif command == BUY:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)

		elif command == COMMIT_BUY:
			user = request[1]
			make_request(pid, transactionNum, command, user)
			
		elif command == CANCEL_BUY:
			user = request[1]
			make_request(pid, transactionNum, command, user)
			
		elif command == SELL:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)

		elif command == COMMIT_SELL:
			user = request[1]
			make_request(pid, transactionNum, command, user)

		elif command == CANCEL_SELL:
			user = request[1]
			make_request(pid, transactionNum, command, user)

		elif command == SET_BUY_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)
			
		elif command == CANCEL_SET_BUY:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transactionNum, command, user, stock_id)

			
		elif command == SET_BUY_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)

			
		elif command == SET_SELL_AMOUNT:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)

			
		elif command == SET_SELL_TRIGGER:
			user = request[1]
			stock_id = request[2]
			amount = request[3]
			make_request(pid, transactionNum, command, user, stock_id, amount)

			
		elif command == CANCEL_SET_SELL:
			user = request[1]
			stock_id = request[2]
			make_request(pid, transactionNum, command, user, stock_id)

			
		elif command == DUMPLOG:
			if len(request) == 2:
				#filename
				filename = request[1]
				make_request(pid, transactionNum, command, filename=filename)

			elif len(request) == 3:
				#userid, filename
				user = request[1]
				filename = request[2]
				make_request(pid, transactionNum, command, user, filename=filename)

		elif command == DISPLAY_SUMMARY:
			user = request[1]
			make_request(pid, transactionNum, command, user)


		else:
			# INVALID REQUEST
			print "invalid request: " + request[0]

#-----------------------------------------------------------------------------
#
def get_transaction_server(user):
	response = requests.post(url=web_server_authenticate, json={"username":user}).json()

	return response["tx_server"]


#-----------------------------------------------------------------------------
#
def worker(id):
	while True:
	    user = q.get()
	    process = get_transaction_server(user)
	    print process
	    # sendWorkload(user, process)
	    q.task_done()

#-----------------------------------------------------------------------------
# send_audit
# Send formatted message to the audit server
def send_audit(message):

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (AUDIT_SERVER_ADDRESS, AUDIT_SERVER_PORT)
	
	if __debug__:
		print 'connecting to ' + AUDIT_SERVER_ADDRESS + ' port ' + str(AUDIT_SERVER_PORT) + '\n'
		
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
	
#-----------------------------------------------------------------------------
# audit_event
# Format message to send to the audit server
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

	message = {"logtype" : "invalid"}

	if type == "command":
		message = {
			"logType": "UserCommandType",
			"timestamp": timestamp,
			"server" : MY_NAME,
			"transactionNum" : transactionNum,
			"command" : command
		}

		if username:
			message["username"] = username

		if stockSymbol:
			message["stockSymbol"] = stockSymbol

		if filename:
			message["filename"] = filename

		if funds:
			message["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(int(funds%100))

	elif type == "error":
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
	else:
		pass

	if message.get('logtype') != 'invalid':
		while threading.active_count() > MAX_THREADS:
			pass
		t = threading.Thread(target=send_audit, args=(message,))
		t.start()
	#send_audit(str(message))
	
	return


def main():
	userList = processWorkloadFile('/',working_dir, workload_file)
	yappi.start()
	for i in range(NUM_WORKER_THREADS):
		t = Thread(target=worker, args=(i,))
		t.daemon = True
		t.start()

	i=0
	for item in userList:
		if workload_id == 0 and i<int(user_count/2):
			q.put(item)
		elif workload_id == 1 and i>=int(user_count/2):
			q.put(item)
		i = i + 1

	q.join() #blocks until everything is done
	# then send last command
	if workload_id == 0:
	    sendWorkload("last", 0)

	yappi.get_func_stats().print_all()
	yappi.get_thread_stats().print_all()

if __name__ == "__main__":
    main()
