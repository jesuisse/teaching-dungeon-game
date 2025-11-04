import pygame

from graphics2d import *
import graphics2d.drawing as _draw


class TileMap(CanvasRectAreaItem):

    def __init__(self, **kwargs):

        if 'mapsize' in kwargs:
            self.mapsize = kwargs['mapsize']
        else:
            self.mapsize = (15, 15)

        if 'tilemap' in kwargs:
            self.tilemap = kwargs['tilemap']
        else:
            self.tilemap = [None] * self.mapsize[0] * self.mapsize[1]

        if 'atlas' in kwargs:
            self.atlas = kwargs['atlas']
        else:
            self.atlas = None

        if 'tilesize' in kwargs:
            self.tilesize = kwargs['tilesize']
        elif self.atlas is not None:
            self.tilesize = self.atlas.tilesize
        else:
            self.tilesize = (48, 48)
        
        if 'size' not in kwargs:
            kwargs['size'] = [self.tilesize[0] * self.mapsize[0] + 2, self.tilesize[1] * self.mapsize[1] + 2]
        
        self.hovered_cell = -1
        self.draw_mode = 0

        super().__init__(**kwargs)
        self.min_size = Vector2(self.size)
        self.max_size = Vector2(self.size)


    def get_cell_index(self, local_point):
        """
        Given a point in local coordinates, returns the index of the cell at this point
        """
        if local_point[0] >= self.mapsize[0] * self.tilesize[0]:
            return -1

        relx = local_point[0]
        rely = local_point[1]

        x = int(relx / self.tilesize[0])
        y = int(rely / self.tilesize[1])
        return y*self.mapsize[0]+x

    def get_cell_rect(self, tile_index):
        """
        Given a tile index, returns the boundary rect of the cell
        """
        x = tile_index % self.mapsize[0]
        y = int(tile_index / self.mapsize[0])
        return Rect(x*self.tilesize[0],y*self.tilesize[1], self.tilesize[0], self.tilesize[1])

    def set_tile(self, index, tile_index):
        self.tilemap[index] = tile_index
        self.request_redraw()

    def set_hovered_cell(self, index):
        self.hovered_cell = index
        self.request_redraw()

    def on_draw(self, surface):
        surface.fill(Color(40, 40, 40))        
        self._draw_tiles(surface)
        self._draw_tile_grid(surface)
        self._draw_selection_state(surface)


    def _draw_tile_grid(self, surface):
        """
        Zeichnet das Raster, auf dem Tiles angeordnet werden
        """    
        pos = Vector2(0, 0)

        _draw.draw_rect(surface, Rect(pos, self.size), Color(50, 50, 50), 2)
        
        gridcolor = Color(70, 70, 70)
        for i in range(self.mapsize[0]):
            x = pos.x + i * self.tilesize[0]
            _draw.draw_line(surface, (x, pos.y), (x, pos.y+self.size[1]), gridcolor, 1)
        for i in range(self.mapsize[1]):
            y = pos.y + i * self.tilesize[1]            
            _draw.draw_line(surface, (pos.x, y), (pos.x+self.size[0], y), gridcolor, 1)


    def _draw_tiles(self, surface):
        if self.atlas is None:
            return
        
        for i in range(self.mapsize[0]*self.mapsize[1]):
            dest_rect = self.get_cell_rect(i)
            tileidx = self.tilemap[i]
            if tileidx is None:
                continue            
            surface.blit(self.atlas.get_tile_image(tileidx), dest_rect.topleft)
    
    def _draw_selection_state(self, surface):
        if self.hovered_cell != -1:
            hover_color = YELLOW
            rect = self.get_cell_rect(self.hovered_cell)        
            _draw.draw_rect(surface, rect, hover_color, 2)

    def _to_local(self, pos):
        return (pos[0]-self.position[0], pos[1]-self.position[1])

    def on_gui_input(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.hovered_cell != -1 and self.atlas.get_selected_tile() != -1:
                if event.button == 1:
                    self.draw_mode = 1
                    self.set_tile(self.hovered_cell, self.atlas.get_selected_tile())
                elif event.button == 3:
                    self.draw_mode = 2
                    self.set_tile(self.hovered_cell, None)
        elif event.type == MOUSEMOTION:
            cell_idx = self.get_cell_index(self._to_local(event.pos))
            self.set_hovered_cell(cell_idx)
            if self.draw_mode == 1:
                self.set_tile(self.hovered_cell, self.atlas.get_selected_tile())
            elif self.draw_mode == 2:
                self.set_tile(self.hovered_cell, None)
        elif event.type == MOUSEBUTTONUP:
            if self.draw_mode:
                self.draw_mode = 0