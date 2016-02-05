import socket
import sys
import io
from thread import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 44421 # Arbitrary non-privileged port
 
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
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
	#this is where all the logic for logging will go.
        data = conn.recv(1024)
	#handle request here
        if not data: 
            break
	#this function call handles the data package and returns ok or asks for a resend.
	status = handleEntry(data)     

	#if the data is handled ok, send back an ok, otherwise request a resend
	if(status=='OK'):
	    reply = 'OK'
	else:
	   reply = "ERROR"
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


## This function handles the data package recieved thru the socket and dumps it into the audit log
def handleEntry(strdict):
    xmlPacket = ''

    #unpack string into dictionary
    entryDict = ast.literal_eval(strdict)
    
    #based on source parse the dict into an xml string and add it to the log
    logType = entryDict['logType']
   
    #based on log type call the appropriate function to generate xml packet
    if(logType == "userCommandType"):
	xmlPacket = parseUserCommand(entryDict)
    elif(logType == "quoteServerType"):
	xmlPacket = pareseQuoteServer(entryDict)
    elif(logType == "accountTransactionType"):
	xmlPacket = parseAccountTransaction(entryDict)
    elif(logType == "systemEventType"):
	xmlPacket = parseSystemEvent(entryDict)
    elif(logType == "errorEventType"):
	xmlPacket = parseErrorEvent(entryDict)
    elif(logType == "DebugType"):
	xmlPacket = parseDebug(entryDict)
    else:
	#unknown log type ?throw an error?

    #open log file to append to, may need to put this in a try block
    f = open('logfile.xml', 'a')     
    



##USER COMMAND TYPE
def parseUserCommand(entryDict):
#inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    command = entryDict['command']
    userName = entryDict.get('username', default='')
    stockSymbol = entryDict.get('stockSymbol', default='')
    filename = entryDict.get('filename', default='')
    funds = entryDict.get('funds', default='')

    userCommandType = ''
    userCommandType += '<userCommand>'
    userCommandType += '<timestamp>' + timeStamp + '</timestamp>'
    userCommandType += '<server>' + server + '</server>'
    userCommandType += '<transactionNum>' + transactionNum +'< /transactionNum>'
    userCommandType += '<command>' + command + '</command>'
    userCommandType += '<username>' + userName + '</username>'
    userCommandType += '<stockSymbol>' + stockSymbol + '</stockSymbol>'
    userCommandType += '<filename>' + filename + '</filename>'
    userCommandType += '<funds>' + funds + '</funds>'
    userCommandType += '</userCommand>'

    return userCommandType



##QUOTE SERVER TYPE
def pareseQuoteServer(entryDict):
#inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    price = entryDict['price']
    stockSymbol = entryDict['stockSymbol']
    userName = entryDict['username']
    quoteServerTime = entryDict['quoteServerTime']
    cryptokey = entryDict['cryptokey']

    quoteServerType = ''
    quoteServerType += '<quoteServer>'
    quoteServerType += '<timestamp>' + timeStamp + '</timestamp>'
    quoteServerType += '<server>' + server + '</server>'
    quoteServerType += '<transactionNum>' + transactionNum + '</transactionNum>'
    quoteServerType += '<quoteServerTime>' + quoteServerTime + '</quoteServerTime>'
    quoteServerType += '<username>' + userName + '</username>'
    quoteServerType += '<stockSymbol>' + stockSymbol + '</stockSymbol>'
    quoteServerType += '<price>' + price + '</price>'
    quoteServerType += '<cryptokey>' + cryptokey + '</cryptokey>'
    quoteServerType += '</quoteServer>'

    return quoteServerType



##Account Transaction Type
def parseAccountTransaction(entryDict):
#inputs
	timeStamp = entryDict['timestamp']
	server = entryDict['server']
	transactionNum = entryDict['transactionNum']
	action = entryDict['action']
	userName = entryDict['username']
	funds = entryDict['funds']

	accountTransactionType = ''
	accountTransactionType += '<accountTransaction>'
	accountTransactionType += '<timestamp>' + timeStamp + '</timestamp>'
	accountTransactionType += '<server>' + server + '</server>'
	accountTransactionType += '<transactionNum>' + transactionNum + '</transactionNum>'
	accountTransactionType += '<action>' + action + '</action>'
	accountTransactionType += '<username>' + userName + '</username>'
	accountTransactionType += '<funds>' + funds + '</funds>'
	accountTransactionType += '</accountTransaction>'

	return accountTransactionType

##System Event Type
def parseSystemEvent(entryDict):
#inputs
	timeStamp = entryDict['timestamp']
        server = entryDict['server']
        transactionNum = entryDict['transactionNum']
        command = entryDict['command']
	userName = entryDict.get('username', default='')
	stockSymbol = entryDict.get('stockSymbol', default='')
	fileName = entryDict.get('filename', default='')
	funds = entryDict.get('funds', default='')

	systemEventType = ''
	systemEventType += '<systemEvent>'
	systemEventType += '<timestamp>' + timeStamp + '</timestamp>'
	systemEventType += '<server>' + server + '</server>'
	systemEventType += '<transactionNum>' + transactionNum + '</transactionNum>'
	systemEventType += '<command>' + command + '</command>'
	systemEventType += '<username>' + userName + '</username>'
	systemEventType += '<stockSymbol>' + stockSymbol + '</stockSymbol>'
	systemEventType += '<funds>' + funds + '</funds>'
	systemEventType += '</systemEvent>'

	return systemEventType


##Error Event Type
def parseErrorEvent(entryDict)
#inputs
	timeStamp = entryDict['timestamp']
	server = entryDict['server']
        transactionNum = entryDict['transactionNum']
        command = entryDict['command']
	userName = entryDict.get('username', default='')
	stockSymbol = entryDict.get('stockSymbol', default='')
	fileName = entryDict.get('filename', default='')
	funds = entryDict.get('funds', default='')
	errorMessage = entryDict.get('errorMessage', default='')

	errorEventType = ''
	errorEventType += '<errorEvent>'
	errorEventType += '<timestamp>' + timeStamp + '</timestamp>'
	errorEventType += '<server>' + server + '</server>'
	errorEventType += '<transactionNum>' + transactionNum + '</transactionNum>'
	errorEventType += '<command>' + command + '</command>'
	errorEventType += '<username>' + userName + '</username>'
	errorEventType += '<stockSymbol>' + stockSymbol + '</stockSymbol>'
	errorEventType += '<funds>' + funds + '</funds>'
	errorEventType += '<errorMessage>' + errorMessage + '</errorMessage>'
	errorEventType += '</errorEvent>'
	
	return errorEventType

'''
##Debug Type
#inputs
timeStamp = ''
server = ''
transactionNum = ''
command = ''
userName = ''
stockSymbol = ''
fileName = ''
funds = ''
debugMessage = ''

DebugType = ''
DebugType += '<debugEvent>'
DebugType += '<timestamp>' + timeStamp + '</timestamp>'
DebugType += '<server>' + server + '</server>'
DebugType += '<transactionNum>' + transactionNum + '</transactionNum>'
DebugType += '<command>' + command + '</command>'
DebugType += '<username>' + userName + '</username>'
DebugType += '<stockSymbol>' + stockSymbol + '</stockSymbol>'
DebugType += '<funds>' + funds + '</funds>'
DebugType += '<debugMessage>' + errorMessage + '</debugMessage>'
DebugType += '</debugEvent>'

'''
