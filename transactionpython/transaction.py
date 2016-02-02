#!/usr/bin/python
import os
import socket
import string
import sys

host = 'b142.seng.uvic.ca'
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
			conn.send('Squawk: ' + data)
		else:
			break