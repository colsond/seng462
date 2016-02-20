#!/usr/bin/python
import ast
import os
import socket
import string
import sys
import time

# -- REMEMBER: to not run in debug mode:
#				python -O transaction.py

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
##			},
##			"sell_trigger": {
##				"stock_id": {
##      		"amount": 0,
##					"trigger": 0
##				}
##			},
##			"quotes": {
##				stock_id: {
##
##				}
##			}
##		}
##	}
##}

server_name = "transaction_server_1"

web_server_address = 'b132.seng.uvic.ca'
audit_server_address = 'b142.seng.uvic.ca'
SELF_HOST = ''

# Port list, in case things are run on same machine
# 44421	Audit
# 44422 Transaction
audit_server_port = 44421
SELF_PORT = 44422

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
		#funds = "{:.2f}".format(float(funds)/100)
		audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(funds%100)
	
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
		"price" : str(int(price/100)) + '.' + "{:02d}".format(price%100),
		#"price": "{:.2f}".format(float(price)/100),
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
		"funds" : str(int(funds/100)) + '.' + "{:02d}".format(funds%100)
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
		#funds = "{:.2f}".format(float(funds)/100)
		audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(funds%100)
	
	send_audit_entry(str(audit_dict))

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
		#funds = "{:.2f}".format(float(funds)/100)
		audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(funds%100)

	if errorMessage:
		audit_dict["errorMessage"] = errorMessage
	
	send_audit_entry(str(audit_dict))

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
#		funds = str(float(funds) / 100)
		audit_dict["funds"] = str(int(funds/100)) + '.' + "{:02d}".format(funds%100)
		

	if debugMessage:
		audit_dict["debugMessage"] = debugMessage
	
	send_audit_entry(str(audit_dict))

	return

def process_request(data, cache):
	# Convert Data to Dict
	data_dict = ast.literal_eval(data)

	print "\nNew transaction: "
	print data_dict
	print "\n"

	response = "Request not processed."
	transaction_id = data_dict.get('transaction_id')
	request_type = data_dict.get('request_type')
	user = data_dict.get('user')
	stock_id = data_dict.get('stock_id')
	filename = data_dict.get('filename')
	amount = data_dict.get('amount')


	# -- DEBUG: store event in audit regardless of correctness
	if __debug__:
		audit_debug(
			now(),
			server_name,
			transaction_id,
			request_type,
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
	if transaction_id is None:
		response = "Missing transaction id. Transaction ignored."
		audit_error_event(
			now(),
			server_name,
			transaction_id,
			request_type,
			user,
			stock_id,
			filename,
			amount,
			response
		)
	else:

		if request_type is None:
			response = "Missing request command. Transaction ignored."
			audit_error_event(
				now(),
				server_name,
				transaction_id,
				request_type,
				user,
				stock_id,
				filename,
				amount,
				response
			)
		else:

			# -- If there is a transaction id and request type then check if there
			# is a user id in the request, check if that user id exists in the 
			# database, and if not then add them; Store user's present balance.

			if user:
				if user not in cache["users"]:
					cache["users"][user] = {
						"balance": 0,
						"stocks": {},
						"quotes": {},
						"pending_buy": {},
						"pending_sell": {},
						"buy_trigger": {},
					  		"sell_trigger": {},
					}
					balance = None
				else:
					balance = cache["users"][user]["balance"]
			# No action if no user in request


			# -- Convert amounts to pennies to avoid decimals
			if amount is not None:
				amount = int(float(amount)*100)

			# Store request before processing
			audit_user_command_event(
				now(),
				server_name,
				transaction_id,
				request_type,
				user,
				stock_id,
				filename,
				amount
			)

# --------------
# -- ADD REQUEST
# --------------
			if request_type == ADD:
				if amount is None:
					response = "Amount not specified."
					audit_error_event(
						now(),
						server_name,
						transaction_id,
						request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response
					)
				else:
					cache["users"][user]["balance"] += amount
					response = "Added."
					audit_transaction_event(
						now(),
						server_name,
						transaction_id,
						request_type,
						user,
						cache["users"][user]["balance"]
					)

# ----------------
# -- QUOTE REQUEST
# ----------------
			elif request_type == QUOTE:
				if stock_id in cache["users"][user]["quotes"]:
					existing_timestamp = cache["users"][user]["quotes"][stock_id].get("timestamp",0)
				else:
					existing_timestamp = None
					
				if __debug__:
					print "existing timestamp: " + str(existing_timestamp)
					print "current time: " + str(now())

				# If there is no existing quote for this user/stock_id, or the existing quote has expired, get a new one
				if not existing_timestamp or now() - int(existing_timestamp) > 60000:

					if __debug__:
						audit_debug(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							stock_id,
							None,#filename
							amount,
							'Sending quote request')

					current_quote = get_quote({"user":user,"stock_id":stock_id,"transaction_id":transaction_id})

					if current_quote[1] == stock_id:
						cache["users"][user]["quotes"][current_quote[1]] = {
							"price": current_quote[0],
							"user": current_quote[2],
							"timestamp": int(current_quote[3]),
							"cryptokey": current_quote[4]
						}
					else:
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							stock_id,
							None,#filename
							None,#amount
							'Quoted stock name [' + str(current_quote[1]) + '] does not match requested stock name.'
						)

					audit_quote_server_event(
						now(),
						server_name,
						transaction_id,
						current_quote[0],
						current_quote[1],
						current_quote[2],
						int(current_quote[3]),
						current_quote[4]
					)

				response = str(stock_id) + ':' + str(cache["users"][user]["quotes"][stock_id]['price'])

# --------------
# -- BUY REQUEST
# --------------
			elif request_type == BUY:

				# Check user balance
				if cache["users"][user]["balance"] >= amount:
					# get quote and send to user to confirm

# FROM QUOTE REQUEST

					# UNCOMMENT IF CACHED QUOTES CAN BE USED FOR BUY REQUESTS
					#existing_timestamp = cache["users"][user]["quotes"][stock_id].get("timestamp")
					#if __debug__:
					#	print "existing timestamp: " + str(existing_timestamp)
					#	print "current time: " + now()

					## If there is no existing quote for this user/stock_id, or the existing quote has expired, get a new one
					#if not existing_timestamp or now() - int(existing_timestamp) > 60000:

					#TAB REMAINING CODE IN QUOTE SECTION IF ENABLING CACHING

					if __debug__:
						audit_debug(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							stock_id,
							None,#filename
							amount,
							'Sending quote request')

					current_quote = get_quote({"user":user,"stock_id":stock_id,"transaction_id":transaction_id})

					if current_quote[1] == stock_id:
						cache["users"][user]["quotes"][current_quote[1]] = {
							"price": current_quote[0],
							"user": current_quote[2],
							"timestamp": now(),
							"cryptokey": current_quote[4]
						}
					else:
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							stock_id,
							None,#filename
							None,#amount
							'Quoted stock name [' + str(current_quote[1]) + '] does not match requested stock name.'
						)

					audit_quote_server_event(
						now(),
						server_name,
						transaction_id,
						current_quote[0],
						current_quote[1],
						current_quote[2],
						int(current_quote[3]),
						current_quote[4]
					)

# END QUOTE SECTION
					
					price = cache["users"][user]["quotes"][stock_id]["price"]
					timestamp = cache["users"][user]["quotes"][stock_id]["timestamp"]
			
					# Set pending buy to new values (should overwrite existing entry)
					cache["users"][user]["pending_buy"]["stock_id"] = stock_id
					cache["users"][user]["pending_buy"]["amount"] = price
					cache["users"][user]["pending_buy"]["timestamp"] = timestamp
					
					response = str(stock_id) + ":" + str(price)

				else:
					response = "Insufficient funds in account to place buy order."

# ---------------------
# -- COMMIT BUY REQUEST
# ---------------------
			elif request_type == COMMIT_BUY: 
				# Check if timestamp is still valid
				if cache["users"][user]["pending_buy"]:
					if now() - 60000 <= cache["users"][user]["pending_buy"]["timestamp"]:
				
						# Get stock_id and amount from pending_buy entry
						amount = int(cache["users"][user]["pending_buy"]["amount"])
						stock_id = cache["users"][user]["pending_buy"]["stock_id"]
				
						# Update user balance
						cache["users"][user]["balance"] = cache["users"][user]["balance"] - amount

						# Create or update stock entry for user
						if stock_id not in cache["users"][user]["stocks"]:
							cache["users"][user]["stocks"][stock_id] = amount
						else:
							cache["users"][user]["stocks"][stock_id] += amount
							
						audit_transaction_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							amount)
				
						# Remove the pending entry
						cache["users"][user]["pending_buy"] = {}

						response = "Last buy order committed."
						
					else:
						response = "Time elapsed. Commit buy cancelled."
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						None,#stock
						None,#filename
						None,#amount
						response)
						

# ---------------------
# -- CANCEL BUY REQUEST
# ---------------------
			elif request_type == CANCEL_BUY:
				cache["users"][user]["pending_buy"] = {}
				response = "Buy cancelled."
				
# ---------------
# -- SELL REQUEST
# ---------------
			elif request_type == SELL:
				# Check user stock amount
				if amount > 0:
					if cache["users"][user]["stocks"].get(stock_id, 0) >= amount:
						# get quote and send to user to confirm
						
# FROM QUOTE REQUEST

						if __debug__:
							audit_debug(
								now(),
								server_name,
								transaction_id,
								request_type,
								user,
								stock_id,
								None,#filename
								amount,
								'Sending quote request')

						current_quote = get_quote({"user":user,"stock_id":stock_id,"transaction_id":transaction_id})

						audit_quote_server_event(
							now(),
							server_name,
							transaction_id,
							current_quote[0],
							current_quote[1],
							current_quote[2],
							int(current_quote[3]),
							current_quote[4]
						)

						if current_quote[1] != stock_id:
							response = 'Quoted stock name [' + current_quote[1] + '] does not match requested stock name.'
							audit_error_event(
								now(),
								server_name,
								transaction_id,
								request_type,
								user,
								stock_id,
								None,#filename
								None,#amount
								response
							)
						else:
							cache["users"][user]["quotes"][current_quote[1]] = {
								"price": current_quote[0],
								"user": current_quote[2],
								"timestamp": now(),
								"cryptokey": current_quote[4]
							}

# END QUOTE SECTION

							price = cache["users"][user]["quotes"][stock_id]["price"]
							timestamp = cache["users"][user]["quotes"][stock_id]["timestamp"]
							
							# Set pending sell to new values (should overwrite existing entry)
							cache["users"][user]["pending_sell"]["stock_id"] = stock_id
							cache["users"][user]["pending_sell"]["amount"] = price
							cache["users"][user]["pending_sell"]["timestamp"] = timestamp
							response = str(stock_id) + ":" + str(price)

					else:
						response = "Insufficient stock owned."
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)
					
# ----------------------
# -- COMMIT SELL REQUEST
# ----------------------
			elif request_type == COMMIT_SELL:
				# Check if timestamp is still valid
				if cache["users"][user]["pending_sell"]:
					if now() - 60000 <= cache["users"][user]["pending_sell"]["timestamp"]:
				
						# Get stock_id and amount from pending_buy entry
						amount = int(cache["users"][user]["pending_sell"]["amount"])
						stock_id = cache["users"][user]["pending_sell"]["stock_id"]

						# Update user stock value
						cache["users"][user]["stocks"][stock_id] -= amount
				
						# Update user balance
						cache["users"][user]["balance"] += amount
						
						audit_transaction_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							amount
						)
				
						# Remove the pending entry
						cache["users"][user]["pending_sell"] = {}
				
						response = "Sell committed."
					else:
						response = "TIME WINDOW ELAPSED"
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						None,#stock
						None,#filename
						None,#amount
						response)
					
# ----------------------
# -- CANCEL SELL REQUEST
# ----------------------
			elif request_type == CANCEL_SELL:
				cache["users"][user]["pending_sell"] = {}
				response = "Sell cancelled."
				
# -------------------------
# -- SET BUY AMOUNT REQUEST
# -------------------------
			elif request_type == SET_BUY_AMOUNT:
			
				# Check user balance
				if cache["users"][user]["balance"] >= amount:
					# Check if there is an existing trigger for the stock
					if stock_id in cache["users"][user]["buy_trigger"] and cache["users"][user]["buy_trigger"][stock_id].get("trigger",0) > 0:
						response = "Trigger already set for stock."
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							stock_id,
							None,#filename
							amount,
							response)
					else:
						# Update user balance
						cache["users"][user]["balance"] -= amount
						
						audit_transaction_event(
							now(),
							server_name,
							transaction_id,
							request_type,
							user,
							amount
						)
			
						# Set up buy trigger with stock and amount to spend
						cache["users"][user]["buy_trigger"] = {
							stock_id: {
								"amount" : amount,
								"trigger" : 0
							}
						}
				else:
					response = "Insufficient funds to set trigger."
					audit_error_event(
						now(),
						server_name,
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)
					
# -------------------------
# -- CANCEL SET BUY REQUEST
# -------------------------
			elif request_type == CANCEL_SET_BUY:
				if stock_id not in cache["users"][user]["buy_trigger"] or cache["users"][user]["buy_trigger"][stock_id].get("trigger",0) == 0:
					#if there was no trigger
					response = "No trigger listed for stock."
					audit_error_event(
						now(),
						server_name,
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						None,#amount
						response)
				else:
					# put the money back into the user account
					amount = cache["users"][user]["buy_trigger"][stock_id]["amount"]
					
					cache["users"][user]["buy_trigger"][stock_id]["trigger"] = 0
					cache["users"][user]["buy_trigger"][stock_id]["amount"] = 0
					
					cache["users"][user]["balance"] += amount
						
					audit_transaction_event(
						now(),
						server_name,
						transaction_id,
						request_type,
						user,
						amount
					)
					
					response = "Buy trigger cancelled."
					#NOTE: trigger remains in cache, but is inactive - with a database the record can be deleted					

# --------------------------
# -- SET BUY TRIGGER REQUEST
# --------------------------
			elif request_type == SET_BUY_TRIGGER:
				# Stock should exist in buy trigger list, and have amount set, but no trigger value set
				if stock_id in cache["users"][user]["buy_trigger"]:
					if cache["users"][user]["buy_trigger"][stock_id].get("amount",0) > 0:
						if cache["users"][user]["buy_trigger"][stock_id].get("trigger",0) == 0:
							if amount > 0:
								cache["users"][user]["buy_trigger"][stock_id]["trigger"] = amount;
								response = "Buy trigger set."
							else:
								response = "Cannot set trigger to buy at 0 or less."
								audit_error_event(
									now(),
									server_name,
									transaction_id,
									request_type,
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
								transaction_id,
								request_type,
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
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)
					
# --------------------------
# -- SET SELL AMOUNT REQUEST
# --------------------------
			elif request_type == SET_SELL_AMOUNT:
				if stock_id in cache["users"][user]["stocks"]:
					if cache["users"][user]["stocks"][stock_id] >= amount:
						if stock_id in cache["users"][user]["sell_trigger"] and cache["users"][user]["sell_trigger"].get("trigger",0) > 0:
							response = "Active sell trigger for stock."
							audit_error_event(
								now(),
								server_name,
								transaction_id,
								request_type,
								user,
								stock_id,
								None,#filename
								amount,
								response)
						else:
							cache["users"][user]["stocks"][stock_id] -= amount
							
							cache["users"][user]["sell_trigger"] = {
								stock_id: {
									"amount" : amount,
									"trigger" : 0
								}
							}
							response = "Sell trigger initialised."
					else:
						response = "Insufficient stock to set trigger."
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)
				
# ---------------------------
# -- SET SELL TRIGGER REQUEST
# ---------------------------
			elif request_type == SET_SELL_TRIGGER:			
				if stock_id in cache["users"][user]["sell_trigger"]:
					if cache["users"][user]["sell_trigger"][stock_id]["amount"] > 0:
						if amount > 0:
							cache["users"][user]["sell_trigger"][stock_id]["trigger"] = amount
							response = "Sell trigger set."
						else:
							response = "Sell trigger amount is not a positive value; Trigger not enabled."
							audit_error_event(
								now(),
								server_name,
								transaction_id,
								request_type,
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
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)
		
# --------------------------
# -- CANCEL SET SELL REQUEST
# --------------------------
			elif request_type == CANCEL_SET_SELL:
				if stock_id in cache["users"][user]["sell_trigger"]:
					if cache["users"][user]["sell_trigger"][stock_id]["trigger"] > 0:
						cache["users"][user]["stocks"][stock_id] += cache["users"][user]["sell_trigger"][stock_id]["amount"]
						cache["users"][user]["sell_trigger"][stock_id]["amount"] = 0
						cache["users"][user]["sell_trigger"][stock_id]["trigger"] = 0
						
						response = "Sell trigger cancelled."
					else:
						response = "Sell trigger not active on this stock."
						audit_error_event(
							now(),
							server_name,
							transaction_id,
							request_type,
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
						transaction_id,
						request_type,
						user,
						stock_id,
						None,#filename
						amount,
						response)

# --------------------------
# -- DUMPLOG REQUEST
# --------------------------		
			elif request_type == DUMPLOG:
					if filename is None:
						print "No filename for dumplog command. Dump not performed.\n"
					else:
						#activate the dump on audit
						print "Dump engaged. Honest.\n"

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
# Values returned from function in the order the quote server provides
#
# Quote server response format:
#		price,stock,user,timestamp,cryptokey
#
# Note: function returns price in cents

def get_quote(data):
	user = data['user']
	stock_id = data['stock_id']
	transaction_id = data['transaction_id']

	if __debug__:
		print "HITTING QUOTE SERVER \n HITTING QUOTE SERVER \n OMG \n!!!"

	request = stock_id + ", " + user + "\r"

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('quoteserve.seng.uvic.ca', 4444))
	s.send(request)
	response = s.recv(1024)
	s.close()

	if __debug__:
		print "quote server response: " + str(response)

	response = response.split(',')
	response[0] = int(float(response[0])*100)
	response[4] = response[4].translate(None,'\n')

	return response

def main():
	cache = {
		"users": {},
		"stocks": {}
	}

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((SELF_HOST, SELF_PORT))

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
