import sys, os.path, pygame.transform
sys.path.append((os.path.join(sys.path[0], "graphics2d")))

from graphics2d import *
from popups import open_textbox
from graphics2d.scenetree.label import Label
from graphics2d.scenetree.canvascontainer import CanvasContainer
from tileatlas import TileAtlas
from tilemap import TileMap
import storage

# Defines scaling of the tile atlas images. If you are using this
# application on a low resolution monitor, change this to 1.5, 2 or 2.5
# as needed.
ATLAS_SCALE = 2

# Initial size of the window
WIDTH = 1060
HEIGHT = 800

RESIZABLE = True
ALWAYS_REDRAW = False

## Currently we only use a single Tile Atlas (with the atlas id 1 in the storage backend)
ATLAS_ID = 1

# Size of the room in tiles
MAPSIZE = (15, 15)

tile_image = None

tile_atlas = None
tilemap = None

status_label = None

# Storage id of the room that's currently being edited
active_room_id = None

def on_draw():
    # Give the window a background color
    get_window_surface().fill(Color(70, 70, 70))


def on_input(event):     
    # handle keyboard shortcuts for loading/saving rooms
    if event.type == KEYDOWN and event.key == pygame.K_n:
        open_textbox("Raumname:", on_roomname_entered)
    
    if event.type == KEYDOWN and event.key == pygame.K_l:
        prompt = open_textbox("Raumid:", on_load_id_entered)
        

    if event.type == KEYDOWN and event.key == pygame.K_s:
        storage.store_room(active_room_id, tilemap)


def on_roomname_entered(prompt, text):
    global active_room_id    
    active_room_id = storage.store_as_new_room(text, tilemap)
    status_label.set_text(f"Created new room with id {active_room_id}")
    tree = get_scenetree()    
    tree.request_redraw_all()


def on_load_id_entered(prompt, text):
    global active_room_id
    try:
        active_room_id = int(text)
        tilemap_data = storage.load_tilemap_data(active_room_id)
        if tilemap_data:
            tilemap.tilemap = tilemap_data
            tilemap.request_redraw()
    except ValueError:
        pass
    finally:
        status_label.set_text(f"Current room has id {active_room_id}")
        tree = get_scenetree()
        tree.request_redraw_all()
    


def initialize_gui():
    global tile_image, tile_atlas, tilemap, status_label

    path = "resources/ohmydungeon_v1.1.png"
    try:
        tile_image = load_image(path)
        size = (tile_image.get_width()*ATLAS_SCALE, tile_image.get_height()*ATLAS_SCALE)
        tile_image = pygame.transform.scale(tile_image, size)

    except FileNotFoundError:
        print(f"Tile Atlas image not found at {path}...")
        sys.exit(1)

    set_window_title("Dungeon Editor")

    # Atlas aus Bild erzeugen und positionieren
    tile_atlas = TileAtlas(tilesize=(16*ATLAS_SCALE,16*ATLAS_SCALE), atlassize=(6,15), image=tile_image, flags=TileAtlas.ALIGN_CENTERED)

    # Die tilemap erzeugen 
    tilemap = TileMap(mapsize=MAPSIZE, atlas=tile_atlas, flags=TileMap.ALIGN_CENTERED) 
    
    tree = get_scenetree()
    
    status_label = Label(name="label", text="Current room is new", flags=Label.ALIGN_CENTERED)

    pc = PanelContainer(name="panelcontainer", bg_color=Color(30, 30, 30), borders=(0, 10), max_size=(None, 40))
    pc.add_child(status_label)
    statuspanel = HBoxContainer(name="statuspanel", separation=5)    
    statuspanel.add_child(pc)
    statuspanel.max_size = (None, 20)

    content = HBoxContainer(name="content-hbox", separation=5)
    content.add_child(tilemap)    
    content.add_child(tile_atlas)
    
    root = VBoxContainer(name="root", separation=0)
    root.size = Vector2(WIDTH, HEIGHT)
    root.add_child(statuspanel)
    root.add_child(content)
        
    tree.set_root(root)


def on_ready():
    global ATLAS_SCALE

    # Adjust tile size for higher resolution monitors
    resolution = get_monitor_resolution()
    if min(resolution.x, resolution.y) > 1000:
        ATLAS_SCALE = 3
    
    storage.initialize()
    initialize_gui()


def on_exit():    
    storage.finalize()


# Starts the framework and its event loop
go()