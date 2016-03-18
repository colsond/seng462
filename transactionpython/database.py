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
                                user_id text, balance bigint)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Users""")
            self.curs.execute("""CREATE TABLE Users (
                                    user_id text, balance bigint)""")
        self.conn.commit()

        try:
            self.curs.execute("""CREATE TABLE Stock (
                                    stock_id text, user_id text, amount bigint)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Stock""")
            self.curs.execute("""CREATE TABLE Stock (
                                    stock_id text, user_id text, amount bigint)""")
        self.conn.commit()

        try:
            self.curs.execute("""CREATE TABLE PendingTrans (
                                    type text, user_id text, stock_id text, amount bigint, timestamp bigint)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE PendingTrans""")
            self.curs.execute("""CREATE TABLE PendingTrans (
                                    type text, user_id text, stock_id text, amount bigint, timestamp bigint)""")
        self.conn.commit()

        try:
            self.curs.execute("""CREATE TABLE Trigger (
                                    type text, user_id text, stock_id text, amount bigint, trigger bigint)""")
        except:
            self.conn.rollback()
            self.curs.execute("""DROP TABLE Trigger""")
            self.curs.execute("""CREATE TABLE Trigger (
                                    type text, user_id text, stock_id text, amount bigint, trigger bigint)""")
        self.conn.commit()

        print "DB Initialized"

    # Return a Database Connection from the pool
    def get_connection(self):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        return connection, cursor

    def close_connection(self, connection):
        self.pool.putconn(connection)

        # call like: select_record("Users", "id,balance", "id='jim' AND balance=200")
    def select_record(self, values, table, constraints):
        connection, cursor = self.get_connection()

        try:
            command = """SELECT %s FROM %s WHERE %s""" % (values, table, constraints)
            cursor.execute(command)
            connection.commit()
        except Exception as e:
            print 'PG Select error: ' + str(e)

        result = cursor.fetchall()
        self.close_connection(connection)

        # Format to always return a tuple of the single record, with each value.
        if len(result) > 1:
            print 'PG Select returned more than one value.'
            return (None,None)
        elif len(result) == 0:
            return (None,None)
        else:
            return result[0]

    def insert_record(self, table, columns, values):
        connection, cursor = self.get_connection()

        try:
            command = """INSERT INTO %s (%s) VALUES (%s)""" % (table, columns, values)
            cursor.execute(command)
            connection.commit()
        except Exception as e:
            print 'PG Insert error: ' + str(e)

        self.close_connection(connection)

    def update_record(self, table, values, constraints):
        connection, cursor = self.get_connection()

        try:
            command = """UPDATE %s SET %s WHERE %s""" % (table, values, constraints)
            cursor.execute(command)
            connection.commit()
        except Exception as e:
            print 'PG Update error: %s \n table=%s values=%s constraints=%s command=%s' % (str(e), table, values, constraints, command)

        self.close_connection(connection)

    def delete_record(self, table, constraints):
        connection, cursor = self.get_connection()

        try:
            command = """DELETE FROM %s WHERE %s""" % (table, constraints)
            cursor.execute(command)
            connection.commit()
        except Exception as e:
            print 'PG Delete error: ' + str(e)

        self.close_connection(connection)
