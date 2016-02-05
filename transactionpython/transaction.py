#!/usr/bin/python
import ast
import os
import socket
import string
import sys
import time

## Cache format:
## cache = {
##	"users": {
##		"user": {
##			"balance": 0,
##			"stocks": {},
##			"pending": {
##				"stock_id": "id",
##				"amount": 0,
##				"timestamp": 0,
##			},
##			"trigger_type": {
##				"stock_id": "id"{
##      		"amount": 0,
##					"trigger": 0
##				}
##			}
##		}
##	}
##}

# web_server_address = 'b132.seng.uvic.ca'
web_server_address = 'localhost'
web_server_port = 44421

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

def send_audit_entry(message):

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (audit_server_address, audit_sever_port)
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)

	try:
		sock.sendall(message)
		print >>sys.stderr, 'sent "%s"' % message
		response = sock.recv(1024)
		print >>sys.stderr, 'received "%s"' % response

	finally:
	    print >>sys.stderr, 'closing socket'
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
		audit_dict["funds"] = funds
	
	send_audit_entry(str(audit_dict))

	return

def audit_quote_server_event(
		timestamp,
		server,
		transactionNum,
		price,
		stockSymbol,
		username
		quoteServerTime,
		cryptokey):
	
	audit_dict = {
		"timestamp": timestamp,
		"server": server,
		"transactionNum": transactionNum,
		"price": price,
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
		"timestamp": timestamp,
		"server": server,
		"transactionNum": transactionNum,
		"action": action,
		"username": username,
		"funds": funds,
	}

	send_audit_entry(str(audit_dict))

	return
	
def audit_system_event(
		timestamp,
		server,
		transactionNum,
		command,
		username,
		stockSymbol,
		filename,
		funds):

	audit_dict = {
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
		audit_dict["funds"] = funds
	
	send_audit_entry(str(audit_dict))

	return

def audit_error_event(
		timestamp,
		server,
		transactionNum,
		command,
		stockSymbol,
		filename,
		funds
		errorMessage):

	audit_dict = {
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
		audit_dict["funds"] = funds

	if errorMessage:
		audit_dict["errorMessage"] = errorMessage
	
	send_audit_entry(str(audit_dict))

	return

def process_request(data, cache):
	# Convert Data to Dict
	data_dict = ast.literal_eval(data)

	# -- store userCommand in audit regardless of correctness
	
	response = "\n"
	request_type = data_dict.get("request_type")
	try:
		#dumplog doesn't require a userid
		user = data_dict.get("user")

	print data_dict
	if request_type:
		if user and user not in cache["users"]:
			cache["users"][user] = {
				"balance": 0,
				"stocks": {},
				"pending_buy": {},
				"pending_sell": {}
			}

		if request_type == ADD:
			amount = float(data_dict["amount"])
			if amount < 0:
				# -- store errorEvent in audit
				response = "Attempting to add a negative amount\n"
			else:
				cache["users"][user]["balance"] = cache["users"][user]["balance"] + amount
				response = "Added\n"
				# -- store accountTransaction in audit
		
		elif request_type == QUOTE:
			result = get_quote(data_dict)
			response = str(result)
			response += "\n"
			# -- store quoteServer in audit
			
		elif request_type == BUY:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]

			# Check user balance
			if cache["users"][user]["balance"] >= amount:
				# get quote and send to user to confirm
				result = get_quote(data_dict)
				result = str(result)
				result = result.split(',')
				response = "Stock: " + result[1] + "  Current price: " + result[0] + "\n"
				# -- store quoteServer in audit
				
				# Set pending buy to new values (should overwrite existing entry)
				cache["users"][user]["pending_buy"]["stock_id"] = stock_id
				cache["users"][user]["pending_buy"]["amount"] = amount
				cache["users"][user]["pending_buy"]["timestamp"] = int(time.time())
				response = "Please confirm your purchase within 60 seconds.\n"
				
			
		elif request_type == COMMIT_BUY: 
			# Check if timestamp is still valid
			if cache["users"][user]["pending_buy"]:
				if int(time.time()) - 60 <= cache["users"][user]["pending_buy"]["timestamp"]:
					
					# Get stock_id and amount from pending_buy entry
					amount = float(cache["users"][user]["pending_buy"]["amount"])
					stock_id = cache["users"][user]["pending_buy"]["stock_id"]

					# Create or update stock entry for user
					if stock_id not in cache["users"][user]["stocks"]:
						cache["users"][user]["stocks"][stock_id] = amount
					else:
						cache["users"][user]["stocks"][stock_id] = cache["users"][user]["stocks"][stock_id] + amount
					
					# Update user balance
					cache["users"][user]["balance"] = cache["users"][user]["balance"] - amount
					# -- store accountTransaction in audit
					
					# Remove the pending entry
					cache["users"][user]["pending_buy"] = {}

					response = "Last buy order committed.\n"
				else:
					print "TIME WINDOW ELAPSED\n"
			
		elif request_type == CANCEL_BUY:
			cache["users"][user]["pending_buy"] = {}
			response = "Buy cancelled.\n"
			
		elif request_type == SELL:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]

			# Check user stock amount
			if amount > 0 and cache["users"][user]["stocks"].get(stock_id, 0) >= amount:
				# get quote and send to user to confirm
				result = get_quote(data_dict)
				result = str(result)
				result = result.split(',')
				response = "Stock: " + result[1] + "  Current price: " + result[0] + "\n"
				# -- store quoteServer in audit

				# Set pending sell to new values (should overwrite existing entry)
				cache["users"][user]["pending_sell"]["stock_id"] = stock_id
				cache["users"][user]["pending_sell"]["amount"] = amount
				cache["users"][user]["pending_sell"]["timestamp"] = int(time.time())
				response = "Please confirm your sell within 60 seconds.\n"
			
		elif request_type == COMMIT_SELL:
			# Check if timestamp is still valid
			if cache["users"][user]["pending_sell"]:
				if int(time.time()) - 60 <= cache["users"][user]["pending_sell"]["timestamp"]:
					
					# Get stock_id and amount from pending_buy entry
					amount = float(cache["users"][user]["pending_sell"]["amount"])
					stock_id = cache["users"][user]["pending_sell"]["stock_id"]

					# Update user stock value
					cache["users"][user]["stocks"][stock_id] = cache["users"][user]["stocks"][stock_id] - amount
					
					# Update user balance
					cache["users"][user]["balance"] = cache["users"][user]["balance"] + amount
					
					# Remove the pending entry
					cache["users"][user]["pending_sell"] = {}
					# -- store accountTransaction in audit
					
					response = "Sell committed.\n"
				else:
					print "TIME WINDOW ELAPSED"

		elif request_type == CANCEL_SELL:
			cache["users"][user]["pending_sell"] = {}
			response = "Sell cancelled.\n"
			
		elif request_type == SET_BUY_AMOUNT:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]

			# Check user balance
			if cache["users"][user]["balance"] >= amount
				# Update user balance
				cache["users"][user]["balance"] -= amount
				# -- store accountTransaction in audit
				
				# Set up buy trigger with stock and amount to spend
				cache["users"][user]["buy_trigger"][stock_id]["amount"] = amount
				print "Trigger ready. Please set commit level.\n"
			
			else:
				print "Insufficient funds to set trigger.\n"
				
		elif request_type == CANCEL_SET_BUY:
			stock_id = data_dict["stock_id"]
			try:
				#deactivate trigger by removing trigger amount
				cache["users"][user]["buy_trigger"][stock_id]["trigger"] = 0
			except:
				#if there was no trigger
				print "Invalid trigger.\n"
			else:
				# put the money back into the user account
				cache["users"][user]["balance"] += cache["users"][user]["buy_trigger"][stock_id]["amount"]
				cache["users"][user]["buy_trigger"][stock_id]["amount"] = 0
				# store accountTransaction in audit
				
				#NOTE: trigger remains in cache, but is inactive - with a database the record can be deleted
			
		elif request_type == SET_BUY_TRIGGER:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]
			
			try:
				if cache["users"][user]["buy_trigger"][stock_id]["amount"] > 0:
					if amount > 0
						cache["users"][user]["buy_trigger"][stock_id]["trigger"] = amount;
					else:
						print "Buy trigger amount is not a positive value; Trigger not enabled.\n"
				else:
					# buy_trigger for stock exists with zero value (old trigger that was cancelled)
					print "Buy trigger not initialized; Trigger not enabled.\n"
					
			except:
				#buy_trigger doesn't exist at all
				print "Buy trigger not initialized; Trigger not enabled.\n"
				
		elif request_type == SET_SELL_AMOUNT:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]
			
			if cache["users"][user]["stocks"][stock_id] >= amount:
				cache["users"][user]["stocks"][stock_id] -= amount
				# -- store accountTransaction in audit
				
				cache["users"][user]["sell_trigger"][stock_id]["amount"] = amount
			else:
				print "Insufficient stock to set trigger.\n"
				
			print "Not implemented"
			
		elif request_type == SET_SELL_TRIGGER:
			# What stock and how much
			amount = float(data_dict["amount"])
			stock_id = data_dict["stock_id"]
			
			try:
				if cache["users"][user]["sell_trigger"][stock_id]["amount"] > 0:
					if amount > 0:
						cache["users"][user]["sell_trigger"][stock_id]["trigger"] = amount
					else:
						print "Sell trigger amount is not a positive value; Trigger not enabled.\n"
				else:
					# sell_trigger for stock exists with zero value (old trigger that was cancelled)
					print "Sell trigger not initialized; Trigger not enabled.\n"
			except:
				print "Sell trigger not initialized; Trigger not enabled.\n"
			
		elif request_type == CANCEL_SET_SELL:
			stock_id = data_dict["stock_id"]
			try:
				cache["users"][user]["sell_trigger"][stock_id]["trigger"] = 0;
			except:
				print "Trigger does not exist.\n"
			else:
				cache["users"][user]["stocks"][stock_id] += cache["users"][user]["sell_trigger"][stock_id]["amount"]
				cache["users"][user]["sell_trigger"][stock_id]["amount"] = 0
				print "Sell trigger on " + stock_id + "cancelled.\n"
			
		elif request_type == DUMPLOG:
			try:
				filename = data_dict["filename"]
			except:
				print "No filename for dumplog command. Dump not performed.\n"
			else:
				#activate the dump on audit

		elif request_type == DISPLAY_SUMMARY:
			print cache["users"][user]
			
		else:
			print "Invalid command.\n"

	print "Cache State: "
	print cache
	print "\n Response: "
	print response
	print "\n"
	return response, cache

# Request a Quote from the quote server
def get_quote(data):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.connect(('quoteserve.seng.uvic.ca', 4444))
	user = data['user']
	stock_id = data['stock_id']
	request = user + ", " + stock_id + "\r"
	s.send(request)

	response = s.recv(1024)
	print response
	s.close()
	return response

def main():
	cache = {
		"users": {},
		"stocks": {}
	}

	host = ''
	port = 44421

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))

	while 1:
		print 'Main: waiting\n'
		s.listen(1)
		conn, addr = s.accept()
		print 'Connection from ' + addr[0] + '\n'
		
		while 1:
			data = conn.recv(1024)
			if (data):
				print 'Received: ' + data
				
				response, cache = process_request(data, cache)
				conn.send(response)
			else:
				break


if __name__ == "__main__":
    main()