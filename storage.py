import sqlite3

connection = None

def db_connect():
    global connection
    connection = sqlite3.connect("resources/default_db.db")


def store_as_new_room(name, tilemap):    
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
    QUERY = "DELETE FROM TileMap WHERE roomid = ?"
    cur = connection.cursor()
    cur.execute(QUERY, [roomid])
    QUERY = "INSERT INTO TileMap (tileid, tileindex, roomid) VALUES (?, ?, ?)"
    for index, tileid in enumerate(tilemap.tilemap):
        if tileid is None:
            # Wir speichern keine leeren Felder ab
            continue
        cur.execute(QUERY, [tileid, index, roomid])
    connection.commit()



def load_tilemap_data(roomid):
    cur = connection.cursor()
    QUERY = "SELECT tileid, tileindex FROM TileMap WHERE roomid = ?"
    cur.execute(QUERY, [roomid,])
    row = cur.fetchone()
    # Im Moment verewnden wir eine fest codierte Grösse 15x15
    tiles = [None]*15*15
    while row:
        tiles[row[1]] = row[0]
        row = cur.fetchone()
    return tiles





