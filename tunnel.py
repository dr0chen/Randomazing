import pygame
from object import *

all_tunnels = pygame.sprite.Group()

class Tunnel(Object):
    outerline_h = [(20, 15), (30, 15), (30, 35), (20, 35)]
    outerline_v = [(15, 20), (35, 20), (35, 30), (15, 30)]
    def __init__(self, direction: str, row, col, pos):
        super().__init__()
        self.surface = pygame.Surface([30, 30])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        match direction:
            case 'h':
                self.outerline = Tunnel.outerline_h
            case 'v':
                self.outerline = Tunnel.outerline_v
        self.pos = pos
        all_tunnels.add(self)
        self.row = row
        self.col = col
        self.direction = direction
        self.relation = None
        self.merge = None
        self.opened = False
        self.locked = True
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def set_state(self, opened: bool) -> bool:
        if self.locked:
            return False
        self.opened = opened
        return True
    def link(self, cell1, cell2) -> bool:
        if self.relation is not None:
            return False
        self.locked = False
        self.relation = (cell1, cell2)
        self.opened = True
        match self.direction:
            case 'h':
                cell1.right = self
                cell2.left = self
            case 'v':
                cell1.down = self
                cell2.up = self
        return True
    def unlink(self) -> bool:
        if self.relation is None:
            return False
        cell1, cell2 = self.relation
        self.relation = None
        self.opened = False
        self.locked = True
        match self.direction:
            case 'h':
                cell1.right = None
                cell2.left = None
            case 'v':
                cell1.down = None
                cell2.up = None
        return True
