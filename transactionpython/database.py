import psycopg2

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

    def select_records(self, table="Users"):
        self.curs.execute("""SELECT * FROM %s""" % table)
        return self.curs.fetchall()


    def insert_record(self, user_id, balance):
        self.curs.execute("""INSERT INTO Users (id, balance) VALUES ('%s', %s)""" % (user_id, balance))
        # insert query
