import MySQLdb
from dbconfig_joel import SERVER_ADDRESS, USERNAME, PORT, PASSWORD, DATABASE
connection = None


def initialize():
    """
    Initializes the connection to the storage backend. Call this before using 
    any other function in this module."""
    global connection    
    connection = MySQLdb.connect(SERVER_ADDRESS, USERNAME, PASSWORD, DATABASE, PORT)

def insert_dump(sqltext):
    c = connection.cursor()
    c.execute(sqltext)

def read_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data

initialize()


dump = read_file("../resources/dungeon_dump.sql")
insert_dump(dump)



