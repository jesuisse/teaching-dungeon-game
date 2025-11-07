import pygame

from graphics2d import *
from lineedit import InputLine
from graphics2d.scenetree.label import Label
from graphics2d.scenetree.canvascontainer import CanvasContainer
import graphics2d.drawing as _draw




class PopupWindow(CanvasContainer):
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

    def layout(self):
        child = self.children[0]
        child.size = Vector2(self.size)
        child.position = Vector2(0, 0)
        self.notify_children_resized()

    def on_draw(self, surface):
        s = surface.get_size()
        mysurface = pygame.Surface(s, pygame.SRCALPHA)
        mysurface.fill(self.bgcolor)
        surface.blit(mysurface)
        super().on_draw(surface)


class InputPrompt(PopupWindow):
    """
    Provides a popup window that displays a prompt and waits for input
    """

    # signal definitions
    accepted = InputLine.accepted
    aborted = InputLine.aborted

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
            self.prompt = "Say something:"
             

        self.label = Label(color=self.color, font=self.font, text=self.prompt,flags=Label.ALIGN_CENTERED)
        self.inputline = InputLine(color=self.color, bgcolor=Color(20, 20, 20), font=self.font, max_size=(None, 35), flags=InputLine.ALIGN_CENTERED)
        
        self.listen(self.inputline, InputLine.accepted, self.on_accepted)
        self.listen(self.inputline, InputLine.aborted, self.on_aborted)
        
        hbox = HBoxContainer(min_size=(100, 30), max_size=(None, 30))
        hbox.add_child(self.label)
        hbox.add_child(self.inputline)
        
        #labelsize = _draw.get_text_size(self.font, self.prompt)
        #inputsize = [self.size[0]-labelsize[0]-3*self.padding[0], self.size[1]-2*self.padding[1]]
        #inputpos = Vector2(labelsize[0]+2*self.padding[0], self.padding[1])
        #self.inputline = InputLine(color=self.color, bgcolor=Color(20, 20, 20), font=self.font, position=inputpos, size=inputsize)        
        self.add_child(hbox)

    def grab_focus(self):
        self.inputline.grab_focus()
       

    def get_text(self):
        return self.inputline.gettext()

    def on_draw(self, surface):
        super().on_draw(surface)

    def _close_popup(self):
        self.inputline.release_focus()        
        get_scenetree().clear_modal(self)
        parent = self.parent()
        if parent:
            parent.remove_child(self)
        
    def on_accepted(self, item, text):    
        self._close_popup()
        self.emit(InputPrompt.accepted, text)    

    def on_aborted(self, item):        
        self._close_popup()
        self.emit(InputPrompt.aborted)



def open_textbox(label, callback) -> InputPrompt:
    wsize = get_window_size()
    tsize = Vector2(700, 100)
    tpos = Vector2(wsize.x/2 - tsize.x/2, wsize.y/2 - tsize.y/2)
    font = get_font(get_default_fontname(), 24)
    prompt = InputPrompt(prompt=label, size=Vector2(700, 100), color=Color(150,150,150), bgcolor=Color(25, 25, 25, 200),
            font=font, position=tpos, padding=(20, 20))    
    listen(prompt, InputPrompt.accepted, lambda x, text: callback(prompt, text))    
    tree = get_scenetree()
    # TODO: we need to add a SceneItem node in between so the child won't get layouted if the tree root is a layouting 
    # container!
    tree.root.add_child(prompt)
    tree.make_modal(prompt)    
    prompt.grab_focus()
    prompt.request_redraw()
    listen(tree.root, CanvasContainer.resized, lambda x, w, h: center_textbox(prompt))
    return prompt

def center_textbox(box):
    wsize = get_window_size()
    tsize = Vector2(700, 100)    
    box.position = Vector2(wsize.x/2 - tsize.x/2, wsize.y/2 - tsize.y/2)