import pygame
import unicodedata
from graphics2d import *
from graphics2d.scenetree.sceneitem import Signal
import graphics2d.drawing as _draw

class InputLine(CanvasRectAreaItem):
    """
    A simple input field supporting basic
    editing commands
    """

    # signal definitions    
    accepted = Signal("accepted", "text")
    aborted = Signal("aborted")

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

    def k_accept(self, event):
        self.emit(InputLine.accepted, self.gettext())
    
    def k_abort(self, event):
        self.emit(InputLine.aborted)

    handlers = {
       pygame.K_LEFT : k_left,
       pygame.K_RIGHT : k_right,
       pygame.K_HOME : k_home,
       pygame.K_END : k_end,
       pygame.K_BACKSPACE : k_backspace,
       pygame.K_DELETE : k_delete,
       pygame.K_RETURN : k_accept,
       pygame.K_ESCAPE : k_abort
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

        ts = _draw.get_text_size(self.font, "M")
        self.min_size = (ts[0] + 2*self.padding[0], ts[1] + 2 * self.padding[1])


        self.pos = 0        
        self.dirty = True
        self.focused = False

        if type(self.text) is str:
            self.text = list(self.text)


    def set_dirty(self):
        self.request_redraw()
        self.dirty = True
   

    def gettext(self):
        return ''.join(self.text)

    def render_text(self):
        return self.font.render(self.gettext(), True, self.color)

    def on_draw(self, surface):        
        rendered = self.render_text()
        surface.fill(self.bgcolor)
        posy = (self.size[1]-2*self.padding[1] - rendered.get_height())/2
        surface.blit(rendered, (self.padding[0], posy), (0,0, self.size[0]-2*self.padding[0], self.size[1]-2*self.padding[1]))
        self.paintCursor(surface)        
        self.dirty = False

    def paintCursor(self, surface):
        if self.focused:
            s = ''.join(self.text[0:self.pos])
            dims = self.font.size(s)
            posy = (self.size[1]-2*self.padding[1] - dims[1])/2
            _draw.draw_line(surface, (self.padding[0]+dims[0], posy), (self.padding[0]+dims[0], posy+dims[1]-1), self.color, 2)

    def getKeyHandler(self, k):
        if k in InputLine.handlers:
            return InputLine.handlers[k]
        else:
            return None

    def on_gui_input(self, event): 
                      
        if event.type == pygame.MOUSEBUTTONDOWN:
            #GUI.set_focus(self)
            pass
        if event.type == pygame.KEYDOWN:
            k = event.key
            handler = self.getKeyHandler(k)
            if handler:
                handler(self, event)
                self.set_dirty()
        if event.type == pygame.TEXTINPUT:
            self.text.insert(self.pos, event.text)
            self.pos += 1
            self.set_dirty()

        """
        elif len(event.unicode) == 1 and unicodedata.category(event.unicode) != 'Cc':
            self.text.insert(self.pos, event.unicode)
            self.pos += 1
            self.set_dirty()
        """
