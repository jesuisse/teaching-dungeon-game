
from graphics2d import *
from graphics2d.scenetree.notification import Notification
import graphics2d.drawing as _draw
import pygame
import storage

from tilemap import TileMap

DEFAULT_PLAYER_SKIN = 54
DEFAULT_PLAYER_POSITION = 7*15+7

class GameWorld(TileMap):
    
    player_moved = Notification("player_moved", "new_tile_index")
    portal_entered = Notification("portal_entered", "target_roomid", "target_tileindex")
    object_taken = Notification("object_taken", "tile_index", "object_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.walkable_tiles = kwargs.get('walkable_tiles', [])
        self.player_skin = kwargs.get('player_skin', DEFAULT_PLAYER_SKIN)
        self.player_position = kwargs.get('player_position', DEFAULT_PLAYER_POSITION)
        self.player_id = None
        self.room_id = None
        self.portals = []
        self.players = []


    def set_room(self, roomid):
        """
        Sets the current room id
        """
        self.room_id = roomid
    

    def set_player(self, player_id):
        """
        Sets the current player
        """
        self.player_id = player_id


    def set_player_position(self, player_position):
        """
        Sets the player position
        """
        self.player_position = player_position


    def set_players(self, players : list):
        self.players = []
        for player in players:
            # ignore our own self
            if player[0] == self.player_id:
                continue
            self.players.append(player)
        self.request_redraw()


    def set_portals(self, portals : list):
        """
        Sets the portal mapping for this room.
        Each portal is a (tileindex, targetroom, targettileindex) tuple
        """
        self.portals = portals
        

    def on_draw(self, surface):
        surface.fill(Color(40, 40, 40))
        self._draw_tiles(surface)
        self._draw_objects(surface)
        self._draw_other_players(surface)
        self._draw_player(surface)
        self._draw_portals(surface)
        #self._draw_tile_grid(surface)
        #self._draw_selection_state(surface)


    def _draw_player(self, surface):
        if self.player_position < 0 or self.player_position >= self.mapsize[0]*self.mapsize[1]:
            return
        
        tile_rect = self.get_cell_rect(self.player_position)
        tile_image = self.atlas.get_tile_image(self.player_skin)
        if tile_image:
            surface.blit(tile_image, Vector2(tile_rect.x, tile_rect.y))

    def _draw_other_players(self, surface):
        for player in self.players:
            tile_rect = self.get_cell_rect(player[1])
            # TODO: Use correct skin, not just the default
            tile_image = self.atlas.get_tile_image(self.player_skin)
            if tile_image:
                surface.blit(tile_image, Vector2(tile_rect.x, tile_rect.y))



    def _draw_portals(self, surface):
        for portal in self.portals:
            tile_index = portal[0]
            portal_color = Color(100, 100, 200)
            rect = self.get_cell_rect(tile_index)        
            _draw.draw_rect(surface, rect, portal_color, 2)


    def can_walk_to(self, tile_index):
        """
        Returns True if the player can walk to the given tile index
        """
        if tile_index < 0 or tile_index >= self.mapsize[0]*self.mapsize[1]:
            return False
        tileid = self.tilemap[tile_index]
        return tileid in self.walkable_tiles or self.is_portal(tile_index)
    

    def is_portal(self, tile_index):
        """
        Returns True if the given tile index is a portal to another room
        """
        if tile_index < 0 or tile_index >= self.mapsize[0]*self.mapsize[1]:
            return False
        
        for portal in self.portals:
            if portal[0] == tile_index:
                return True
        return False


    def notify_portal_entered(self):
        if not self.is_portal(self.player_position):
            return 
        for portal in self.portals:
            if portal[0] == self.player_position:
                target_roomid = portal[1]
                target_tileindex = portal[2]
                self.emit(GameWorld.portal_entered, target_roomid, target_tileindex)
                return


    def notify_player_moved(self):
        self.emit(GameWorld.player_moved, self.player_position)

    def notify_object_taken(self):
        self.emit(GameWorld.object_taken, self.player_position, self.get_object(self.player_position))


    def get_object(self, tile_index):
        return self.objectmap[tile_index]


    def on_input(self, event):
        moves = {pygame.K_w: -self.mapsize[0], pygame.K_s: self.mapsize[0],
                 pygame.K_a: -1, pygame.K_d: 1
                 }
        pickup = {pygame.K_t: 1}
        if event.type == KEYDOWN:
            # handles movement in the four cardinal directions
            if event.key in moves:
                new_position = self.player_position + moves[event.key]
                if self.can_walk_to(new_position):
                    self.player_position = new_position
                    self.notify_player_moved()
                    self.request_redraw()
                if self.is_portal(self.player_position):
                    self.notify_portal_entered()
            # handles picking up objects
            if event.key in pickup:
                if self.get_object(self.player_position):
                    self.notify_object_taken()
                    self.objectmap[self.player_position] = None
