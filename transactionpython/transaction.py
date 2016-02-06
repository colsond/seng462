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
##			"buy_trigger": {
##				"stock_id": {
##      		"amount": 0,
##					"trigger": 0
##				}
##			"sell_trigger": {
##				"stock_id": {
##      		"amount": 0,
##					"trigger": 0
##				}
##			},
##			"quotes": {
##				stock_id: {
##
##}
##			}
##		}
##	}
##}

web_server_address = 'b132.seng.uvic.ca'
audit_server_address = 'b142.seng.uvic.ca'

web_server_port = 44421
audit_server_port = 44421

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
	server_address = (audit_server_address, audit_server_port)
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
		funds = str(float(funds) / 100)
		audit_dict["funds"] = funds
	
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
		"logType": "AccountTransactionType",
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
		funds = str(float(funds) / 100)
		audit_dict["funds"] = funds
	
	send_audit_entry(str(audit_dict))

	return

def audit_error_event(
		timestamp,
		server,
		transactionNum,
		command,username="",
		stockSymbol="",
		filename="",
		funds=0,
		errorMessage=""):

	audit_dict = {
		"logType": "ErrorEventType",
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
		funds = str(float(funds) / 100)
		audit_dict["funds"] = funds

	if errorMessage:
		audit_dict["errorMessage"] = errorMessage
	
	send_audit_entry(str(audit_dict))

	return

def audit_debug(
		timestamp,
		server,
		transactionNum,
		command,
		username="",
		stockSymbol="",
		filename="",
		funds=0,
		debugMessage=""):

	audit_dict = {
		"logType": "ErrorEventType",
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
		funds = str(float(funds) / 100)
		audit_dict["funds"] = funds

	if errorMessage:
		audit_dict["debugMessage"] = errorMessage
	
	send_audit_entry(str(audit_dict))

	return

def process_request(data, cache):
	# Convert Data to Dict
	data_dict = ast.literal_eval(data)

	# -- store userCommand in audit regardless of correctness
	
	response = "\n"

	server_name = "transaction_server_1"
	filename = ""
	username = ""
	transaction_id = data_dict.get('transaction_id')
	
	if transaction_id is None:
		print "Missing transaction id. Ignored.\n"
	else:

		request_type = data_dict.get('request_type')

		if request_type is None:
			print "Malformed request. Ignored.\n"
		else:
			stock_id = data_dict.get('stock_id')

			user = data_dict.get('user')
			if user and user not in cache["users"]:
				cache["users"][user] = {
					"balance": 0,
					"stocks": {},
					"quotes": {},
					"pending_buy": {},
					"pending_sell": {},
					"buy_trigger": {},
		      		"sell_trigger": {},
				}

			amount = data_dict.get('amount')
			
			if amount is not None:
				# store amounts in pennies to avoid decimals
				amount = int(float(amount)*100)

			filename = data_dict.get('filename')
			balance = cache["users"][user]["balance"]

			audit_user_command_event(
				now(),
				server_name,
				transaction_id,
				request_type,
				username,
				stock_id,
				filename,
				balance
			)

			if request_type == ADD:
					if amount is None:
						response = "ADD - Amount not specified.\n"
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							username,
							stock_id,
							filename,
							response
						)
					elif amount < 0:
						response = "ADD - Attempting to add a negative amount\n"
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							username,
							stock_id,
							filename,
							response
						)
					else:
						cache["users"][user]["balance"] += amount
						response = "Added\n"
						audit_transaction_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							username,
							cache["users"][user]["balance"]
						)
		
			elif request_type == QUOTE:
				cache = get_quote(data_dict, cache)
				response += "\n"
			
			elif request_type == BUY:
				# Check user balance
				if cache["users"][user]["balance"] >= amount:
					# get quote and send to user to confirm
					cache = get_quote(data_dict, cache)
					price = cache["users"][user]["quotes"][stock_id]["price"]
					timestamp = cache["users"][user]["quotes"][stock_id]["timestamp"]
					response = "Stock: " + stock_id + "  Current price: " + price + "\n"
				
				
					# Set pending buy to new values (should overwrite existing entry)
					cache["users"][user]["pending_buy"]["stock_id"] = stock_id
					cache["users"][user]["pending_buy"]["amount"] = amount
					cache["users"][user]["pending_buy"]["timestamp"] = now()
					response = "Please confirm your purchase within 60 seconds.\n"
			
			elif request_type == COMMIT_BUY: 
				# Check if timestamp is still valid
				if cache["users"][user]["pending_buy"]:
					if now() - 60 <= cache["users"][user]["pending_buy"]["timestamp"]:
					
						# Get stock_id and amount from pending_buy entry
						amount = int(cache["users"][user]["pending_buy"]["amount"])
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
				# Check user stock amount
				if amount > 0 and cache["users"][user]["stocks"].get(stock_id, 0) >= amount:
					# get quote and send to user to confirm
					time_start = now()
					cache = get_quote(data_dict, cache)
					quoteServerTime = now() - time_start
					price = cache["users"][user]["quotes"][stock_id]["price"]
					timestamp = cache["users"][user]["quotes"][stock_id]["timestamp"]
					cryptokey = cache["users"][user]["quotes"][stock_id]["cryptokey"]
					response = "Stock: " + stock_id + "  Current price: " + price + "\n"
					# -- store quoteServer in audit

					# Set pending sell to new values (should overwrite existing entry)
					cache["users"][user]["pending_sell"]["stock_id"] = stock_id
					cache["users"][user]["pending_sell"]["amount"] = amount
					cache["users"][user]["pending_sell"]["timestamp"] = now()
					response = "Please confirm your sell within 60 seconds.\n"
			
			elif request_type == COMMIT_SELL:
				# Check if timestamp is still valid
				if cache["users"][user]["pending_sell"]:
					if now() - 60 <= cache["users"][user]["pending_sell"]["timestamp"]:
					
						# Get stock_id and amount from pending_buy entry
						amount = int(cache["users"][user]["pending_sell"]["amount"])
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
				# Check user balance
				if cache["users"][user]["balance"] >= amount:
					# Update user balance
					cache["users"][user]["balance"] -= amount
					# -- store accountTransaction in audit
			
					# Set up buy trigger with stock and amount to spend
					if stock_id not in cache["users"][user]["buy_trigger"]:
						cache["users"][user]["buy_trigger"] = {
							stock_id: {
								"amount" : amount,
								"trigger" : 0
							}
						}
					else:
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
				try:
					if cache["users"][user]["buy_trigger"][stock_id]["amount"] > 0:
						if amount > 0:
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
					if cache["users"][user]["stocks"][stock_id] >= amount:
						cache["users"][user]["stocks"][stock_id] -= amount
						# -- store accountTransaction in audit
				
						if stock_id not in cache["users"][user]["sell_trigger"]:
							cache["users"][user]["sell_trigger"] = {
								stock_id: {
									"amount" : amount,
									"trigger" : 0
								}
							}
						else:
							cache["users"][user]["sell_trigger"][stock_id]["amount"] = amount
				
					else:
						print "Insufficient stock to set trigger.\n"
			
			elif request_type == SET_SELL_TRIGGER:			
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
				try:
					cache["users"][user]["sell_trigger"][stock_id]["trigger"] = 0;
				except:
					print "Trigger does not exist.\n"
				else:
					cache["users"][user]["stocks"][stock_id] += cache["users"][user]["sell_trigger"][stock_id]["amount"]
					cache["users"][user]["sell_trigger"][stock_id]["amount"] = 0
					print "Sell trigger on " + stock_id + "cancelled.\n"
			
			elif request_type == DUMPLOG:
					if filename is None:
						print "No filename for dumplog command. Dump not performed.\n"
					else:
						#activate the dump on audit
						print "Dump engaged.\n"

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
def get_quote(data, cache):
	user = data['user']
	stock_id = data['stock_id']
	transaction_id = data['transaction_id']
	try:
		existing_timestamp = cache["users"][user]["quotes"][stock_id]["timestamp"]
		print "existing timestamp: " + str(existing_timestamp)
	except KeyError:
		existing_timestamp = None
	print now()
	# If there is no existing quote for this user/stock_id, or the existing quote has expired, get a new one
	if not existing_timestamp or now() - int(existing_timestamp) > 60:
		time_start = now()
		print "HITTING QUOTE SERVER \n HITTING QUOTE SERVER \n OMG \n!!!"
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		s.connect(('quoteserve.seng.uvic.ca', 4444))
		request = user + ", " + stock_id + "\r"
		s.send(request)

		response = s.recv(1024)
		print response
		s.close()
		quoteServerTime = now() - time_start()
		response = response.split(',')
		print "quote server response: " + str(response)

		cache["users"][user]["quotes"][response[2]] = {
			"price": response[0],
			"user": response[1],
			"timestamp": int(response[3]),
			"cryptokey": response[4]
		}

		audit_quote_server_event(
			int(response[3]),
			server_name,
			transaction_id,
			response[0],
			response[2],
			response[1],
			quoteServerTime,
			response[4]
		)

	return cache

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
