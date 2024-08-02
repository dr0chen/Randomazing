from object import *
from maze_global import *
import random

all_small_cells = pygame.sprite.Group()
all_large_cells = pygame.sprite.Group()

def get_all_cells():
    return [cell for cell in all_small_cells if cell.merge is None] + list(all_large_cells)

class Cell(Object):
    def __init__(self, row, col, pos, bounding_size, outerline, innerline):
        super().__init__()
        self.surface = pygame.Surface(bounding_size)
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.outerline = outerline
        self.innerline = innerline
        self.row = row
        self.col = col
        self.pos = pos
        self.locked = False
        self.has_player = False
        self.type = 'n'
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def player_enter(self):
        self.has_player = True
        self.lock()
    def player_leave(self):
        self.has_player = False
        self.unlock()
    def render(self, surface: pygame.Surface):
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
    def __init__(self, row, col, pos):
        super().__init__(row, col, pos, [50, 50], SmallCell.outerline, SmallCell.innerline)
        all_small_cells.add(self)
        self.merge = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
    def get_neighbor(self, direction: str):
        neighbor = (None, None)
        match direction:
            case 'u':
                if self.up is not None:
                    neighbor = (self.up, self.up.relation[0])
            case 'd':
                if self.down is not None:
                    neighbor = (self.down, self.down.relation[1])
            case 'l':
                if self.left is not None:
                    neighbor = (self.left, self.left.relation[0])
            case 'r':
                if self.right is not None:
                    neighbor = (self.right, self.right.relation[1])
        if neighbor[1] is not None and neighbor[1].merge is not None:
            neighbor = (neighbor[0], neighbor[1].merge)
        return neighbor
    def get_neighbors(self):
        neighbors = map(self.get_neighbor, 'udlr')
        neighbors = [neighbor for neighbor in neighbors if neighbor != (None, None)]
        return neighbors
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 0 <= inside_pos[0] <= 50 and 0 <= inside_pos[1] <= 50:
            return True
        return False
    def is_mergable(self) -> bool:
        return not self.locked and self.merge is None

class LargeCell(Cell):
    def __init__(self, shape, cells, tunnels, pos, bounding_size, outerline, innerline) -> None:
        super().__init__(cells[0].row, cells[0].col, pos, bounding_size, outerline, innerline)
        all_large_cells.add(self)
        self.shape = shape
        self.cells = cells
        self.tunnels = tunnels
        for cell in self.cells:
            cell.merge = self
        for tunnel in self.tunnels:
            tunnel.merge = self
    def get_neighbors(self):
        neighbors = sum([cell.get_neighbors() for cell in self.cells], [])
        neighbors = [(tunnel, neighbor) for tunnel, neighbor in neighbors if neighbor not in self.cells]
        return neighbors
    def unmerge(self):
        for tunnel in self.tunnels:
            tunnel.merge = None
        for cell in self.cells:
            cell.merge = None
            all_large_cells.remove(self)

class BlockTwoCell(LargeCell):
    outerline_h2 = [(0, 0), (100, 0), (100, 50), (0, 50)]
    innerline_h2 = [(5, 5), (95, 5), (95, 45), (5, 45)]
    size_h2 = [100, 50]
    size_v2 = [50, 100]
    outerline_v2 = [(0, 0), (50, 0), (50, 100), (0, 100)]
    innerline_v2 = [(5, 5), (45, 5), (45, 95), (5, 95)]
    def __init__(self, tunnel) -> None:
        match tunnel.direction:
            case 'h':
                shape = 'h2'
                outerline = BlockTwoCell.outerline_h2
                innerline = BlockTwoCell.innerline_h2
                size = BlockTwoCell.size_h2
            case 'v':
                shape = 'v2'
                outerline = BlockTwoCell.outerline_v2
                innerline = BlockTwoCell.innerline_v2
                size = BlockTwoCell.size_v2
        pos = tunnel.relation[0].pos
        super().__init__(shape, [tunnel.relation[0], tunnel.relation[1]], [tunnel], pos, size, outerline, innerline)
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
    size = [100, 100]
    def __init__(self, shape, htunnel, vtunnel):
        tunnels = [htunnel, vtunnel]
        match shape:
            case 'ulL':
                assert(htunnel.relation[0] is vtunnel.relation[0])
                pos = htunnel.relation[0].pos
                outerline = LCell.outerline_ulL
                innerline = LCell.innerline_ulL
                cells = [htunnel.relation[0], htunnel.relation[1], vtunnel.relation[1]]
            case 'dlL':
                assert(htunnel.relation[0] is vtunnel.relation[1])
                pos = vtunnel.relation[0].pos
                outerline = LCell.outerline_dlL
                innerline = LCell.innerline_dlL
                cells = [vtunnel.relation[0], htunnel.relation[0], htunnel.relation[1]]
            case 'urL':
                assert(htunnel.relation[1] is vtunnel.relation[0])
                pos = htunnel.relation[0].pos
                outerline = LCell.outerline_urL
                innerline = LCell.innerline_urL
                cells = [htunnel.relation[0], htunnel.relation[1], vtunnel.relation[1]]
            case 'drL':
                assert(htunnel.relation[1] is vtunnel.relation[1])
                pos = (htunnel.relation[0].pos[0], vtunnel.relation[0].pos[1])
                outerline = LCell.outerline_drL
                innerline = LCell.innerline_drL
                cells = [vtunnel.relation[0], htunnel.relation[0], htunnel.relation[1]]
            case _:
                assert(0)
        super().__init__(shape, cells, tunnels, pos, LCell.size, outerline, innerline)
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
    size = [100, 100]
    def __init__(self, utunnel, dtunnel, ltunnel, rtunnel):
        assert(utunnel.relation[1] is rtunnel.relation[0])
        assert(rtunnel.relation[1] is dtunnel.relation[1])
        assert(dtunnel.relation[0] is ltunnel.relation[1])
        assert(ltunnel.relation[0] is utunnel.relation[0])
        pos = utunnel.relation[0].pos
        cells = [utunnel.relation[0], utunnel.relation[1], dtunnel.relation[0], dtunnel.relation[1]]
        tunnels = [utunnel, dtunnel, ltunnel, rtunnel]
        super().__init__('4', cells, tunnels, pos, BlockFourCell.size, BlockFourCell.outerline, BlockFourCell.innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 0 <= inside_pos[0] <= 100 and 0 <= inside_pos[1] <= 100:
            return True
        return False