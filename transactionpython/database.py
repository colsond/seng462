import psycopg2

class ConnectionPool:

    def __init__(self, mincon, maxcon):
        

class Database:

    def __init__(self, dbname, dbuser, dbpass):
        self.conn = psycopg2.connect(
            # host=conf_hostname,
            database=dbname,
            user=dbuser,
            password=dbpass,
            # port=conf_dbport
        )
        self.conn.autocommit = True
        self.curs = self.conn.cursor()

    def initialize(self):
        ## Will need to change these based 
        try:
            self.curs.execute("""CREATE TABLE Users (
                                id char(20), balance int)""")
        except:
    	    self.conn.rollback()
    	    self.curs.execute("""DROP TABLE Users""")
    	    self.curs.execute("""CREATE TABLE Users (
                                    id text, balance int)""")

    	try:
    	    self.curs.execute("""CREATE TABLE Stock (
                                    id text, quote int, timestamp int)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Stock""")
            self.curs.execute("""CREATE TABLE Stock (
                                id text, quote int, timestamp int)""")
        self.conn.commit()

    # call like: select_records("Users", "id,balance", "id='jim' AND balance=200")
    def select_records(self, values, table, constraints):
        self.curs.execute("""SELECT %s FROM %s WHERE %s""" % (values_format, table, constraints_format))
        result = self.curs.fetchall()

        if len(result) > 1:
            print 'more than one value returned!!!?'

        return result


    def insert_record(self, table, columns, values):
        self.curs.execute("""INSERT INTO %s (%s) VALUES (%s)""" % (table, columns, values))

    def update_record(self, table, values, constraints):
        self.curs.execute("""UPDATE %s SET %s WHERE %s)""" % (table, values, constraints))
