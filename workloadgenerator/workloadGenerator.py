import requests
import io

f = open("1userWorkLoad", 'r')
for line in f:
	tokens = line.split()
	cmdNum = tokens[0]
	request = tokens[1].split(',')
	if request[0]== "add":
		//CALL ADD
		//LOG TO AUDIT
	if request[0]== "QUOTE":
		//CALL QUOTE
		//LOG TO AUDIT
						
	if request[0]== "BUY":
		//CALL BUY
		//LOG TO AUDIT
	if request[0]== "COMMIT_BUY":
		//CALL COMMIT_BUY
		//LOG TO AUDIT
	if request[0]== "COMMIT_SELL":
		//CALL COMMIT_SELL
		//LOG TO AUDIT
	if request[0]== "DISPLAY_SUMMARY":
		//CALL DISPLAY_SUMMARY
		//LOG TO AUDIT
	if request[0]== "CANCEL_BUY":
		//CALL CANCEL_BUY
		//LOG TO AUDIT
	if request[0]== "CANCEL_SET_BUY":
		//CALL CANCEL_SET_BUY
		//LOG TO AUDIT
	if request[0]== "SET_BUY_AMOUNT":
		//CALL SET_BUY_AMOUNT
		//LOG TO AUDIT
	if request[0]== "SELL":
		//CALL SELL
		//LOG TO AUDIT
	if request[0]== "CANCEL_SET_SELL":
		//CALL CANCEL_SET_SELL
		//LOG TO AUDIT
	if request[0]== "SET_SELL_TRIGGER":
		//CALL SET_SELL_TRIGGER
		//LOG TO AUDIT
	if request[0]== "SET_SELL_AMOUNT":
		//CALL SET_SELL_AMOUNT
		//LOG TO AUDIT
	if request[0]== "DUMPLOG":
		//CALL DUMPLOG
		//GENERATE XML ON AUDIT SERVER
	else
		//INVALID REQUEST
		
