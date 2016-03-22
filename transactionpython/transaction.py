#!/usr/bin/python
import ast
import os
import socket
import string
import sys
import time
from thread import *
from threading import Thread, current_thread, activeCount

from database import Database

server_name = "transaction_server_1"
sever_id = 1

web_server_address = 'b132.seng.uvic.ca' # Workload Generator

audit_server_address = ['b149.seng.uvic.ca', 'b153.seng.uvic.ca']
audit_server_port = 44421

cache_server_address = ['b143.seng.uvic.ca', 'b144.seng.uvic.ca', 'b145.seng.uvic.ca']
cache_server_port = 44420

SELF_HOST = ''
SELF_PORT = 44422

MAX_THREADS = 10

# Commands
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


def now():
    return int(time.time() * 1000)

def send_audit_entry(message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (audit_server_address[server_id%2], audit_server_port)
    sock.connect(server_address)

    try:
        sock.sendall(message)
        response = sock.recv(1024)

    finally:
        sock.close()

    return

def audit_user_command_event(
        timestamp, 
        server, 
        transactionNum, 
        command, 
        username="", 
        stockSymbol="", 
        filename="", 
        funds=0):

    audit_dict = {
        "logType": "UserCommandType",
        "timestamp": timestamp,
        "server": server,
        "transactionNum": transactionNum,
        "command": command,
    }
    if username:
        audit_dict["username"] = username

    if stockSymbol:
        audit_dict["stockSymbol"] = stockSymbol

    if filename:
        audit_dict["filename"] = filename

    if funds:
        audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(int(funds%100))
    
    send_audit_entry(str(audit_dict))

    return

def audit_quote_server_event(
        timestamp,
        server,
        transactionNum,
        price,
        stockSymbol,
        username,
        quoteServerTime,
        cryptokey):
    
    audit_dict = {
        "logType": "QuoteServerType",
        "timestamp": timestamp,
        "server": server,
        "transactionNum": transactionNum,
        "price": str(price),
        "stockSymbol": stockSymbol,
        "username": username,
        "quoteServerTime": quoteServerTime,
        "cryptokey": cryptokey,
    }

    send_audit_entry(str(audit_dict))

    return

def audit_transaction_event(
        timestamp,
        server,
        transactionNum,
        action,
        username,
        funds):

    audit_dict = {
        "logType": "AccountTransactionType",
        "timestamp": timestamp,
        "server": server,
        "transactionNum": transactionNum,
        "action": action,
        "username": username,
        "funds" : str(int(funds/100)) + '.' + "{:02d}".format(int(funds%100))
    }

    # send_audit_entry(str(audit_dict))

    return
    
def audit_system_event(
        timestamp,
        server,
        transactionNum,
        command,
        username="",
        stockSymbol="",
        filename="",
        funds=0):

    audit_dict = {
        "logType": "SystemEventType",
        "timestamp": timestamp,
        "server": server,
        "transactionNum": transactionNum,
        "command": command,
    }

    if username:
        audit_dict["username"] = username

    if stockSymbol:
        audit_dict["stockSymbol"] = stockSymbol

    if filename:
        audit_dict["filename"] = filename

    if funds:
        audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(int(funds%100))
    
    # send_audit_entry(str(audit_dict))

    return

def audit_error_event(
        timestamp,
        server,
        transactionNum=None,
        command=None,
        username=None,
        stockSymbol=None,
        filename=None,
        funds=None,
        errorMessage=None):

    audit_dict = {
        "logType": "ErrorEventType",
        "timestamp": timestamp,
        "server": server
    }

    if transactionNum:
        audit_dict["transactionNum"] = transactionNum

    if command:
        audit_dict["command"] = command

    if username:
        audit_dict["username"] = username

    if stockSymbol:
        audit_dict["stockSymbol"] = stockSymbol

    if filename:
        audit_dict["filename"] = filename

    if funds: 
        audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(int(funds%100))

    if errorMessage:
        audit_dict["errorMessage"] = errorMessage
    
    # send_audit_entry(str(audit_dict))

    return

def audit_debug(
        timestamp,
        server,
        transactionNum=None,
        command=None,
        username="",
        stockSymbol="",
        filename="",
        funds=0,
        debugMessage=""):

    audit_dict = {
        "logType": "DebugType",
        "timestamp": timestamp,
        "server": server
    }

    if transactionNum:
        audit_dict["transactionNum"] = transactionNum

    if command:
        audit_dict["command"] = command

    if username:
        audit_dict["username"] = username

    if stockSymbol:
        audit_dict["stockSymbol"] = stockSymbol

    if filename:
        audit_dict["filename"] = filename

    if funds: 
        audit_dict["funds"] = str(int(float(funds)/100)) + '.' + "{:02d}".format(int(funds%100))
        

    if debugMessage:
        audit_dict["debugMessage"] = debugMessage
    
    # send_audit_entry(str(audit_dict))

    return

def process_request(data, conn):
    # Convert Data to Dict
    data_dict = ast.literal_eval(data)

    response = "Request not processed."
    transactionNum = data_dict.get('transactionNum')
    command = data_dict.get('command')
    user = data_dict.get('user')
    stock_id = data_dict.get('stock_id')
    filename = data_dict.get('filename')
    amount = data_dict.get('amount')
    if amount:
        amount = int(float(amount) * 100)

    # -- DEBUG: store event in audit regardless of correctness
    if __debug__:
        audit_debug(
            now(),
            server_name,
            transactionNum,
            command,
            user,
            stock_id,
            filename,
            amount,
            "Storing command before processing."
        )


# ---------------------------------------------------------
# Begin processing request
# ---------------------------------------------------------

    # -- Check for transaction id and request type
    if transactionNum is None:
        response = "Missing transaction id. Transaction ignored."
        audit_error_event(
            now(),
            server_name,
            transactionNum,
            command,
            user,
            stock_id,
            filename,
            amount,
            response
        )
    else:

        if command is None:
            response = "Missing request command. Transaction ignored."
            audit_error_event(
                now(),
                server_name,
                transactionNum,
                command,
                user,
                stock_id,
                filename,
                amount,
                response
            )
        else:

            if user:
                balance = conn.select_record("balance", "Users", "user_id='%s'" % user)[0]
                if balance == None:
                    conn.insert_record("Users", "user_id,balance", "'%s',%d" % (user,0))
                    balance = 0

            # Store request before processing
            audit_user_command_event(
                now(),
                server_name,
                transactionNum,
                command,
                user,
                stock_id,
                filename,
                amount
            )

# --------------
# -- ADD REQUEST
# --------------
            if command == ADD:
                if amount is None:
                    response = "Amount not specified."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response
                    )
                elif amount < 0:
                    response = 'Attempting to add a negative amount.' 
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response
                    )
                else:
                    conn.update_record("Users", "balance=balance+%d" % amount, "user_id='%s'" % user)
                    response = "Added."

                    audit_transaction_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        balance + amount
                    )

# ----------------
# -- QUOTE REQUEST
# ----------------
            elif command == QUOTE:
                current_quote = get_quote(data_dict)
                response = str(stock_id) + ':' + str(current_quote['price'])

# --------------
# -- BUY REQUEST
# --------------
            elif command == BUY:

                # Check user balance
                if conn.select_record("balance", "Users", "user_id='%s'" % user)[0] >= amount:
                
                    if __debug__:
                        audit_debug(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            'Sending quote request')

                    current_quote = get_quote(data_dict)

                    price = current_quote["price"]
                    timestamp = int(current_quote["timestamp"])
            
                    # Set pending buy to new values (should overwrite existing entry)
                    conn.update_record("PendingTrans", "stock_id='%s',amount=%d,timestamp=%d" % (stock_id, amount, timestamp), "user_id='%s'" % user)
                    
                    response = str(stock_id) + ":" + str(price)

                else:
                    response = "Insufficient funds in account to place buy order."

# ---------------------
# -- COMMIT BUY REQUEST
# ---------------------
            elif command == COMMIT_BUY: 
                # Check if timestamp is still valid
                pending_buy = conn.select_record("timestamp,amount,stock_id", "PendingTrans", "type='buy' AND user_id='%s'" % user)
                if pending_buy[0]:
                    if now() - 60000 <= int(pending_buy[0]):
                        amount = pending_buy[1]
                        stock_id = pending_buy[2]
                
                        # Update user balance
                        conn.update_record("Users", "balance=balance-%d" % amount, "user_id='%s'" % user)

                        # Create or update stock entry for user
                        stock = conn.select_record("amount", "Stock", "stock_id='%s' AND user_id='%s'" % (stock_id, user))
                        if stock[0] != None:
                            conn.update_record("Stock", "amount=amount+%d" % amount, "stock_id='%s' AND user_id='%s'" % (stock_id, user))
                        else:
                            conn.insert_record("Stock", "stock_id,user_id,amount", "%s,%s,%d" % (stock_id, user, amount))
                            
                        audit_transaction_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            amount)
                
                        # Remove the pending entry
                        conn.delete_record("PendingTrans", "type='buy' AND user_id='%s'" % user)

                        response = "Last buy order committed."
                        
                    else:
                        response = "Time elapsed. Commit buy cancelled."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            None,#stock
                            None,#filename
                            None,#amount
                            response)
                else:
                    response = "No buy order in place. Commit buy cancelled."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        None,#stock
                        None,#filename
                        None,#amount
                        response)
                        

# ---------------------
# -- CANCEL BUY REQUEST
# ---------------------
            elif command == CANCEL_BUY:
                conn.delete_record("PendingTrans", "type='buy' AND user_id='%s'" % user)
                response = "Buy cancelled."
                
# ---------------
# -- SELL REQUEST
# ---------------
            elif command == SELL:
                # Check user stock amount
                if amount > 0:
                    if conn.select_record("amount", "Stock", "user_id='%s' AND stock_id='%s'" % (user, stock_id))[0] >= amount:

                        if __debug__:
                            audit_debug(
                                now(),
                                server_name,
                                transactionNum,
                                command,
                                user,
                                stock_id,
                                None,#filename
                                amount,
                                'Sending quote request')

                        current_quote = get_quote(data_dict)
                        price = current_quote["price"]
                        timestamp = int(current_quote["timestamp"])
                        
                        if conn.select_record("amount", "PendingTrans", "type='sell' AND user_id='%s'" % user)[0]:
                            conn.update_record("PendingTrans", "stock_id,amount,timestamp", "'%s',%d,'%s'" % (stock_id, amount, timestamp), "user_id='%s' AND type='sell'" % user)
                        else:
                            conn.insert_record("PendingTrans", "type,user_id,stock_id,amount,timestamp", "'sell','%s','%s',%d,'%s'" % (user,stock_id,amount,timestamp))
                        response = str(stock_id) + ":" + str(price)

                    else:
                        response = "Insufficient stock owned."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                else:
                    response = "Attempt to sell 0 or fewer shares."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)
                    
# ----------------------
# -- COMMIT SELL REQUEST
# ----------------------
            elif command == COMMIT_SELL:
                pending_sell = conn.select_record("timestamp,amount,stock_id", "PendingTrans", "type='sell' AND user_id='%s'" % user)
                if pending_sell[0]:
                    if now() - 60000 <= int(pending_sell[0]):
                        amount = pending_sell[1]
                        stock_id = pending_sell[2]

                        # Update user stock value
                        conn.update_record("Stock", "amount=amount-%d" % amount, "stock_id='%s' AND user_id='%s'" % (stock_id, user_id))
                
                        # Update user balance
                        conn.update_record("Users", "balance=balance+%d" % amount, "user_id='%s'" % user)
                        
                        audit_transaction_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            amount
                        )
                
                        # Remove the pending entry
                        conn.delete_record("PendingTrans", "user_id='%s' AND type='sell'" % user)
                
                        response = "Sell committed."
                    else:
                        response = "TIME WINDOW ELAPSED"
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            None,#stock
                            None,#filename
                            None,#amount
                            response)
                else:
                    response = 'No sale pending.'
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        None,#stock
                        None,#filename
                        None,#amount
                        response)
                    
# ----------------------
# -- CANCEL SELL REQUEST
# ----------------------
            elif command == CANCEL_SELL:
                conn.delete_record("PendingTrans", "type='sell' AND user_id='%s'" % user)
                response = "Sell cancelled."
                
# -------------------------
# -- SET BUY AMOUNT REQUEST
# -------------------------
            elif command == SET_BUY_AMOUNT:
            
                # Check user balance\
                if conn.select_record("balance", "Users", "user_id='%s'" % user)[0] >= amount:
                    if conn.select_record("*", "Trigger", "type='buy' AND user_id='%s' AND stock_id='%s'" % (user, stock_id)):
                        response = "Trigger already set for stock."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                    else:
                        # Update user balance
                        conn.update_record("Users", "balance=balance-%d" % amount, "user_id='%s'" % user)
                        
                        audit_transaction_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            amount
                        )
            
                        # Set up buy trigger with stock and amount to spend
                        conn.insert_record("Trigger", "type,user_id,stock_id,amount,trigger", "'buy','%s','%s',%d,%d" % (user,stock_id,amount,0))
                else:
                    response = "Insufficient funds to set trigger."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)
                    
# -------------------------
# -- CANCEL SET BUY REQUEST
# -------------------------
            elif command == CANCEL_SET_BUY:
                amount = conn.select_record("amount", "Trigger", "type='buy' AND user_id='%s' AND stock_id='%s'" % (user, stock_id))[0]
                if not amount:
                    #if there was no trigger
                    response = "No trigger listed for stock."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        None,#amount
                        response)
                else:
                    # put the money back into the user account
                    conn.delete_record("Trigger", "type='buy' AND user_id='%s' AND stock_id='%s'" % (user, stock_id))
                    conn.update_record("Users", "balance=balance+%d" % amount, "user_id='%s'" % user)   

                    audit_transaction_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        amount
                    )
                    
                    response = "Buy trigger cancelled."
                    #NOTE: trigger remains in cache, but is inactive - with a database the record can be deleted                    

# --------------------------
# -- SET BUY TRIGGER REQUEST - Maybe add a field to the database "last quote ttl"
# --------------------------
            elif command == SET_BUY_TRIGGER:
                # Stock should exist in buy trigger list, and have amount set, but no trigger value set
                buy_trigger = conn.select_record("amount,trigger", "Trigger", "type='buy' AND user_id='%s' AND stock_id='%s'" % (user,stock_id))
                if buy_trigger:
                    if buy_trigger[0] > 0:
                        if buy_trigger[1] == 0:
                            if amount > 0:
                                conn.update_record("Trigger", "trigger=%d" % amount, "type='buy' AND user_id='%s' AND stock_id='%s'" % (user,stock_id))
                                response = "Buy trigger set."
                            else:
                                response = "Cannot set trigger to buy at 0 or less."
                                audit_error_event(
                                    now(),
                                    server_name,
                                    transactionNum,
                                    command,
                                    user,
                                    stock_id,
                                    None,#filename
                                    amount,
                                    response)
                        else:
                            response = "Buy trigger already enabled for this stock."
                            audit_error_event(
                                now(),
                                server_name,
                                transactionNum,
                                command,
                                user,
                                stock_id,
                                None,#filename
                                amount,
                                response)
                                    
                    else:
                        response = "Buy trigger not initialized; Trigger not enabled."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                            
                else:
                    response = "No trigger set for stock."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)
                    
# --------------------------
# -- SET SELL AMOUNT REQUEST
# --------------------------
            elif command == SET_SELL_AMOUNT:
                sell_trigger = conn.select_record("amount,trigger", "Trigger", "type='sell' AND user_id='%s' AND stock_id='%s'" % (user, stock_id))
                if sell_trigger:
                    if conn.select_record("amount", "Stock", "user_id='%s' AND stock_id='%s'")[0] >= amount:
                        if sell_trigger[1] > 0:
                            response = "Active sell trigger for stock."
                            audit_error_event(
                                now(),
                                server_name,
                                transactionNum,
                                command,
                                user,
                                stock_id,
                                None,#filename
                                amount,
                                response)
                        else:
                            conn.update_record("Stock", "amount=amount-%d" % amount, "stock_id='%s' AND user_id='%s'" % (stock_id,user))
                            
                            conn.update_record("Trigger", "amount=%d,trigger=%d" % (amount,0), "type='sell' AND user_id='%s' AND stock_id='%s'" % (user,stock_id))
                            response = "Sell trigger initialised."
                    else:
                        response = "Insufficient stock to set trigger."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                else:
                    response = "User does not own this stock."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)
                
# ---------------------------
# -- SET SELL TRIGGER REQUEST
# ---------------------------
            elif command == SET_SELL_TRIGGER:           
                sell_trigger = conn.select_record("amount", "Trigger", "user_id='%s' AND stock_id='%s' AND type='sell'" % (user, stock_id))
                if sell_trigger[0] != None:
                    if sell_trigger[0] > 0:
                        if amount > 0:
                            conn.update_record("Trigger", "amount=%d" % amount, "user_id='%s' AND stock_id='%s' AND type='sell'" % (user,stock_id))
                            cache["users"][user]["sell_trigger"][stock_id]["trigger"] = amount
                            response = "Sell trigger set."
                        else:
                            response = "Sell trigger amount is not a positive value; Trigger not enabled."
                            audit_error_event(
                                now(),
                                server_name,
                                transactionNum,
                                command,
                                user,
                                stock_id,
                                None,#filename
                                amount,
                                response)
                    else:
                        response = "Sell trigger not initialized; Trigger not enabled."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                else:
                    response = "Sell trigger not initialized; Trigger not enabled.\n"
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)
        
# --------------------------
# -- CANCEL SET SELL REQUEST - CHECK LOGIC - you might want to cancel a trigger
# -- that didn't get set up correctly. 
# --------------------------
            elif command == CANCEL_SET_SELL:
                sell_trigger = conn.select_record("trigger", "Trigger", "user_id='%s' AND stock_id='%s' AND type='sell'" % (user,stock_id))
                if sell_trigger[0] != None:
                    if sell_trigger[0] > 0:
                        conn.update_record("Stock", "amount=amount+%d" % amount, "stock_id='%s' AND user_id='%s'" % (stock_id,user))
                        conn.delete_record("Trigger", "type='sell' AND user_id='%s' AND stock_id='%s'" % (user,stock_id))
                        
                        response = "Sell trigger cancelled."
                    else:
                        response = "Sell trigger not active on this stock."
                        audit_error_event(
                            now(),
                            server_name,
                            transactionNum,
                            command,
                            user,
                            stock_id,
                            None,#filename
                            amount,
                            response)
                else:
                    response = "Sell trigger does not exist for this stock."
                    audit_error_event(
                        now(),
                        server_name,
                        transactionNum,
                        command,
                        user,
                        stock_id,
                        None,#filename
                        amount,
                        response)

# --------------------------
# -- DUMPLOG REQUEST
# --------------------------        
            elif command == DUMPLOG:
                    if filename is None:
                        print "No filename for dumplog command. Dump not performed.\n"
                    else:
                        #activate the dump on audit
                        print "Dump engaged. Honest.\n"

            elif command == DISPLAY_SUMMARY:
                print "TX Display Summary: %s" % str(conn.select_record("*", "Users", "user_id='%s'" % (user)))
        
            else:
                print "Invalid command.\n"

    return response

# Request a Quote from the quote server
# Values returned from function in the order the quote server provides
#
# Quote server response format:
#       price,stock,user,timestamp,cryptokey
#
# Note: function returns price in cents
#returns price of stock, doesnt do any checking.
# target_server_address and target_server_port need to be set globally or the function must be modified to recieve these values
def get_quote(data):

    #pull out stock ID to send to a given cache server
    stock_id = data.get('stock_id')

    #python string compare values a>z>A>Z>1>9>0
    #stock quotes only seem to be capital letters so we can trisection the alphabet
    # A-I, J-Q, R-Z


    if (stock_id <= "I"):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (cache_server_address[0], cache_server_port)
        
        sock.connect(server_address)
        sock.sendall(str(data))
        response = sock.recv(1024)
        response = ast.literal_eval(response)
        sock.close()
        return  response
    elif (stock_id <= "Q"):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (cache_server_address[1], cache_server_port)
        
        sock.connect(server_address)
        sock.sendall(str(data))
        response = sock.recv(1024)
        response = ast.literal_eval(response)
        sock.close()
        return  response
    else:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (cache_server_address[2], cache_server_port)
        
        sock.connect(server_address)
        sock.sendall(str(data))
        response = sock.recv(1024)
        response = ast.literal_eval(response)
        sock.close()
        return  response




def transactionWorkerthread(conn, db):
    #global active_threads
    while 1:
        data = conn.recv(1024)

        if (data):
            response = process_request(data, db)
            conn.send(response)

        else:
            break
    conn.close()
    #active_threads -= 1 
    sys.exit(1)



def main():
    # Initialize Database
    db = Database(
        host="b133.seng.uvic.ca",
        port="44429",
        dbname="transactiondb",
        dbuser="cusmith",
        dbpass="",
        minconn=1,
        maxconn=100,
    )
    db.initialize()
    #global active_threads
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SELF_HOST, SELF_PORT))
    s.listen(1)
    global MAX_THREADS
    while 1:
        try:
            threads_free = activeCount() < 10
            if(threads_free):
                conn, addr = s.accept()

                #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
                value = start_new_thread(transactionWorkerthread, (conn, db))

        except:
            print 'Recieved user interrupt'
            #sys.exit(0)
            #break
    s.close()



if __name__ == "__main__":
    main()
