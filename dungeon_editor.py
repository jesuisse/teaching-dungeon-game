import sys, os.path, pygame.transform
sys.path.append(os.path.join(sys.path[0], ".."))

from graphics2d import *
from lineedit import InputLine
from popups import InputPrompt


# Diese Konstanten legen die Grösse des Grafikfensters fest
WIDTH = 1060
HEIGHT = 900

RESIZABLE = False


tilegrid_size = (15, 15)

tile_image = None
grid_rect = Rect(20, 20, 720, 720)
tileset_rect = Rect(750, 20, 6*48, 15*48)
tile_size = (48, 48)
tilemap = [None] * 15 * 15

selected_tile = 14
hovered_tile = -1

selected_cell = -1
hovered_cell = -1

# 1 = drawing, -1 = erasing
draw_mode = 0

textinput = None

active_popup = None


def on_draw():
    # Wird aufgerufen, um den Inhalt des Grafikfensters neu zu zeichnen

    # Grösse des Grafikfensters ausfindig machen
    breite, höhe = get_window_size()
    
    draw_filled_rect((0, 0), (breite, höhe), Color(70, 70, 70))
    
    draw_filled_rect(grid_rect.topleft, grid_rect.size, Color(40, 40, 40))
    
    draw_tiles()
    draw_tile_grid()
    draw_tileset_grid()
   
    # Rendert Text
    fontname = get_default_fontname()
    fontsize = 30
    draw_text(fontname, fontsize, "Dare to do peachy things!", (40, 800), Color("orange"))

    # Render an image
    if tile_image:
        draw_surface(tile_image, (750, 20))

    draw_selection_state()

    if active_popup:
        active_popup.on_draw(get_window_surface())
    

def draw_tile_grid():    
    """
    Zeichnet das Raster, auf dem Tiles angeordnet werden
    """    
    draw_rect(grid_rect.topleft, grid_rect.size, Color(50, 50, 50), 2)

    gridcolor = Color(70, 70, 70)
    for i in range(16):
        x = grid_rect.left + i * tile_size[0]
        y = grid_rect.top + i * tile_size[1]
        draw_line((x, grid_rect.top), (x, grid_rect.bottom), gridcolor, 1)
        draw_line((grid_rect.left, y), (grid_rect.right, y), gridcolor, 1)

def draw_tileset_grid():
    """
    Zeichnet die Tile-Palette
    """
    draw_filled_rect(tileset_rect.topleft, tileset_rect.size, Color(40, 40, 40))    
    draw_rect(tileset_rect.topleft, tileset_rect.size, Color(50, 50, 50), 2)

    gridcolor = Color(70, 70, 70)
    for i in range(7):
        x = tileset_rect.left + i * tile_size[0]
        draw_line((x, tileset_rect.top), (x, tileset_rect.bottom), gridcolor, 1)
    for i in range(15):
        y = tileset_rect.top + i * tile_size[1]
        draw_line((x, tileset_rect.top), (x, tileset_rect.bottom), gridcolor, 1)
        draw_line((tileset_rect.left, y), (tileset_rect.right, y), gridcolor, 1)

def draw_tiles():
    for i in range(tilegrid_size[0]*tilegrid_size[1]):
        dest_rect = get_cell_rect(i)
        tileidx = tilemap[i]        
        if tileidx is None:
            continue        
        src_rect = get_tile_rect(tileidx)
        src_rect.left -= tileset_rect.left
        src_rect.top -= tileset_rect.top       
        draw_surface(tile_image, dest_rect.topleft, src_rect)


def draw_selection_state():
    
    if hovered_tile >= 0:
        hover_color = YELLOW
        rect = get_tile_rect(hovered_tile)        
        draw_rect(rect.topleft, rect.size, hover_color, 2)

    if selected_tile >= 0:
        select_color = Color(255, 255, 255)
        rect = get_tile_rect(selected_tile)
        draw_rect(rect.topleft, rect.size, select_color, 2)

    if hovered_cell >= 0:
        hover_color = YELLOW
        rect = get_cell_rect(hovered_cell)        
        draw_rect(rect.topleft, rect.size, hover_color, 2)


def get_cell_index(point):
    relx = point[0] - grid_rect.left
    rely = point[1] - grid_rect.top

    x = int(relx / tile_size[0])
    y = int(rely / tile_size[1])
    return y*tilegrid_size[0]+x

def get_cell_rect(tile_index):
    x = tile_index % tilegrid_size[0]
    y = int(tile_index / tilegrid_size[0])
    return Rect(grid_rect.left + x*tile_size[0], grid_rect.top + y*tile_size[1], tile_size[0], tile_size[1])



def get_tile_index(point):
    relx = point[0] - tileset_rect.left
    rely = point[1] - tileset_rect.top

    x = int(relx / tile_size[0])
    y = int(rely / tile_size[1])
    return y*6+x

def get_tile_rect(tile_index):
    x = tile_index % 6
    y = int(tile_index / 6)
    return Rect(tileset_rect.left + x*tile_size[0], tileset_rect.top + y*tile_size[1], tile_size[0], tile_size[1])

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



def on_input(event):
    global hovered_tile, selected_tile, hovered_cell, draw_mode
    
    if active_popup:
        if let_popup_handle_event(event):
            return
 
    if event.type == MOUSEMOTION:
        mouse_coords = event.pos
            
        if tileset_rect.collidepoint(mouse_coords):
            tile_idx = get_tile_index(mouse_coords)
            hovered_tile = tile_idx
            request_redraw()
            return
        
        elif grid_rect.collidepoint(mouse_coords):
            cell_idx = get_cell_index(mouse_coords)
            hovered_cell = cell_idx
            if draw_mode == 1:
                tilemap[hovered_cell] = selected_tile               
            elif draw_mode == 2:
                tilemap[hovered_cell] = None
            request_redraw()
            return

        if hovered_tile != -1:
            hovered_tile = -1            
            request_redraw()
        if hovered_cell != -1:
            hovered_cell = -1
            request_redraw()

    if event.type == MOUSEBUTTONDOWN:
        if hovered_tile != -1:
            selected_tile = hovered_tile
            request_redraw()  
        elif hovered_cell != -1 and selected_tile != -1:
            if event.button == 1:
                draw_mode = 1
                tilemap[hovered_cell] = selected_tile
            elif event.button == 3:
                draw_mode = 2
                tilemap[hovered_cell] = None
        
    
    if event.type == MOUSEBUTTONUP:
        if draw_mode:
            draw_mode = 0





def on_ready():
    # Wird aufgerufen, wenn das Grafik-Framework bereit ist, unmittelbar vor dem Start der Event Loop.

    # Lade ein Bild
    global tile_image, textinput, active_popup
    try:
        tile_image = load_image("resources/ohmydungeon_v1.1.png")
        size = (tile_image.get_width()*3, tile_image.get_height()*3)
        tile_image = pygame.transform.scale(tile_image, size)

    except FileNotFoundError:
        print("Tileset image not found...")
        sys.exit(1)

    # Setze Fenstertitel
    set_window_title("Dungeon Editor")

    font = get_font(get_default_fontname(), 24)
    textinput = InputLine(text="Hello World", 
                        position=Vector2(30, 350), 
                        size=Vector2(700, 120),
                        padding=[10, 40],
                        bgcolor=Color(30, 30, 30, 180),
                        color=Color(150,150,150),
                        font=font)
    prompt = InputPrompt(prompt="Name:", size=Vector2(700, 120), color=Color(150,150,150), bgcolor=Color(30, 30, 30, 200),
            font=font, position=Vector2(30, 150))

    tree = get_scenetree()
    tree.set_root(prompt)

    #active_popup = prompt
    textinput.focused = True



# Konfiguriert und startet das Grafikprogramm.
go()
