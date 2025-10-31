from graphics2d import *
import graphics2d.drawing as _draw

class TileAtlas(CanvasRectAreaItem):

    def __init__(self, **kwargs):

        if 'tilesize' in kwargs:
            self.tilesize = kwargs['tilesize']
        else:
            self.tilesize = (48, 48)

        if 'atlassize' in kwargs:
            self.atlassize = kwargs['atlassize']
        else:
            self.atlassize = (1, 1)

        if 'size' not in kwargs:
            kwargs['size'] = [self.tilesize[0] * self.atlassize[0], self.tilesize[1] * self.atlassize[1]]
        
        if 'image' in kwargs:
            self.image = kwargs['image']
        else:
            self.image = None

        self.hovered_tile = -1
        self.selected_tile = -1
               

        super().__init__(**kwargs)


    def get_tile_index(self, local_point):            
        relx = local_point[0]
        rely = local_point[1]

        x = int(relx / self.tilesize[0])
        y = int(rely / self.tilesize[1])
        return y*self.atlassize[0]+x

    def get_tile_rect(self, tile_index):
        x = tile_index % self.atlassize[0]
        y = int(tile_index / self.atlassize[0])
        return Rect(x*self.tilesize[0], y*self.tilesize[1], self.tilesize[0], self.tilesize[1])


    def get_tile_image(self, index):
        """
        Returns the tile image for index.
        DO NOT DRAW ONTO THE SURFACE! IT REFERENCES THE ORIGINAL TILE!
        """        
        return self.image.subsurface(self.get_tile_rect(index))


    def set_hovered_tile(self, index):
        self.hovered_tile = index
        self.request_redraw()

    def set_selected_tile(self, index):
        self.selected_tile = index
        self.request_redraw()


    def on_draw(self, surface):        
        self._draw_tileset_grid(surface)
        self._draw_state(surface)
    
    def _draw_tileset_grid(self, surface):
        """
        Zeichnet die Tile-Palette
        """
        pos = Vector2(0,0) #self.position
        _draw.draw_filled_rect(surface, Rect(pos, self.size), Color(40, 40, 40))
        _draw.draw_rect(surface, Rect(pos, self.size), Color(50, 50, 50), 2)
        surface.blit(self.image, pos)

        gridcolor = Color(70, 70, 70)
        for i in range(self.atlassize[0]+1):
            x = pos.x + i * self.tilesize[0]
            _draw.draw_line(surface, (x, pos.y), (x, pos.y+self.size[1]), gridcolor, 1)
        for i in range(self.atlassize[1]+1):
            y = pos.y + i * self.tilesize[1]
            _draw.draw_line(surface, (pos.x, y), (pos.x+self.size[0], y), gridcolor, 1)

    def _draw_state(self, surface):
        if self.hovered_tile != -1:
            hover_color = YELLOW
            rect = self.get_tile_rect(self.hovered_tile)            
            _draw.draw_rect(surface, rect, hover_color, 2)

        if self.selected_tile != -1:
            select_color = Color(255, 255, 255)
            rect = self.get_tile_rect(self.selected_tile)            
            _draw.draw_rect(surface, rect, select_color, 2)