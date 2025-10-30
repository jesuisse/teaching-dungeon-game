
from graphics2d import *

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
        
    def on_draw(self, surface):
        surface.draw_image(self.image, (0, 0))
