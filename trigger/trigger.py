# trigger.py
#
# Database stores triggers
# Get list of upcoming quote expirations on triggers
# get quotes for each one
# check against trigger price
# complete trigger if price met
#
# Every 5 seconds:
# get upcoming expirations
# 	connect to db
# 	request records
# get quotes for each
# 	connect to quote cache
# 	request quotes, ttl
# check against trigger
# 	compare quote against trigger val
# complete
# 	if buy
# 		if quote <= trigger, give stock, erase trigger
# 		else update ttl
# 	if sell
# 		if quote >= trigger, give money, erase trigger
# 		else update ttl

import time

PORT = 44420
MIN_PORT = 44420
MAX_PORT = 44429

DB_HOST = "b133.seng.uvic.ca"
DB_PORT = "44429"

check_time_delta = 5000	# update records older than this many milliseconds

quote_connections = 10	# maximum connections to quote_cache server

db = Database()

#-----------------------------------------------------------------------------
# now
# Returns server time in milliseconds
def now():
	return int(time.time() * 1000)

def get_upcoming_triggers(connection):

	target_time = now + check_time_delta
	#magically request records from db with check time < check_time_delta

	return #I'm going to assume this returns an array of results

def update_triggers(trigger_list):

	for a_dict in trigger_list:
#		stock_id, user, transactionNum, command
		quote = get_quote({'stock_id':a_dict['stock_id'], 'user':a_dict['user_id'], 'transactionNum':9999, 'command':'QUOTE')
#		stock_id, user, transactionNum, price, timestamp, key
		if a_dict['type'] == 'BUY':
			if quote['price'] <= a_dict['trigger']:
				#erase the trigger
				#give that MF hiz stock
			else:
				#update the trigger table with the new check_time

		if a_dict['type'] == 'SELL':
			if quote['price'] >= a_dict['trigger']:
				#erase the trigger
				#give that MF hiz monay
			else:
				#update the trigger table with the new check_time

return

# feeder
# conn.insert_record("Trigger", "type,user_id,stock_id,amount,trigger", "'buy','%s','%s',%d,%d" % (user,stock_id,amount,0))


def connect_to_db():
	# Initialize Database
	global db = Database(
		host=DB_HOST,
		port=DB_PORT,
		dbname="transactiondb",
		dbuser="cusmith",
		dbpass="",
		minconn=1,
		maxconn=1,
	)
	db.initialize()

	# Get a connection to the DB (Need to create threads here)
	connection = db.get_connection()

return connection

def main(argv):
	global PORT
	
	try:
		cmdline_options, args = getopt.getopt(argv,'hp:')
	
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) + '\n'# will print something like "option -a not recognized"
		print 'Use -p [port number] to set port. Valid range is 44420 to 44429\n'
		usage()
		sys.exit(2)

	for o, a in cmdline_options:
		if o == "-p":
			a = int(a)
			if a >= MIN_PORT and a <= MAX_PORT:
				PORT = a
			else:
				print "Invalid port (" + str(a) + ") specified. Valid range: " + str(MAX_PORT) + " - " + str(MIN_PORT) + "\n"
				sys.exit(2)
		if o == "-h":
			print "Use -p to set port number. Valid range: " + str(MAX_PORT) + " - " + str(MIN_PORT) + "\n"
			sys.exit(2)
	print "Setting port [" + str(PORT) + "]\n"

if __name__ == "__main__":
	main(sys.argv[1:])

