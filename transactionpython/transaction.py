#!/usr/bin/python
import os
import socket
import string
import sys
import ast

def process_request(data):
	print "Gonna do some shit with this:"
	print data
	data_dict = ast.literal_eval(data)
	for key, value in data_dict.iteritems():
		print key + " is " + value + "\n"
	result = ""
	if data_dict["request_type"] == "BUY":
		print "holy moly its a buy"
	elif data_dict["request_type"] == "QUOTE":
		result = get_quote(data_dict)
	return result

def get_quote(data):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('quoteserve.seng.uvic.ca', 4445))
	s.send(data['user'])
	response = s.recv(1024)
	print response
	s.close
	return response




host = ''
port = 44421
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
counter = 0

while 1:
	print 'Main: waiting\n'
	s.listen(1)
	conn, addr = s.accept()
	print 'Connection from ' + addr[0] + '\n'
	
	while 1:
		data = conn.recv(1024)
		if (data):
			print 'Received: ' + data
			conn.send('Received OK')
			process_request(data)
		else:
			break