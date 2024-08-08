import pygame
import random
from utils import *

class Tile(pygame.sprite.Sprite):
    all_tiles = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2, cm, group: str):
        super().__init__()
        self.surface = pygame.Surface([50, 50])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect(pos, [50, 50])
        Tile.all_tiles.add(self)
        match group:
            case 'static':
                cm.add_static(self)
            case 'dynamic':
                cm.add_dynamic(self)
    def render(self, surface):
        surface.blit(self.surface, self.rect)

class Wall(Tile):
    all_walls = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2, cm):
        super().__init__(pos, cm, 'static')
        self.surface.fill("white")
        Wall.all_walls.add(self)

class TunnelEntry(Tile):
    def __init__(self, pos: pygame.Vector2, tunnel, direction: pygame.Vector2, cm):
        super().__init__(pos, cm, 'static')
        self.tunnel = tunnel
        self.direction = direction
        self.poses = [pos, pos - direction * 50]
        if direction == pygame.Vector2(-1, 0) or direction == pygame.Vector2(0, -1):
            self.next_cell = tunnel.relations[0]
        else:
            self.next_cell = tunnel.relations[1]
    def render(self, surface):
        if self.tunnel.merge is not None:
            return
        if self.tunnel.opened and not self.tunnel.closed_down:
            self.rect.topleft = self.poses[0]
            self.surface.fill("black")
        else:
            self.rect.topleft = self.poses[1]
            if self.tunnel.breakable and not self.tunnel.closed_down:
                self.surface.fill("bisque")
            else:
                self.surface.fill("grey")
        surface.blit(self.surface, self.rect)

class Chest(Tile):
    def __init__(self, cell, pos: pygame.Vector2, loot_table):
        super().__init__(pygame.Vector2(0, 0), cell.cm, 'dynamic')
        self.rect.center = cell.pos + pos
        self.loot_table = loot_table
        self.cell = cell
        self.opened = False
    def render(self, surface):
        if self.opened:
            self.surface.fill("darkgoldenrod")
        else:
            self.surface.fill("darkgoldenrod1")
        surface.blit(self.surface, self.rect)

class Exit(Tile):
    def __init__(self, cell, pos: pygame.Vector2):
        super().__init__(pygame.Vector2(0, 0), cell.cm, 'dynamic')
        self.surface.fill("lime")
        self.rect.center = cell.pos + pos
        self.func = self.exit
    def exit(self, player):
        glob_var["exited"] = True