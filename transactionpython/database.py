class Database:

    def __init__(self, dbname, dbuser, dbpass):
        self.conn = connect(
            # host=conf_hostname,
            database=conf_dbname,
            user=conf_dbuser,
            password=conf_dbpass,
            # port=conf_dbport
        )
        self.conn.autocommit = True
        self.curs = self.conn.cursor()

    def initialize(self):
        ## Will need to change these based 
        try:
            self.curs.execute("""CREATE TABLE User (
                                id text, balance int)""")
            self.curs.execute("""CREATE TABLE Stock (
                                id text, quote int, timestamp int)""")
        except:
            self.conn.rollback()
            self.curs.execute("DROP TABLE User")
            self.curs.execute("""CREATE TABLE User (
                                id text, balance int)""")
            self.curs.execute("""CREATE TABLE Stock (
                                id text, quote int, timestamp int)""")
        self.conn.commit()

    def select_records(self, table="User"):
        self.cursor.execute("""SELECT * FROM %s""" % table)
        return self.cursor.fetchall()


    def insert_record(self, user_id, balance):
        self.cursor.execute("""INSERT INTO User VALUES (%s, %s)""" % (user_id, balance))
        # insert query