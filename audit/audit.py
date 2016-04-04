import ast
import socket
import sys
import io
import time
import threading

from thread import *
 

if(len(sys.argv)==2):
    audit_id = sys.argv[1]
else:
   # audit id 0 is the master
   audit_id = 0 


# Symbolic name meaning all available interfaces
HOST = ''
# Arbitrary non-privileged port
PORT = 44421 
#logfile name
logfile = "logfile_" + str(audit_id) + ".xml"
#string to hold staging logs
staging_logs = ""
#lock for appending logs
audit_lock = threading.Semaphore(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

########## THIS STUFF IS INTRODUCED FOR KEEPING THE STUFF IN MEMORY ###########
''' ONLY HERE FOR DICT FORMATTING
    audit_dict = {
        "user": "xmlchunk",

    }

    audit_dict[user] += xmlpacket
'''
audit_dict = { 'system': ''}

###############################################################################


print 'Socket created'
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(200)
print 'Socket now listening'




###USER COMMAND TYPE
def parseUserCommand(entryDict):
#inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    command = entryDict['command']
    userName = entryDict.get('username', "")
    stockSymbol = entryDict.get('stockSymbol', "")
    fileName = entryDict.get('filename', "")
    funds = entryDict.get('funds', "")

    userCommandType = ''
    userCommandType += '<userCommand>\n'
    userCommandType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    userCommandType += '    <server>' + server + '</server>\n'
    userCommandType += '    <transactionNum>' + str(transactionNum) +'</transactionNum>\n'
    userCommandType += '    <command>' + command + '</command>\n'
    if (userName!=""):
        userCommandType += '    <username>' + userName + '</username>\n'
    if (stockSymbol!=""):
        userCommandType += '    <stockSymbol>' + stockSymbol + '</stockSymbol>\n'
    if (fileName!=""):
        userCommandType += '    <filename>' + fileName + '</filename>\n'
    if (funds!=""):
        userCommandType += '    <funds>' + str(funds) + '</funds>\n'
    userCommandType += '</userCommand>\n'

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
    quoteServerType += '<quoteServer>\n'
    quoteServerType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    quoteServerType += '    <server>' + server + '</server>\n'
    quoteServerType += '    <transactionNum>' + str(transactionNum) + '</transactionNum>\n'
    quoteServerType += '    <quoteServerTime>' + str(quoteServerTime) + '</quoteServerTime>\n'
    quoteServerType += '    <username>' + userName + '</username>\n'
    quoteServerType += '    <stockSymbol>' + stockSymbol + '</stockSymbol>\n'
    quoteServerType += '    <price>' + str(price) + '</price>\n'
    quoteServerType += '    <cryptokey>' + cryptokey + '</cryptokey>\n'
    quoteServerType += '</quoteServer>\n'

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
    accountTransactionType += '<accountTransaction>\n'
    accountTransactionType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    accountTransactionType += '    <server>' + server + '</server>\n'
    accountTransactionType += '    <transactionNum>' + str(transactionNum) + '</transactionNum>\n'
    accountTransactionType += '    <action>' + action + '</action>\n'
    accountTransactionType += '    <username>' + userName + '</username>\n'
    accountTransactionType += '    <funds>' + str(funds) + '</funds>\n'
    accountTransactionType += '</accountTransaction>\n'

    return accountTransactionType

##System Event Type
def parseSystemEvent(entryDict):
#inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    command = entryDict['command']
    userName = entryDict.get('username', "")
    stockSymbol = entryDict.get('stockSymbol', "")
    fileName = entryDict.get('filename', "")
    funds = entryDict.get('funds', "")

    systemEventType = ''
    systemEventType += '<systemEvent>\n'
    systemEventType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    systemEventType += '    <server>' + server + '</server>\n'
    systemEventType += '    <transactionNum>' + str(transactionNum) + '</transactionNum>\n'
    systemEventType += '    <command>' + command + '</command>\n'
    if (userName!=""):
        systemEventType += '    <username>' + userName + '</username>\n'
    if (stockSymbol!=""):
        systemEventType += '    <stockSymbol>' + stockSymbol + '</stockSymbol>\n'
    if (fileName!=""):
        systemEventType += '    <filename>' + fileName + '</filename>\n'
    if (funds!=""):
        systemEventType += '    <funds>' + str(funds) + '</funds>\n'
    systemEventType += '</systemEvent>\n'

    return systemEventType


##Error Event Type
def parseErrorEvent(entryDict):
    #inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    command = entryDict['command']
    userName = entryDict.get('username', "")
    stockSymbol = entryDict.get('stockSymbol', "")
    fileName = entryDict.get('filename', "")
    funds = entryDict.get('funds', "")
    errorMessage = entryDict.get('errorMessage', "")

    errorEventType = ''
    errorEventType += '<errorEvent>\n'
    errorEventType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    errorEventType += '    <server>' + server + '</server>\n'
    errorEventType += '    <transactionNum>' + str(transactionNum) + '</transactionNum>\n'
    errorEventType += '    <command>' + command + '</command>\n'
    if (userName!=""):
        errorEventType += '    <username>' + userName + '</username>\n'
    if (stockSymbol!=""):
        errorEventType += '    <stockSymbol>' + stockSymbol + '</stockSymbol>\n'
    if (fileName!=""):
        errorEventType += '    <filename>' + fileName + '</filename>\n'
    if (funds!=""):
        errorEventType += '    <funds>' + str(funds) + '</funds>\n'
    if (errorMessage!=""):
        errorEventType += '    <errorMessage>' + errorMessage + '</errorMessage>\n'
    errorEventType += '</errorEvent>\n'
    
    return errorEventType

##Debug Type
def parseDebug(entryDict):
    #inputs
    timeStamp = entryDict['timestamp']
    server = entryDict['server']
    transactionNum = entryDict['transactionNum']
    command = entryDict['command']
    userName = entryDict.get('username', "")
    stockSymbol = entryDict.get('stockSymbol', "")
    fileName = entryDict.get('filename', "")
    funds = entryDict.get('funds', "")
    debugMessage = entryDict.get('debugMessage', "")

    DebugType = ''
    DebugType += '<debugEvent>\n'
    DebugType += '    <timestamp>' + str(timeStamp) + '</timestamp>\n'
    DebugType += '    <server>' + server + '</server>\n'
    DebugType += '    <transactionNum>' + str(transactionNum) + '</transactionNum>\n'
    DebugType += '    <command>' + command + '</command>\n'
    if (userName!=""):
        DebugType += '    <username>' + userName + '</username>\n'
    if (stockSymbol!=""):
        DebugType += '    <stockSymbol>' + stockSymbol + '</stockSymbol>\n'
    if (fileName!=""):
        DebugType += '    <filename>' + fileName + '</filename>\n'
    if (funds!=""):
        DebugType += '    <funds>' + str(funds) + '</funds>\n'
    if (debugMessage!=""):
        DebugType += '    <debugMessage>' + debugMessage + '</debugMessage>\n'
    DebugType += '</debugEvent>\n'
    
    return DebugType
# This function handles the data package recieved thru the socket and dumps it into the audit log
def handleEntry(strdict):
    global staging_logs
    xmlPacket = ''
    #print strdict
    #unpack string into dictionary
    entryDict = ast.literal_eval(strdict)
    
    '''
    detect if its a user dumplog then call fetchUserLog
        return fetchUserLog()
    '''


    #based on source parse the dict into an xml string and add it to the log
    logType = entryDict['logType']
   
    #based on log type call the appropriate function to generate xml packet
    if(logType == "UserCommandType"):
        xmlPacket = parseUserCommand(entryDict)
    elif(logType == "QuoteServerType"):
        xmlPacket = pareseQuoteServer(entryDict)
    elif(logType == "AccountTransactionType"):
        xmlPacket = parseAccountTransaction(entryDict)
    elif(logType == "SystemEventType"):
        xmlPacket = parseSystemEvent(entryDict)
    elif(logType == "ErrorEventType"):
        xmlPacket = parseErrorEvent(entryDict)
    elif(logType == "DebugType"):
        xmlPacket = parseDebug(entryDict)
    else:
        print "unknown log type"
        return "UNKNOWN_LOG_TYPE"
    #unknown log type ?throw an error?
    
    #aquire audit lock and append the string

    '''ORIGINAL CODE
    audit_lock.acquire()
    staging_logs = staging_logs + xmlPacket
    audit_lock.release()
    '''
    if 'username' in entryDict:
        if entryDict['username'] in audit_dict:
            audit_dict[entryDict['username']] += xmlPacket
        else:
            audit_dict[entryDict['username']] = xmlPacket

    else:
        audit_dict['system'] += xmlPacket

    return "OK"

def fetchUserLog(username):
    if username in audit_dict:
        return audit_dict[username]
    else:
        return "No existing logs for that user"

def writerthread():
    global staging_logs
    while True:
        #get the lock and copy the staging logs
        audit_lock.acquire()
        to_be_logged = staging_logs
        staging_logs = ""
        audit_lock.release()

        #write all staging audits to the logfile then sleep for a second
        if(to_be_logged):
            f = open(logfile, 'a')
            f.write(to_be_logged)
            f.close()
        time.sleep(1)


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
    #this function call handles the data package and returns ok or gives an unknown log error
        reply = handleEntry(data) 
        conn.sendall(reply)
        conn.close()
        sys.exit(0) 

    #came out of loop
    print "Ending transmission"
    conn.close()
    #sys.exit(0) 


def dumpLog():
    f = open(logfile, 'a')
    f.write('<?xml version="1.0"?>\n<log>\n')
    for entry in audit_dict:
        f.write(audit_dict[entry])

    f.write("</log>")

#now keep talking with the client
'''
if(audit_id==0):
    f = open(logfile, 'a')
    f.write('<?xml version="1.0"?>\n<log>\n')
    f.close()

start_new_thread(writerthread,())
'''
while 1:
    try:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
         
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,))
    except:
        if(audit_id==0):
            '''
            f = open(logfile, 'a')
            f.write("</log>")
            f.close()
            '''
            dumpLog()
        sys.exit(0) 

s.close()
