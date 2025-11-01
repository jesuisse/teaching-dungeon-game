import sys, os.path, pygame.transform
sys.path.append((os.path.join(sys.path[0], "graphics2d")))

from graphics2d import *
from lineedit import InputLine
from popups import InputPrompt
from tileatlas import TileAtlas
from tilemap import TileMap
import storage

# Legt fest, wie stark die Atlas-Bilder hochskaliert werden. 
ATLAS_SCALE = 3

# Diese Konstanten legen die Grösse des Grafikfensters fest
WIDTH = 1060
HEIGHT = 800

RESIZABLE = False
ALWAYS_REDRAW = False

## Currently we only use a single Tile Atlas (with the atlas id 1 in the storage backend)
ATLAS_ID = 1

# Grösse des editierbaren Raumes in Tiles
MAPSIZE = (15, 15)

tile_image = None
grid_rect = None
tileset_rect = None


# 1 = drawing, -1 = erasing
draw_mode = 0

tile_atlas = None
tilemap = None

# Storage id of the room that's currently being edited
active_room_id = None

def on_draw():
    # Give the window a background color
    get_window_surface().fill(Color(70, 70, 70))


def to_local(canvasitem, pos):
    return (pos[0]-canvasitem.position[0], pos[1]-canvasitem.position[1])


def on_input(event):
    global draw_mode    
 
    if event.type == MOUSEMOTION:
        mouse_coords = event.pos

        mouse_in_tile_atlas = tile_atlas.get_bbox().collidepoint(mouse_coords)
        mouse_in_tilemap = tilemap.get_bbox().collidepoint(mouse_coords)

        # Check whether the mouse is still hovering and disable the hover if not
        if tile_atlas.hovered_tile != -1 and not mouse_in_tile_atlas:
            tile_atlas.set_hovered_tile(-1)
        if tilemap.hovered_cell != -1 and not mouse_in_tilemap:
            tilemap.set_hovered_cell(-1)

        # Handle hovering and drawing tiles
        if mouse_in_tile_atlas:
            tile_idx = tile_atlas.get_tile_index(to_local(tile_atlas, mouse_coords))
            tile_atlas.set_hovered_tile(tile_idx)            
                    
        elif mouse_in_tilemap:
            cell_idx = tilemap.get_cell_index(to_local(tilemap, mouse_coords))
            tilemap.set_hovered_cell(cell_idx)
            if draw_mode == 1:
                tilemap.set_tile(tilemap.hovered_cell, tile_atlas.selected_tile)
            elif draw_mode == 2:
                tilemap.set_tile(tilemap.hovered_cell, None)            
    
    if event.type == MOUSEBUTTONDOWN:
        if tile_atlas.hovered_tile != -1:
            tile_atlas.set_selected_tile(tile_atlas.hovered_tile)
        elif tilemap.hovered_cell != -1 and tile_atlas.selected_tile != -1:
            if event.button == 1:
                draw_mode = 1
                tilemap.set_tile(tilemap.hovered_cell, tile_atlas.selected_tile)
            elif event.button == 3:
                draw_mode = 2
                tilemap.set_tile(tilemap.hovered_cell, None)        
    
    # stop drawing or erasing tiles
    if event.type == MOUSEBUTTONUP:
        if draw_mode:
            draw_mode = 0

    # handle keyboard shortcuts for loading/saving rooms
    if event.type == KEYDOWN and event.key == pygame.K_n:
        create_new_room()
    
    if event.type == KEYDOWN and event.key == pygame.K_l:
        load_room()

    if event.type == KEYDOWN and event.key == pygame.K_s:
        store_room()



def create_new_room():
    open_textbox("Raumname:", on_roomname_entered)

def store_room():
    storage.store_room(active_room_id, tilemap)

def load_room():
    open_textbox("Raumid:", on_load_id_entered)


def on_roomname_entered(prompt):
    global active_room_id
    name = prompt.get_text()
    active_room_id = storage.store_as_new_room(name, tilemap)
    print(f"Created new room with id {active_room_id}")
    tree = get_scenetree()
    tree.root.remove_child(prompt)

def on_load_id_entered(prompt):
    global active_room_id
    active_room_id = int(prompt.get_text())
    tilemap_data = storage.load_tilemap_data(active_room_id)
    if tilemap_data:
        tilemap.tilemap = tilemap_data
        tilemap.request_redraw()
    tree = get_scenetree()
    tree.root.remove_child(prompt)

    
def open_textbox(label, callback):
    font = get_font(get_default_fontname(), 24)
    prompt = InputPrompt(prompt=label, size=Vector2(700, 100), color=Color(150,150,150), bgcolor=Color(25, 25, 25, 200),
            font=font, position=Vector2(30, 150), padding=(20, 20), callback=lambda: callback(prompt))
    tree = get_scenetree()    
    tree.root.add_child(prompt)
    tree.make_modal(prompt)


def initialize_gui():
    global tile_image, tile_atlas, tilemap

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
    tile_atlas = TileAtlas(position=Vector2(750, 20), tilesize=(16*ATLAS_SCALE,16*ATLAS_SCALE), atlassize=(6,15), image=tile_image)

    # Die tilemap erzeugen 
    tilemap = TileMap(position=Vector2(20, 20), mapsize=MAPSIZE, atlas=tile_atlas) 
    
    tree = get_scenetree()
    root = CanvasItem(position=Vector2(0, 0), name="root")
    root.add_child(tile_atlas)
    root.add_child(tilemap)
        
    tree.set_root(root)



def on_ready():
    # Wird aufgerufen, wenn das Grafik-Framework bereit ist, unmittelbar vor dem Start der Event Loop.
    storage.initialize()
    initialize_gui()

def on_exit():
    # Wird aufgerufen, wenn das Grafik-Framework beendet wird, unmittelbar vor dem Verlassen der Event Loop.
    storage.finalize()


# Konfiguriert und startet das Framework
go()
