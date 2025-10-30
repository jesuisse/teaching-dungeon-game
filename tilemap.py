import pygame

from graphics2d import *


class Tilemap(CanvasRectAreaItem):

    def __init__(self, **kwargs):

        if 'tilesize' in kwargs:
            self.tilesize = kwargs['tilesize']
        else:
            self.tilesize = (48, 48)

        if 'mapsize' in kwargs:
            self.mapsize = kwargs['mapsize']
        else:
            self.mapsize = (15, 15)

        if 'size' not in kwargs:
            kwargs['size'] = [self.tilesize[0] * self.mapsize[0], self.tilesize[1] * self.mapsize[1]]
        
        if 'tilemap' in kwargs:
            self.tilemap = kwargs['tilemap']
        else:
            self.tilemap = [None] * self.mapsize[0] * self.mapsize[1]

        if 'atlas' in kwargs:
            self.atlas = kwargs['atlas']
        else:
            self.atlas = None

        super().__init__(**kwargs)


    def get_cell_index(local_point):
        """
        Given a point in local coordinates, returns the index of the cell at this point
        """
        relx = local_point[0]
        rely = local_point[1]

        x = int(relx / self.tilesize[0])
        y = int(rely / self.tilesize[1])
        return y*self.mapsize[0]+x

    def get_cell_rect(tile_index):
        """
        Given a tile index, returns the boundary rect of the cell
        """
        x = tile_index % self.mapsize[0]
        y = int(tile_index / self.mapsize[0])
        return Rect(self.position.x + x*self.tilesize[0], self.position.y + y*self.tilesize[1], self.tilesize[0], self.tilesize[1])


    def draw_tile_grid():
        """
        Zeichnet das Raster, auf dem Tiles angeordnet werden
        """    
        draw_rect(self.position, self.size, Color(50, 50, 50), 2)

        gridcolor = Color(70, 70, 70)
        for i in range(self.mapsize[0]):
            x = self.position.x + i * self.tilesize[0]
            draw_line((x, self.position.y), (x, self.position.y+self.size[1]), gridcolor, 1)
        for i in range(self.mapsize[1]):
            y = self.position.y + i * self.tilesize[1]            
            draw_line((self.position.x, y), (self.position.x+self.size[0], y), gridcolor, 1)


    def draw_tiles():
        if self.tileimage is None:
            return
        
        for i in range(self.mapsize[0]*self.mapsize[1]):
            dest_rect = get_cell_rect(i)
            tileidx = self.tilemap[i]
            if tileidx is None:
                continue        
            src_rect = get_tile_rect(tileidx)
            src_rect.left -= tileset_rect.left
            src_rect.top -= tileset_rect.top       
            draw_surface(self.tileimage, dest_rect.topleft, src_rect)