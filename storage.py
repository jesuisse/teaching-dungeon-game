"""
This module is the interface between the actual game and it's storage backend. When we
decide to switch from sqlite to another storage backend, all we have to do is switch out
this module.
"""
import sqlite3
from datetime import datetime


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

    QUERY = "INSERT INTO ObjectMap (objectid, objectindex, roomid) VALUES (?, ?, ?)"
    for index, objectid in enumerate(tilemap.objectmap):
        if objectid is None:
            continue
        cur.execute(QUERY, [objectid, index, room_id])
    
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
        if tileid is None:
            # we only save non-empty tiles
            cur.execute(QUERY, [tileid, index, roomid])
    QUERY = "INSERT INTO ObjectMap (objectid, objectindex, roomid) VALUES (?, ?, ?)"
    for index, objectid in enumerate(tilemap.objectmap):
        if objectid is None:
            continue
        cur.execute(QUERY, [objectid, index, roomid])
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

    QUERY = "SELECT objectid, objectindex FROM ObjectMap WHERE roomid = ?"
    cur.execute(QUERY, (roomid,))
    row = cur.fetchone()

    objects = [None]*room_size[0]*room_size[1]
    while row:
        objects[row[1]] = row[0]
        row = cur.fetchone()

    return (tiles, objects)


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


def get_room_connections(roomid) -> list:
    """
    Returns (tileid, targetroomid, targettileid) tuples of all connections 
    to other rooms from the given room.
    """
    cur = connection.cursor()
    QUERY = "SELECT tileid, targetroomid, targettileid FROM room_connections WHERE roomid = ?"
    cur.execute(QUERY, (roomid,))
    rows = cur.fetchall()
    if rows is None:
        return rows
    else:
        return []
    


def create_room_connection(roomid, tileid, targetroomid, targettileid):
    cur = connection.cursor()
    parameters = {
        'roomid': roomid, 
        'tileid': tileid, 
        'targetroomid': targetroomid, 
        'targettileid': targettileid
        }
    cur.execute("INSERT INTO room_connections (roomid, tileid, targetroomid, targettileid) VALUES (:roomid, :tileid, :targetroomid, :targettileid)", parameters)
    connection.commit()


def add_object_to_room(roomid, tileid, objectid):
    """
    Adds the given object ID to the given tile in the given room.
    """
    # Mockup implementation (does nothing)
    pass


def remove_object_from_room(roomid, tileid):
    """
    Removes any object from the given tile in the given room.
    """
    # Mockup implementation (does nothing)
    pass


def get_tile_object_ids() -> list:
    """
    Returns a list of all tile object IDs in the storage backend.

    A tile object is an object in the tile atlas that can be set 
    above a tile in the tilemap.
    """
    
    # Mockup implementation
    return [44, 45, 46, 47, 48, 49, 50, 54]


def get_walkable_tile_ids() -> list:
    """
    Returns a list of all walkable tile IDs in the storage backend.
    """

    cur = connection.cursor()
    QUERY = "SELECT tile_id FROM TileInfo WHERE atlas_id = ? AND property = ?"
    cur.execute(QUERY, (1, "walkable",))
    row = cur.fetchone()
    tileids = []
    while row:
        tileids.append(row[0])
        row = cur.fetchone()
    
    return tileids



def get_player_list() -> list:
    """
    Returns a list of all player IDs ever seen in the game.
    """
    # Mockup implementation
    return [1, 2, 3, 4, 5]



def get_player_info(playerid) -> dict:
    """
    Returns a dictionary with player information for the given player ID.
    """
    # Mockup implementation
    return {
        'player_id': playerid,
        'name': 'Player'+str(playerid),
        'room_id': 1,               # the room id where the player currently is
        'position': (7, 7),         # the player's current position in room_id
        'object_id': 54,            # the tile object ID representing the player
        'last_seen': "2025-11-04 12:00:00" # last seen timestamp
    }


def register_player(playername, skin) -> int:
    """
    Returns the player id of the player with the given name.
    Creates a new player if the given name does not exist yet,
    spawning them in room 2.
    """
    QUERY = "SELECT player_id FROM players WHERE name = ?"
    cur = connection.cursor()
    cur.execute(QUERY, (playername,))
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        room_id = 2
        position = 99
        last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Mit hilfe von ChatGPT
        QUERY = "INSERT INTO players (name, room_id, position, object_id, last_seen) VALUES (?, ?, ?, ?, ?)"
        cur = connection.cursor()
        cur.execute(QUERY, [playername, room_id, position, skin])
        connection.commit()
        player_id = cur.lastrowid
        return player_id



def get_player_location(playerid) -> tuple:
    """
    Returns the current location of the given player as (roomid, tileid)
    """
    # Mockup implementation always returns room 1, tile 83
    return (1, 83)


def set_player_location(playerid, roomid, tileid):
    """
    Sets the current location of the given player.
    """
    # Mockup implementation (does nothing)
    pass


def get_player_inventory_objects(playerid) -> list:
    """
    Returns a list of object IDs in the inventory of the given player.
    Note: The same objects can be present in the inventory multiple
    times.
    """
    cur = connection.cursor()
    QUERY = "SELECT objectid FROM Inventory WHERE playerid = ?"
    cur.execute(QUERY, (playerid,))
    rows = cur.fetchall()
    return [row[0] for row in rows]
    


def add_object_to_player_inventory(playerid, objectid):
    """
    Adds the given object ID to the inventory of the given player.
    """
    # Mockup implementation (does nothing)
    pass


def remove_object_from_player_inventory(playerid, objectid):
    """
    Removes one instance of the given object ID from the inventory
    of the given player.
    """
    # Mockup implementation (does nothing)
    pass