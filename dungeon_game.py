import sys, os.path, pygame.transform

BASEDIR=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(BASEDIR, "graphics2d"))

from graphics2d import *
import graphics2d.constants as G2D
from graphics2d.scenetree.canvascontainer import FreeLayoutContainer, CanvasContainer 
from graphics2d.scenetree.label import Label
from graphics2d.scenetree.notification import listen, Notification
from popups import open_inputbox
from tileatlas import TileAtlas
from tilemap import TileMap
from gameworld import GameWorld
import storage

RESIZABLE = True
WIDTH = 1024
HEIGHT = 800

ATLAS_SCALE = 2

## Currently we only use a single Tile Atlas (with the atlas id 1 in the storage backend)
ATLAS_ID = 1

# Size of the room in tiles
MAPSIZE = (15, 15)

tile_image = None

gameworld = None

walkable_tiles = []

active_room_id = None

# id of the player controlling this instance
player_id = 0

def load_room(roomid):
    tilemap_data = storage.load_tilemap_data(roomid)
    if tilemap_data:
        gameworld.tilemap = tilemap_data[0]
        gameworld.objectmap = tilemap_data[1]
        gameworld.room_id = roomid

        portals = storage.get_room_connections(roomid)
        gameworld.set_portals(portals)

        gameworld.request_redraw()
        


def initialize_gui():
    global status_label

    set_window_title("Dungeon Game v0.6")

    objectids = storage.get_tile_object_ids()
    walkable_tiles = storage.get_walkable_tile_ids()

    status_label = Label(name="label", text="Hi. I'm Dungeon Game Version 0.6. Use WASD for player movement.", flags=G2D.V_ALIGN_CENTERED)

    pc = PanelContainer(name="panelcontainer", bg_color=Color(30, 30, 30), borders=(0, 0), max_size=(None, 40), flags=G2D.H_EXPAND)
    pc.add_child(status_label)
    statuspanel = HBoxContainer(name="statuspanel", separation=5)    
    statuspanel.add_child(pc)
    statuspanel.max_size = (None, 20)
    
    flc = FreeLayoutContainer(name="root", size=get_window_size(), bgcolor = Color(20, 20, 25))

    vbox = VBoxContainer(name="vbox", separation=0)
    vbox.size = Vector2(WIDTH, HEIGHT)
    vbox.add_child(statuspanel)
    vbox.add_child(gameworld)

    flc.add_child(vbox)

    tree = get_scenetree()        
    tree.set_root(flc)

    def resizing(x, w, h):
        vbox.on_resized(w, h)
        #center_map(w, h)

    listen(flc, CanvasContainer.resized, resizing)


def on_portal_entered(gameworld, target_roomid, target_tileindex):
    print(f"Portal entered to room {target_roomid} at tile {target_tileindex}")
    load_room(target_roomid)
    gameworld.set_player_position(target_tileindex)
    

def on_player_moved(gameworld, new_player_position):
    storage.set_player_location(gameworld.player_id, gameworld.room_id, new_player_position)
    print(new_player_position)


def on_object_taken(gameworld, object_position, object_id):
    storage.add_object_to_player_inventory(gameworld.player_id, object_id)
    storage.remove_object_from_room(gameworld.room_id, object_position)

time_count = 0
def on_update(dt):
    global time_count
    # dt is in ms (milliseconds)
    time_count += dt
    if time_count < 100:
        return
    
    time_count = 0
    # do this every 100 ms (eg 10 times per second)
    players = storage.get_players_at(gameworld.room_id)
    objects = storage.get_objects_at(gameworld.room_id)
    gameworld.set_players(players)
    gameworld.set_objects(objects)

        




def on_ready():
    global ATLAS_SCALE, gameworld, tile_atlas, tile_image, player_id

    # Adjust tile size for higher resolution monitors
    resolution = get_monitor_resolution()
    if min(resolution.x, resolution.y) > 1000:
        ATLAS_SCALE = 3
    
    storage.initialize()
    
    path = "resources/ohmydungeon_v1.1.png"
    try:
        tile_image = load_image(path)
        size = (tile_image.get_width()*ATLAS_SCALE, tile_image.get_height()*ATLAS_SCALE)
        tile_image = pygame.transform.scale(tile_image, size)

    except FileNotFoundError:
        print(f"Tile Atlas image not found at {path}...")
        sys.exit(1)

    objectids = storage.get_tile_object_ids()
    walkable_tiles = storage.get_walkable_tile_ids()

    tile_atlas = TileAtlas(tilesize=(16*ATLAS_SCALE,16*ATLAS_SCALE), atlassize=(6,15), image=tile_image)
    gameworld = GameWorld(mapsize=MAPSIZE, atlas=tile_atlas, objectids=objectids, walkable_tiles=walkable_tiles,
                          flags=G2D.H_ALIGN_CENTERED) 
    
    listen(gameworld, GameWorld.portal_entered, on_portal_entered)
    listen(gameworld, GameWorld.player_moved, on_player_moved)
    listen(gameworld, GameWorld.object_taken, on_object_taken)


    player_id = storage.register_player("Berserker", 50)
    gameworld.set_player(player_id)
    print(player_id, "ist meine Spieler-ID")
    
    room_id, player_position = storage.get_player_location(player_id)
    load_room(room_id)
    gameworld.set_player_position(player_position)

    initialize_gui()

    #open_inputbox("Hello World", lambda x, text:print(text))

 
go()
