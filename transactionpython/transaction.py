#!/usr/bin/python
import ast
import os
import socket
import string
import sys
import time

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

def process_request(data, cache):
	# Convert Data to Dict
	data_dict = ast.literal_eval(data)

	# -- store userCommand in audit regardless of correctness
	
	response = "\n"
	request_type = data_dict.get("request_type")
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
				response = str(result)
				response += "\n"
				# -- store quoteServer in audit
				
				# Set pending buy to new values (should overwrite existing entry)
				cache["users"][user]["pending_buy"]["stock_id"] = stock_id
				cache["users"][user]["pending_buy"]["amount"] = amount
				cache["users"][user]["pending_buy"]["timestamp"] = time.time()
				response = "Please confirm your purchase within 60 seconds.\n"
				
			
		elif request_type == COMMIT_BUY: 
			# Check if timestamp is still valid
			if cache["users"][user]["pending_buy"]:
				if time.time() - 60 <= cache["users"][user]["pending_buy"]["timestamp"]:
					
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
				cache["users"][user]["pending_sell"]["timestamp"] = time.time()
				response = "Please confirm your sell within 60 seconds.\n"
			
		elif request_type == COMMIT_SELL:
			# Check if timestamp is still valid
			if cache["users"][user]["pending_sell"]:
				if time.time() - 60 <= cache["users"][user]["pending_sell"]["timestamp"]:
					
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
			print "Not implemented"
			# make_request(request_type, user)
			# -- converted from apparent duplicate SET_SELL_AMOUNT
			# -- Check if given user has given amount money
			# -- if yes, set up buy trigger for user with stock and amount to buy
			
		elif request_type == CANCEL_SET_BUY:
			print "Not implemented"
			# make_request(request_type, user)
			# -- check to see if user has a set buy trigger for given stock
			# -- if yes, remove trigger entry and return funds to user
			
		elif request_type == SET_BUY_TRIGGER:
			print "Not implemented"
			# make_request(request_type, user)
			# -- check if trigger is initialised with given user and stock
			# -- if yes, set buy trigger price
			
		elif request_type == SET_SELL_AMOUNT:
			print "Not implemented"
			# make_request(request_type, user)
			# -- check if user has enough stock to set trigger
			# -- create entry in trigger list: user, stock, amount to sell
			
		elif request_type == SET_SELL_TRIGGER:
			print "Not implemented"
			# make_request(request_type, user)
			# -- check if trigger has been initialized for the given user/stock combination
			# -- if yes, add given triggering price to trigger
			
		elif request_type == CANCEL_SET_SELL:
			print "Not implemented"
			# make_request(request_type, user)
			# -- Check if there is a trigger for the stock
			# -- if yes, cancel it and return the stock to the active portfolio
			
		elif request_type == DUMPLOG:
			print "Not implemented"
			# make_request(request_type, user)
			# -- two modes:
			# --   userid, filename - print transactions for user to file
			# --   filename - print all transactions to file

		elif request_type == DISPLAY_SUMMARY:
			print "Not implemented"
			# make_request(request_type, user)
			# -- for first run, only needs to touch log
			# -- requires: transaction history, current balance, current stocks held, current triggers

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
##			}
##		}
##	}
##}

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