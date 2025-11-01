"""
This module is the interface between the actual game and it's storage backend. When we
decide to switch from sqlite to another storage backend, all we have to do is switch out
this module.
"""
import sqlite3

connection = None

def initialize():
    """
    Initializes the connection to the storage backend. Call this before using 
    any other function in this module."""
    global connection
    connection = sqlite3.connect("resources/default_db.db")

def finalize():
    """
    Closes the connection to the storage backend. Call this before the application
    exits.
    """
    connection.close()



def store_new_room(name, tilemap):  
    """
    Store a new room in the database and return its assigned ID
    """  
    cur = connection.cursor()
    # wir verwenden im Moment immer den Tile Atlas mit der ID 1 und die Grösse 15x15    
    QUERY = "INSERT INTO Rooms (name, atlas_id, size_x, size_y) VALUES (?, ?, ?, ?)"        
    cur.execute(QUERY, [name, 1, 15, 15])
    room_id = cur.lastrowid
    
    QUERY = "INSERT INTO TileMap (tileid, tileindex, roomid) VALUES (?, ?, ?)"
    for index, tileid in enumerate(tilemap.tilemap):
        if tileid is None:
            # Wir speichern keine leeren Felder ab
            continue
        cur.execute(QUERY, [tileid, index, room_id])
    connection.commit()

    return room_id


def store_room(roomid, tilemap):
    """
    Store the tilemap data for an existing room
    """
    QUERY = "DELETE FROM TileMap WHERE roomid = ?"
    cur = connection.cursor()
    cur.execute(QUERY, [roomid])
    QUERY = "INSERT INTO TileMap (tileid, tileindex, roomid) VALUES (?, ?, ?)"
    for index, tileid in enumerate(tilemap.tilemap):
        if tileid:
            # we only save non-empty tiles
            cur.execute(QUERY, [tileid, index, roomid])
    connection.commit()



def load_tilemap_data(roomid) -> list:
    """
    Load the tilemap data for a given room. Returns a list of tile IDs, 
    with None for empty tiles.
    """
    cur = connection.cursor()
    QUERY = "SELECT tileid, tileindex FROM TileMap WHERE roomid = ?"
    cur.execute(QUERY, (roomid,))
    row = cur.fetchone()
    room_size = get_room_size(roomid)
    if not room_size:
        raise ValueError(f"Room {roomid} does not have a size defined")
        
    tiles = [None]*room_size[0]*room_size[1]
    while row:
        tiles[row[1]] = row[0]
        row = cur.fetchone()
    return tiles


def get_room_size(roomid) -> tuple:
    """
    Get the size of a room. Returns a (size_x, size_y) tuple
    """
    cur = connection.cursor()
    QUERY = "SELECT size_x, size_y FROM Rooms WHERE id = ?"
    cur.execute(QUERY, (roomid,))
    row = cur.fetchone()
    if row:
        return (row[0], row[1])
    else:
        raise ValueError(f"Room {roomid} does not exist in storage backend")
    





