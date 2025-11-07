import sys, os.path

BASEDIR=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(BASEDIR, "graphics2d"))

from graphics2d import *
from popups import open_textbox


RESIZABLE = True
WIDTH = 1024
HEIGHT = 800


def on_ready():
    open_textbox(label="Hello World", callback=lambda x:print(x))


go()
