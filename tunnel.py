import pygame
from utils import *
from object import *

class Tunnel(Object):
    def __init__(self, direction: str, row, col, pos):
        super().__init__()
        self.surface = pygame.Surface([50, 50])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        match direction:
            case 'h':
                self.outerline = [(0, 15), (50, 15), (50, 35), (0, 35)]
                self.innerline = [(0, 20), (50, 20), (50, 30), (0, 30)]
            case 'v':
                self.outerline = [(15, 0), (35, 0), (35, 50), (15, 50)]
                self.innerline = [(20, 0), (30, 0), (30, 50), (20, 50)]
        self.pos = pos
        all_tunnels.add(self)
        self.row = row
        self.col = col
        self.direction = direction
        self.relation = None
        self.merge = None
        self.opened = False
        self.locked = True
    def render(self, screen):
        if not self.opened or self.merge is not None:
            return
        pygame.draw.polygon(self.surface, "white", self.outerline)
        screen.blit(self.surface, self.pos)
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
