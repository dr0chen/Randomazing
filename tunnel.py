import pygame
from object import *
from utils import *
from tile import *

all_tunnels = pygame.sprite.Group()

class Tunnel(Object):
    outerline_h = [(5, 0), (15, 0), (15, 20), (5, 20)]
    innerline_h = []
    outerline_v = [(0, 5), (20, 5), (20, 15), (0, 15)]
    innerline_v = []
    def __init__(self, direction: str, row, col, cell1, cell2):
        super().__init__()
        self.surface = pygame.Surface([20, 20])
        self.surface.set_colorkey("white")
        self.surface.fill("white")
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
                entries = [
                    [pygame.Vector2(cell2.pos.x, cell2.pos.y + i * TILE_HEIGHT) for i in range(4, 8)],
                    [pygame.Vector2(cell1.pos.x + CELL_WIDTH - TILE_WIDTH, cell1.pos.y + i * TILE_HEIGHT) for i in range(4, 8)]
                ]
                directions = [pygame.Vector2(1, 0), pygame.Vector2(-1, 0)]
            case 'v':
                self.minipos = pygame.Vector2(15 + col * TILE_WIDTH, 40 + row * 50)
                self.outerline = Tunnel.outerline_v
                cell1.neighbor_cells['d'] = (self, cell2)
                cell2.neighbor_cells['u'] = (self, cell1)
                entries = [
                    [pygame.Vector2(cell2.pos.x + i * TILE_WIDTH, cell2.pos.y) for i in range(6, 10)],
                    [pygame.Vector2(cell1.pos.x + i * TILE_WIDTH, cell1.pos.y + CELL_HEIGHT - TILE_HEIGHT) for i in range(6, 10)]
                ]
                directions = [pygame.Vector2(0, 1), pygame.Vector2(0, -1)]
        all_tunnels.add(self)
        self.merge = None
        self.opened = True
        self.locked = False
        for entry in entries[0]:
            tunnel_tile = TunnelEntry(entry, self, directions[0])
            cell1.tiles.add(tunnel_tile)
        for entry in entries[1]:
            tunnel_tile = TunnelEntry(entry, self, directions[1])
            cell2.tiles.add(tunnel_tile)
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def set_state(self, opened: bool) -> bool:
        if self.locked:
            return False
        self.opened = opened
        return True
