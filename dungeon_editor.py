import sys, os.path, pygame.transform
sys.path.append(os.path.join(sys.path[0], ".."))

from graphics2d import *
from lineedit import InputLine
from popups import InputPrompt
from tileatlas import TileAtlas
from tilemap import TileMap
import storage


# Diese Konstanten legen die Grösse des Grafikfensters fest
WIDTH = 1060
HEIGHT = 900

RESIZABLE = False
ALWAYS_REDRAW = False

## Im Moment ist der verwendete Tile-Atlas immer der mit ID 1
ATLAS_ID = 1


tilegrid_size = (15, 15)

tile_image = None
grid_rect = Rect(20, 20, 720, 720)
tileset_rect = Rect(750, 20, 6*48, 15*48)
tile_size = (48, 48)


# 1 = drawing, -1 = erasing
draw_mode = 0

tile_atlas = None
tilemap = None

active_room_id = None

def on_draw():
    # Wird aufgerufen, um den Inhalt des Grafikfensters neu zu zeichnen

    # Grösse des Grafikfensters ausfindig machen
    breite, höhe = get_window_size()
    
    draw_filled_rect((0, 0), (breite, höhe), Color(70, 70, 70))
       
    # Rendert Text
    fontname = get_default_fontname()
    fontsize = 30
    draw_text(fontname, fontsize, "Dare to do peachy things!", (40, 800), Color("orange"))
    


def to_local(canvasitem, pos):
    return (pos[0]-canvasitem.position[0], pos[1]-canvasitem.position[1])

def on_input(event):
    global draw_mode
    
 
    if event.type == MOUSEMOTION:
        mouse_coords = event.pos

        if tile_atlas.hovered_tile != -1:
            tile_atlas.set_hovered_tile(-1)
        if tilemap.hovered_cell != -1:
            tilemap.set_hovered_cell(-1)

        if tileset_rect.collidepoint(mouse_coords):
            tile_idx = tile_atlas.get_tile_index(to_local(tile_atlas, mouse_coords))
            tile_atlas.set_hovered_tile(tile_idx)            
            return
        
        elif grid_rect.collidepoint(mouse_coords):
            cell_idx = tilemap.get_cell_index(to_local(tilemap, mouse_coords))
            tilemap.set_hovered_cell(cell_idx)
            if draw_mode == 1:
                tilemap.set_tile(tilemap.hovered_cell, tile_atlas.selected_tile)
            elif draw_mode == 2:
                tilemap.set_tile(tilemap.hovered_cell, None)            
            return
           

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
        
    
    if event.type == MOUSEBUTTONUP:
        if draw_mode:
            draw_mode = 0


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
    print("Neuer Raum mit id", active_room_id, "erzeugt")
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



def on_ready():
    # Wird aufgerufen, wenn das Grafik-Framework bereit ist, unmittelbar vor dem Start der Event Loop.

    # Lade ein Bild
    global tile_image, textinput, active_popup, tile_atlas, tilemap
    try:
        tile_image = load_image("resources/ohmydungeon_v1.1.png")
        size = (tile_image.get_width()*3, tile_image.get_height()*3)
        tile_image = pygame.transform.scale(tile_image, size)

    except FileNotFoundError:
        print("Tileset image not found...")
        sys.exit(1)

    # Verbinde dich mit Speicher-Backend (Datenbank)
    storage.db_connect()


    # Setze Fenstertitel
    set_window_title("Dungeon Editor")

    # Atlas aus Bild erzeugen und positionieren
    tile_atlas = TileAtlas(position=Vector2(750, 20), tilesize=(48,48), atlassize=(6,15), image=tile_image)

    # Die tilemap erzeugen 
    tilemap = TileMap(position=Vector2(20, 20), mapsize=(15,15), atlas=tile_atlas) 
    
    tree = get_scenetree()

    root = CanvasItem(position=Vector2(0, 0), name="root")
    root.add_child(tile_atlas)
    root.add_child(tilemap)
        
    tree.set_root(root)
    

# Konfiguriert und startet das Grafikprogramm.
go()
