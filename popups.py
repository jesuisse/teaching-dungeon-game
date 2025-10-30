import pygame

from graphics2d import *
from lineedit import InputLine
import graphics2d.drawing as _draw


class PopupWindow(CanvasRectAreaItem):
    """
    A Popup Window. By default, it has no decoration, it's just
    a flat background with a bgcolor.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if "bgcolor" in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = Color(80, 80, 80, 200)

        if "padding" in kwargs:
            self.padding = kwargs['padding']
        else:
            self.padding = [20, 10]

    def on_draw(self, surface):
        mysurface = pygame.Surface(self.size, flags=pygame.SRCALPHA)        
        mysurface.fill(self.bgcolor)
        surface.blit(mysurface, self.position)

class InputPrompt(PopupWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if "color" in kwargs:
            self.color = kwargs['color']
        else:
            self.color = Color(120, 120, 120)

        if "font" in kwargs:
            self.font = kwargs['font']
        else:
            self.font = get_font(get_default_font_name())

        if "prompt" in kwargs:
            self.prompt = kwargs['prompt']
        else:
            self.prompt = ""

        labelsize = _draw.get_text_size(self.font, self.prompt)
        inputsize = [self.size[0]-labelsize[0], self.size[1]]
        self.inputline = InputLine(color=self.color, bgcolor=self.bgcolor, font=self.font, position=[labelsize[0], 0], size=inputsize)


    def on_draw(self, surface):
        super().on_draw(surface)        
        labelsize = _draw.get_text_size(self.font, self.prompt)
        rendered_text = _draw.draw_text(self.font, self.prompt, self.color, antialias=True)
        
        pos = Vector2(self.position.x + self.padding[0], self.position.y + self.size[1] / 2 - labelsize[1]/2)
        
        surface.blit(rendered_text, pos)

        self.inputline.on_draw(surface)

    def on_input(self, event):
        self.inputline.on_input(event)

        





