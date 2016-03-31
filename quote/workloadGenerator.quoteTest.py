import io
import socket
import sys
import string
import ast
import threading
import Queue
import time


MAX_WORKERS = 100

target_server_address = 'b132.seng.uvic.ca'
target_server_port = 44420

out_queue = Queue.Queue()

def make_request():

	while True:

		data = out_queue.get()

		#if __debug__:
		#	print "Transaction number: " + data['transactionNum'] + "\n"
		#	print "Req: " + data['user'] + "," + data['stock_id'] + " - " + data['command'] + "\n"
		#	print "Recv: " + response['user'] + "," + response['stock_id'] + " - " + response['price'] + " [" + response['timestamp'] + "]\n\n"

		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect the socket to the port where the server is listening
		server_address = (target_server_address, target_server_port)
	
		sock.connect(server_address)
		sock.sendall(str(data))
		response = sock.recv(1024)
		response = ast.literal_eval(response)
		sock.close()

		out_queue.task_done()
		print out_queue.qsize()

#end make_request

def feeder():
	bad_chars = '[]'
	f = open("activeWorkLoad.txt", 'r')
	for line in f:
		tokens = line.split(' ')

		transaction_id = tokens[0]
		transaction_id = transaction_id.translate(None, bad_chars)

		request = tokens[1].split(',')

		request_type = request[0].upper()

		if request_type == 'QUOTE' or request_type == 'BUY' or request_type == 'SELL':
			request_d = "{\'stock_id\':\'"+request[2]+"\'"
			request_d += ",\'user\':\'"+request[1]+"\'"
			request_d += ",\'transactionNum\':\'"+transaction_id+"\'"
			request_d += ",\'command\':\'"+request_type+"\'}"

			out_queue.put(request_d)
			print transaction_id

			if out_queue.qsize() > 500:
				time.sleep(1)
			elif out_queue.qsize() > 200:
				time.sleep(0.005)

		else:
			# INVALID REQUEST
			#print "invalid request: " + request[0]
			pass

def main():
	for i in range(1, MAX_WORKERS):
		t_id = threading.Thread(target=make_request, args=())
		t_id.daemon = True
		t_id.start()
		print "Starting " + str(t_id)

	t = threading.Thread(target=feeder, args=())
	t.daemon = True
	t.start()

	t.join()


if __name__ == "__main__":
    main()
