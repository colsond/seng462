import socket
import sys
import io
from thread import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 50000 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    f = open('logfile.txt', 'a')     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
	#this is where all the logic for logging will go.
        data = conn.recv(1024)
        f.write(data+"\n")
	reply = 'Recieved: ' + data
	#handle request here
        if not data: 
            f.close()
            break
     
        conn.sendall(reply)
     
    #came out of loop
    print "Ending transmission"
    conn.close()
    sys.exit(0) 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()
