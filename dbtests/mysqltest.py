import MySQLdb

connection = None

# load db configuration and credentials
from dbconfig_sqlite import *


def initialize():
    """
    Initializes the connection to the storage backend. Call this before using 
    any other function in this module."""
    global connection    
    connection = MySQLdb.connect(SERVER_ADDRESS, USERNAME, PASSWORD, DATABASE)
    

def query_test():
    c = connection.cursor()
    c.execute("SELECT * FROM test2")
    result = c.fetchall()
    for row in result:
        print(row)


def insert_test(value1, value2):
    c = connection.cursor()
    c.execute("INSERT INTO test2 (a, b) VALUES (%s, %s)", (value1, value2))
    connection.commit()


initialize()
query_test()
insert_test(5, 8)

