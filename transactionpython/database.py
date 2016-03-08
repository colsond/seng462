import psycopg2
from psycopg2.pool import ThreadedConnectionPool


class Database:

    def __init__(self, host, port, dbname, dbuser, dbpass, minconn=1, maxconn=1):
        # Thread pool
        self.pool = ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            host=host,
            database=dbname,
            user=dbuser,
            password=dbpass,
            port=port
        )
        # Base connection for initialization
        self.conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=dbuser,
            password=dbpass,
            port=port
        )
        self.curs = self.conn.cursor()

    def initialize(self):
        # Initialize Database, Recreate Tables
        try:
            self.curs.execute("""CREATE TABLE Users (
                                user_id text, balance int)""")
        except:
    	    self.conn.rollback()
    	    self.curs.execute("""DROP TABLE Users""")
    	    self.curs.execute("""CREATE TABLE Users (
                                    user_id text, balance int)""")
        self.conn.commit()

    	try:
    	    self.curs.execute("""CREATE TABLE Stock (
                                    stock_id text, user_id text, amount int)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Stock""")
            self.curs.execute("""CREATE TABLE Stock (
                                    stock_id text, user_id text, amount int)""")
        self.conn.commit()

        try:
            self.curs.execute("""CREATE TABLE PendingTrans (
                                    type text, user_id text, stock_id text, amount int, timestamp int)""")

        except Exception as e:
            print e
            self.conn.rollback()
            self.curs.execute("""DROP TABLE PendingTrans""")
            self.curs.execute("""CREATE TABLE PendingTrans (
                                    type text, user_id text, stock_id text, amount int, timestamp int)""")
        self.conn.commit()

        try:
            self.curs.execute("""CREATE TABLE Trigger (
                                    type text, user_id text, stock_id text, amount integer, trigger integer)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Trigger""")
            self.curs.execute("""CREATE TABLE Trigger (
                                    type text, user_id text, stock_id text, amount integer, trigger integer)""")
        self.conn.commit()

    # Return a Database Connection from the pool
    def get_connection(self):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        return DatabaseConnection(connection, cursor)

    def close_connection(self, connection):
	self.pool.putconn(connection)

class DatabaseConnection:

    def __init__(self, connection, cursor):
        self.conn = connection
        self.conn.autocommit = True
        self.curs = cursor

        # call like: select_record("Users", "id,balance", "id='jim' AND balance=200")
    def select_record(self, values, table, constraints):
        try:
            self.curs.execute("""SELECT %s FROM %s WHERE %s""" % (values, table, constraints))
        except Exception as e:
            print e
        result = self.curs.fetchall()
        print result
        # Format to always return a tuple of the single record, with each value.
        if len(result) > 1:
            print 'more than one value returned!!!?'
            return (None,None)
        elif len(result) == 0:
            return (None,None)
        else:
            return result[0]

    def insert_record(self, table, columns, values):
        try:
            self.curs.execute("""INSERT INTO %s (%s) VALUES (%s)""" % (table, columns, values))
        except Exception as e:
            print e

    def update_record(self, table, values, constraints):
        try:
            self.curs.execute("""UPDATE %s SET %s WHERE %s""" % (table, values, constraints))
        except Exception as e:
            print e

    def delete_record(self, table, constraints):
        try:
            self.curs.execute("""DELETE FROM %s WHERE %s""" % (table, constraints))
        except Exception as e:
            print e
