#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
 
#create an INET, STREAMing socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
     
print 'Socket Created'
 
host = '';
port = 50000;
 
try:
    remote_ip = socket.gethostbyname( host )
 
except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()
 
#Connect to remote server
s.connect((remote_ip , port))
 
print 'Socket Connected to ' + host + ' on ip ' + remote_ip
 
#this is a continuous loop but it should use a variable that gets changed when there is an OK from server
#once the server gives the ok the connection should be closed
while(True):
	#Send some data to remote server
	#format string to send to server here
	message = raw_input(">>") 
	try :
	    #Set the whole string
	    s.sendall(message)
	except socket.error:
	    #Send failed
	    print 'Send failed'
	    sys.exit()
	 
	 
	#Now receive data
	reply = s.recv(4096)
	 
	print reply
