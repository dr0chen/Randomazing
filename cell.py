import pygame
from object import *
from utils import *
from collision import *
from layout import *
from unit import *
import random

class Cell(Object):
    def __init__(self, row, col, mini_bound, bound):
        super().__init__()
        self.minisurface = pygame.Surface(mini_bound)
        self.minisurface.set_colorkey("gray")
        self.minisurface.fill("gray")
        self.row = row
        self.col = col
        self.minipos = pygame.Vector2(TILE_WIDTH * col, TILE_HEIGHT * row)
        self.pos = pygame.Vector2(CELL_WIDTH * col, CELL_HEIGHT * row)
        self.bound = pygame.Rect(self.pos, bound)
        self.locked = False
        self.has_player = False
        self.type = 'n'
        self.enemies = pygame.sprite.Group()
        self.cm = deploy_cm()
    def is_including(self, rect: pygame.Rect) -> bool:
        for point in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
            for area in self.areas:
                if is_inside(pygame.Vector2(point), pygame.Rect(area)):
                    break
            else:
                return False
        return True
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def player_enter(self, player):
        self.has_player = True
        self.cm.add_dynamic(player)
        self.lock()
    def player_leave(self, player):
        self.has_player = False
        self.cm.remove(player)
        if self.type != 'e':
            self.unlock()
    def make_layout(self):
        pass
    def clear_layout(self):
        pass
    def render_layout(self, surface: pygame.Surface):
        pass
    def set_type(self, type: str):
        self.type = type
    def randomize(self) -> bool:
        if self.locked:
            return False
        if glob_var["exitable"]:
            if self.type != 'e':
                self.set_type('n')
            return True
        r = random.randint(1, 100)
        if r > 40:
            self.set_type('n')
        elif r > 15:
            self.set_type('s1')
        elif r > 5:
            self.set_type('s-1')
        else:
            self.set_type('s2')
        return True

class SmallCell(Cell):
    outerline = [(0, 0), (50, 0), (50, 50), (0, 50)]
    innerline = [(5, 5), (45, 5), (45, 45), (5, 45)]
    mini_bound = [TILE_WIDTH, TILE_HEIGHT]
    bound = [CELL_WIDTH, CELL_HEIGHT]
    all_small_cells = pygame.sprite.Group()
    def __init__(self, row, col):
        super().__init__(row, col, SmallCell.mini_bound, SmallCell.bound)
        self.shape = '1'
        self.outerline = SmallCell.outerline
        self.innerline = SmallCell.innerline
        self.areas = [
            (self.pos.x + 50, self.pos.y + 50, CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50)
        ]
        SmallCell.all_small_cells.add(self)
        self.layout = {
            'u': 'W' if row == 0 else 'T',
            'd': 'W' if row == MAZE_SIZE-1 else 'T',
            'l': 'W' if col == 0 else 'T',
            'r': 'W' if col == MAZE_SIZE-1 else 'T',
        }
        self.merge = None
        self.tiles = pygame.sprite.Group()
        self.neighbor_cells = {
            'u': (None, None),
            'd': (None, None),
            'l': (None, None),
            'r': (None, None)
        }
    def get_neighbor(self, direction: str):
        neighbor = self.neighbor_cells[direction]
        if neighbor[1] and neighbor[1].merge:
            neighbor = (neighbor[0], neighbor[1].merge)
        return neighbor
    def get_neighbors(self):
        neighbors = map(lambda x: self.neighbor_cells[x], 'udlr')
        neighbors = [neighbor for neighbor in neighbors if neighbor != (None, None)]
        return neighbors
    def is_mergable(self) -> bool:
        return not self.locked and not self.merge
    def make_layout(self):
        make_layout_1(self, self.layout, self.cm)
    def clear_layout(self):
        for tile in self.tiles:
            self.tiles.remove(tile)
        for enemy in self.enemies:
            enemy.kill()
    def render_layout(self, surface: pygame.Surface):
        for tile in self.tiles:
            tile.render(surface)

class LargeCell(Cell):
    all_large_cells = pygame.sprite.Group()
    def __init__(self, row, col, cells, tunnels, mini_bound, bound):
        super().__init__(row, col, mini_bound, bound)
        LargeCell.all_large_cells.add(self)
        self.cells = cells
        self.tunnels = tunnels
        for cell in self.cells:
            cell.merge = self
            cell.clear_layout()
        for tunnel in self.tunnels:
            tunnel.merge = self
        self.make_layout()
    def get_neighbors(self):
        neighbors = sum([cell.get_neighbors() for cell in self.cells], [])
        neighbors = [(tunnel, neighbor) for tunnel, neighbor in neighbors if neighbor not in self.cells]
        return neighbors
    def make_layout(self):
        for cell, layout in zip(self.cells, self.layouts):
            make_layout_1(cell, layout, self.cm)
    def clear_layout(self):
        for cell in self.cells:
            for tile in cell.tiles:
                cell.tiles.remove(tile)
                self.cm.remove(tile)
    def render_layout(self, surface: pygame.Surface):
        for tile in sum([list(cell.tiles) for cell in self.cells], []):
            tile.render(surface)
    def unmerge(self):
        self.clear_layout()
        for cell in self.cells:
            cell.merge = None
            cell.make_layout()
        for tunnel in self.tunnels:
            tunnel.merge = None
        self.kill()

class BlockTwoCell(LargeCell):
    outerline_h2 = [(0, 0), (100, 0), (100, 50), (0, 50)]
    innerline_h2 = [(5, 5), (95, 5), (95, 45), (5, 45)]
    mini_bound_h2 = [2 * TILE_WIDTH, TILE_HEIGHT]
    bound_h2 = [2 * CELL_WIDTH, CELL_HEIGHT]
    outerline_v2 = [(0, 0), (50, 0), (50, 100), (0, 100)]
    innerline_v2 = [(5, 5), (45, 5), (45, 95), (5, 95)]
    mini_bound_v2 = [TILE_WIDTH, 2 * TILE_HEIGHT]
    bound_v2 = [CELL_WIDTH, 2 * CELL_HEIGHT]
    def __init__(self, tunnel) -> None:
        row = tunnel.relations[0].row
        col = tunnel.relations[0].col
        match tunnel.direction:
            case 'h':
                self.shape = 'h2'
                self.outerline = BlockTwoCell.outerline_h2
                self.innerline = BlockTwoCell.innerline_h2
                mini_bound = BlockTwoCell.mini_bound_h2
                bound = BlockTwoCell.bound_h2
                self.areas = [
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'W' if row == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'M'
                    },
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'W' if row == MAZE_SIZE-1 else 'T',
                        'l': 'M',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    }
                ]
            case 'v':
                self.shape = 'v2'
                self.outerline = BlockTwoCell.outerline_v2
                self.innerline = BlockTwoCell.innerline_v2
                mini_bound = BlockTwoCell.mini_bound_v2
                bound = BlockTwoCell.bound_v2
                self.areas = [
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'M',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'W' if col == MAZE_SIZE-1 else 'T'
                    },
                    {
                        'u': 'M',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'W' if col == MAZE_SIZE-1 else 'T'
                    }
                ]
        super().__init__(row, col, [tunnel.relations[0], tunnel.relations[1]], [tunnel], mini_bound, bound)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        match self.shape:
            case 'h2':
                if 0 <= inside_pos[0] <= 100 and 0 <= inside_pos[1] <= 50:
                    return True
            case 'v2':
                if 0 <= inside_pos[0] <= 50 and 0 <= inside_pos[1] <= 100:
                    return True
        return False

class LCell(LargeCell):
    outerline_ulL = [(0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100)]
    innerline_ulL = [(5, 5), (95, 5), (95, 45), (45, 45), (45, 95), (5, 95)]
    outerline_dlL = [(0, 0), (50, 0), (50, 50), (100, 50), (100, 100), (0, 100)]
    innerline_dlL = [(5, 5), (45, 5), (45, 55), (95, 55), (95, 95), (5, 95)]
    outerline_urL = [(0, 0), (100, 0), (100, 100), (50, 100), (50, 50), (0, 50)]
    innerline_urL = [(5, 5), (95, 5), (95, 95), (55, 95), (55, 45), (5, 45)]
    outerline_drL = [(50, 0), (100, 0), (100, 100), (0, 100), (0, 50), (50, 50)]
    innerline_drL = [(55, 5), (95, 5), (95, 95), (5, 95), (5, 55), (55, 55)]
    mini_bound = [2 * TILE_WIDTH, 2 * TILE_HEIGHT]
    bound = [2 * CELL_WIDTH, 2 * CELL_HEIGHT]
    def __init__(self, shape, htunnel, vtunnel):
        tunnels = [htunnel, vtunnel]
        self.shape = shape
        match shape:
            case 'ulL':
                assert(htunnel.relations[0] is vtunnel.relations[0])
                row = htunnel.relations[0].row
                col = htunnel.relations[0].col
                self.outerline = LCell.outerline_ulL
                self.innerline = LCell.innerline_ulL
                cells = [htunnel.relations[0], htunnel.relations[1], vtunnel.relations[1]]
                self.areas = [
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50),
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'M',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'M'
                    },
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'W' if row == MAZE_SIZE-1 else 'T',
                        'l': 'M',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    },
                    {
                        'u': 'M',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'W' if col == MAZE_SIZE-1 else 'T'
                    }
                ]
            case 'dlL':
                assert(htunnel.relations[0] is vtunnel.relations[1])
                row = vtunnel.relations[0].row
                col = vtunnel.relations[0].col
                self.outerline = LCell.outerline_dlL
                self.innerline = LCell.innerline_dlL
                cells = [vtunnel.relations[0], htunnel.relations[0], htunnel.relations[1]]
                self.areas = [
                    (col * CELL_WIDTH + 50, (row+1) * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50),
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'M',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'W' if col == MAZE_SIZE-1 else 'T'
                    },
                    {
                        'u': 'M',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'M'
                    },
                    {
                        'u': 'W' if row+1 == 0 else 'T',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'M',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    }
                ]
            case 'urL':
                assert(htunnel.relations[1] is vtunnel.relations[0])
                row = htunnel.relations[0].row
                col = htunnel.relations[0].col
                self.outerline = LCell.outerline_urL
                self.innerline = LCell.innerline_urL
                cells = [htunnel.relations[0], htunnel.relations[1], vtunnel.relations[1]]
                self.areas = [
                    (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50),
                    ((col+1) * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'W' if row == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'M'
                    },
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'M',
                        'l': 'M',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    },
                    {
                        'u': 'M',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col+1 == 0 else 'T',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    }
                ]
            case 'drL':
                assert(htunnel.relations[1] is vtunnel.relations[1])
                row = vtunnel.relations[0].row
                col = htunnel.relations[0].col
                self.outerline = LCell.outerline_drL
                self.innerline = LCell.innerline_drL
                cells = [vtunnel.relations[0], htunnel.relations[0], htunnel.relations[1]]
                self.areas = [
                    (col * CELL_WIDTH + 50, (row+1) * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, CELL_HEIGHT - 2 * 50),
                    ((col+1) * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
                ]
                self.layouts = [
                    {
                        'u': 'W' if row == 0 else 'T',
                        'd': 'M',
                        'l': 'W' if col+1 == 0 else 'T',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    },
                    {
                        'u': 'W' if row+1 == 0 else 'T',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'W' if col == 0 else 'T',
                        'r': 'M'
                    },
                    {
                        'u': 'M',
                        'd': 'W' if row+1 == MAZE_SIZE-1 else 'T',
                        'l': 'M',
                        'r': 'W' if col+1 == MAZE_SIZE-1 else 'T'
                    }
                ]
            case _:
                assert(0)
        super().__init__(row, col, cells, tunnels, LCell.mini_bound, LCell.bound)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        match self.shape[0]:
            case 'u':
                if 0 <= inside_pos[0] <= 100 and 0 <= inside_pos[1] <= 50:
                    return True
            case 'd':
                if 0 <= inside_pos[0] <= 100 and 50 <= inside_pos[1] <= 100:
                    return True
        match self.shape[1]:
            case 'l':
                if 0 <= inside_pos[0] <= 50 and 0 <= inside_pos[1] <= 100:
                    return True
            case 'r':
                if 50 <= inside_pos[0] <= 100 and 0 <= inside_pos[1] <= 100:
                    return True
        return False

class BlockFourCell(LargeCell):
    outerline = [(0, 0), (100, 0), (100, 100), (0, 100)]
    innerline = [(5, 5), (95, 5), (95, 95), (5, 95)]
    mini_bound = [2 * TILE_WIDTH, 2 * TILE_HEIGHT]
    bound = [2 * CELL_WIDTH, 2 * CELL_HEIGHT]
    def __init__(self, utunnel, dtunnel, ltunnel, rtunnel):
        assert(utunnel.relations[1] is rtunnel.relations[0])
        assert(rtunnel.relations[1] is dtunnel.relations[1])
        assert(dtunnel.relations[0] is ltunnel.relations[1])
        assert(ltunnel.relations[0] is utunnel.relations[0])
        row = utunnel.relations[0].row
        col = utunnel.relations[0].col
        cells = [utunnel.relations[0], utunnel.relations[1], dtunnel.relations[0], dtunnel.relations[1]]
        tunnels = [utunnel, dtunnel, ltunnel, rtunnel]
        self.shape = '4'
        self.areas = [
            (col * CELL_WIDTH + 50, row * CELL_HEIGHT + 50, 2 * CELL_WIDTH - 2 * 50, 2 * CELL_HEIGHT - 2 * 50)
        ]
        self.outerline = BlockFourCell.outerline
        self.innerline = BlockFourCell.innerline
        self.layouts = [
            {
                'u': 'W' if row == 0 else 'T',
                'd': 'M',
                'l': 'W' if col == 0 else 'T',
                'r': 'M',
            },
            {
                'u': 'W' if row == 0 else 'T',
                'd': 'M',
                'l': 'M',
                'r': 'W' if col+1 == MAZE_SIZE - 1 else 'T',
            },
            {
                'u': 'M',
                'd': 'W' if row+1 == MAZE_SIZE - 1 else 'T',
                'l': 'W' if col == 0 else 'T',
                'r': 'M',
            },
            {
                'u': 'M',
                'd': 'W' if row+1 == MAZE_SIZE - 1 else 'T',
                'l': 'M',
                'r': 'W' if col+1 == MAZE_SIZE - 1 else 'T',
            }
        ]
        super().__init__(row, col, cells, tunnels, BlockFourCell.mini_bound, BlockFourCell.bound)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 0 <= inside_pos[0] <= 100 and 0 <= inside_pos[1] <= 100:
            return True
        return False
    
def get_all_cells():
    return [cell for cell in SmallCell.all_small_cells if not cell.merge] + list(LargeCell.all_large_cells)