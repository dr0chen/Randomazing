import pygame
from utils import *
from unit import *

class Tunnel(pygame.sprite.Sprite):
    all_tunnels = pygame.sprite.Group()
    outerline_h = [(5, 0), (15, 0), (15, 20), (5, 20)]
    outerline_v = [(0, 5), (20, 5), (20, 15), (0, 15)]
    def __init__(self, direction: str, row, col, cell1, cell2):
        super().__init__()
        self.minisurface = pygame.Surface([20, 20])
        self.minisurface.set_colorkey("white")
        self.minisurface.fill("white")
        self.row = row
        self.col = col
        self.direction = direction
        self.relations = (cell1, cell2)
        match direction:
            case 'h':
                self.minipos = pygame.Vector2(40 + col * TILE_WIDTH, 15 + row * TILE_HEIGHT)
                self.outerline = Tunnel.outerline_h
                cell1.neighbor_cells['r'] = (self, cell2)
                cell2.neighbor_cells['l'] = (self, cell1)
                self.poses = {
                    'r': [pygame.Vector2(cell2.pos.x, cell2.pos.y + i * TILE_HEIGHT) for i in range(4, 8)],
                    'l': [pygame.Vector2(cell1.pos.x + CELL_WIDTH - TILE_WIDTH, cell1.pos.y + i * TILE_HEIGHT) for i in range(4, 8)]
                }
            case 'v':
                self.minipos = pygame.Vector2(15 + col * TILE_WIDTH, 40 + row * 50)
                self.outerline = Tunnel.outerline_v
                cell1.neighbor_cells['d'] = (self, cell2)
                cell2.neighbor_cells['u'] = (self, cell1)
                self.poses = {
                    'd': [pygame.Vector2(cell2.pos.x + i * TILE_WIDTH, cell2.pos.y) for i in range(6, 10)],
                    'u': [pygame.Vector2(cell1.pos.x + i * TILE_WIDTH, cell1.pos.y + CELL_HEIGHT - TILE_HEIGHT) for i in range(6, 10)]
                }
        Tunnel.all_tunnels.add(self)
        self.merge = None
        self.opened = True
        self.closed_down = False
        self.locked = False
        self.breakable = False
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def close_down(self):
        self.closed_down = True
    def open_up(self):
        self.closed_down = False
    def set_state(self, opened: bool) -> bool:
        if self.locked:
            return False
        self.opened = opened
        return True
