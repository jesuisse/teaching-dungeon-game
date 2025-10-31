import sys, os.path, pygame.transform
sys.path.append(os.path.join(sys.path[0], ".."))

from graphics2d import *
from lineedit import InputLine
from popups import InputPrompt
from tileatlas import TileAtlas
from tilemap import TileMap


# Diese Konstanten legen die Grösse des Grafikfensters fest
WIDTH = 1060
HEIGHT = 900

RESIZABLE = False
ALWAYS_REDRAW = False


tilegrid_size = (15, 15)

tile_image = None
grid_rect = Rect(20, 20, 720, 720)
tileset_rect = Rect(750, 20, 6*48, 15*48)
tile_size = (48, 48)


# 1 = drawing, -1 = erasing
draw_mode = 0

textinput = None

active_popup = None

tile_atlas = None
tilemap = None


def on_draw():
    # Wird aufgerufen, um den Inhalt des Grafikfensters neu zu zeichnen

    # Grösse des Grafikfensters ausfindig machen
    breite, höhe = get_window_size()
    
    draw_filled_rect((0, 0), (breite, höhe), Color(70, 70, 70))
       
    # Rendert Text
    fontname = get_default_fontname()
    fontsize = 30
    draw_text(fontname, fontsize, "Dare to do peachy things!", (40, 800), Color("orange"))


    if active_popup:
        active_popup.on_draw(get_window_surface())



def let_popup_handle_event(event):
    if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
        rect = Rect(active_popup.position, active_popup.size)
        if rect.collidepoint(event.pos):
            active_popup.on_input(event)
            # consume mouse event
            return True
        else:
            # pass on event 
            return False     
    elif event.type == KEYDOWN or event.type == KEYUP:
        active_popup.on_input(event)
        # consume event
        return True
    
    return False

def to_local(canvasitem, pos):
    return (pos[0]-canvasitem.position[0], pos[1]-canvasitem.position[1])

def on_input(event):
    global draw_mode
    
    if active_popup:
        if let_popup_handle_event(event):
            return
 
    if event.type == MOUSEMOTION:
        mouse_coords = event.pos
            
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

        if tile_atlas.hovered_tile != -1:
            tile_atlas.set_hovered_tile(-1)
        if tilemap.hovered_cell != -1:
            tilemap.set_hovered_cell(-1)
            

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

    # Setze Fenstertitel
    set_window_title("Dungeon Editor")

    # Atlas aus Bild erzeugen und positionieren
    tile_atlas = TileAtlas(position=Vector2(750, 20), tilesize=(48,48), atlassize=(6,15), image=tile_image)

    # Die tilemap erzeugen 
    tilemap = TileMap(position=Vector2(20, 20), mapsize=(15,15), atlas=tile_atlas) 


    font = get_font(get_default_fontname(), 24)
    
    prompt = InputPrompt(prompt="Name:", size=Vector2(700, 100), color=Color(150,150,150), bgcolor=Color(25, 25, 25, 200),
            font=font, position=Vector2(30, 150), padding=(20, 20))

    tree = get_scenetree()

    root = CanvasItem(position=Vector2(0, 0), name="root")
    root.add_child(tile_atlas)
    root.add_child(tilemap)
    
    root.add_child(prompt)
    tree.make_modal(prompt)

    tree.set_root(root)
    
   


# Konfiguriert und startet das Grafikprogramm.
go()
