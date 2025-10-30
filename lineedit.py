import pygame
import unicodedata
from graphics2d import *

class InputLine(CanvasRectAreaItem):
    """
    A simple input field supporting basic
    editing commands
    """

    # The following k_methods take care of key presses. They are configured
    # in the handlers dictionary.

    def k_left(self, event):
        if self.pos > 0:
            self.pos -= 1

    def k_right(self, event):
        if self.pos < len(self.text):
            self.pos += 1

    def k_home(self, event):
        self.pos = 0

    def k_end(self, event):
        self.pos = len(self.text)

    def k_delete(self, event):
        if self.pos < len(self.text):
            del self.text[self.pos]

    def k_backspace(self, event):
        if self.pos > 0 and self.pos <= len(self.text):
            self.pos -= 1
            del self.text[self.pos]

    handlers = {
       pygame.K_LEFT : k_left,
       pygame.K_RIGHT : k_right,
       pygame.K_HOME : k_home,
       pygame.K_END : k_end,
       pygame.K_BACKSPACE : k_backspace,
       pygame.K_DELETE : k_delete,
       pygame.K_RETURN : None,
    }

    def __init__(self, **kwargs): 
        super().__init__(**kwargs)

        if "text" in kwargs:
            self.text = kwargs['text']
        else:
            self.text = []
      
        if "padding" in kwargs:
            self.padding = kwargs['padding']
        else:
            self.padding = [5, 2]    

        if "font" in kwargs:
            self.font = kwargs['font']
        else:
            self.font = get_font(get_default_fontname())

        if "color" in kwargs:
            self.color = kwargs['color']
        else:
            self.color = Color(3, 3, 3)    


        if "bgcolor" in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = Color(0xa8, 0xa8, 0xa8)    
                

        self.pos = 0        
        self.dirty = True
        self.focused = False

        if type(self.text) is str:
            self.text = list(self.text)


    def set_dirty(self):
        request_redraw()
        self.dirty = True

    def layout(self, dimension):
        """
        if self.policy[dimension] == GUI.SHRINK:
            ts = self.font.size(self.gettext())
            self.size[dimension] = ts[dimension] + 2 * self.padding[dimension]
        """
        self.set_dirty()

    def gettext(self):
        return ''.join(self.text)

    def render_text(self):
        return self.font.render(self.gettext(), True, self.color)

    def on_draw(self, surface):
        mysurface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        rendered = self.render_text()
        mysurface.fill(self.bgcolor)
        mysurface.blit(rendered, self.padding, (0,0, self.size[0]-2*self.padding[0], self.size[1]-2*self.padding[1]))
        self.paintCursor(mysurface)
        surface.blit(mysurface, self.position)
        self.dirty = False

    def paintCursor(self, surface):
        if self.focused:
            s = ''.join(self.text[0:self.pos])
            dims = self.font.size(s)
            pygame.draw.line(surface, self.color, (self.padding[0]+dims[0], self.padding[1]), (self.padding[0]+dims[0], self.padding[1]+dims[1]-1), 2)

    def getKeyHandler(self, k):
        if k in InputLine.handlers:
            return InputLine.handlers[k]
        else:
            return None

    def on_input(self, event):
        """
        if event.type == GOTFOCUS:
            print("Got focus")
        if event.type == LOSTFOCUS:
            print("Lost focus")
        """
        print(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            #GUI.set_focus(self)
            print("Mouse press in Inputline")
        if event.type == pygame.KEYDOWN:
            k = event.key
            handler = self.getKeyHandler(k)
            if handler:
                handler(self, event)
                self.set_dirty()
            elif len(event.unicode) == 1 and unicodedata.category(event.unicode) != 'Cc':
                self.text.insert(self.pos, event.unicode)
                self.pos += 1
                self.set_dirty()
            print(''.join(self.text), len(self.text), self.pos)
