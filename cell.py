from object import *
from utils import *
import random

class Cell(Object):
    def __init__(self, pos, bounding_size, outerline, innerline):
        super().__init__()
        self.surface = pygame.Surface(bounding_size)
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.outerline = outerline
        self.innerline = innerline
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
        match self.type:
            case 'n':
                color = "white"
            case 's1':
                color = "cyan"
            case 's2':
                color = "yellow"
            case 's-1':
                color = "purple"
            case 'e':
                color = "lime"
        if self.has_player:
            pygame.draw.polygon(self.surface, "red", self.outerline)
            pygame.draw.polygon(self.surface, color, self.innerline)
        else:
            pygame.draw.polygon(self.surface, color, self.outerline)
        surface.blit(self.surface, self.pos)
    def set_type(self, type: str):
        self.type = type
    def randomize(self) -> bool:
        if self.locked:
            return False
        if exitable:
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
    def __init__(self, row, col, pos):
        outerline = [(25, 25), (75, 25), (75, 75), (25, 75)]
        innerline = [(30, 30), (70, 30), (70, 70), (30, 70)]
        super().__init__(pos, [100, 100], outerline, innerline)
        all_small_cells.add(self)
        self.row = row
        self.col = col
        self.merge = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
    def render(self, surface):
        if self.merge is not None:
            return
        super().render(surface)
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
        if 25 <= inside_pos[0] <= 75 and 25 <= inside_pos[1] <= 75:
            return True
        return False
    def is_mergable(self) -> bool:
        return not self.locked and self.merge is None

class LargeCell(Cell):
    def __init__(self, shape, cells, tunnels, pos, bounding_size, outerline, innerline) -> None:
        super().__init__(pos, bounding_size, outerline, innerline)
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
    def __init__(self, tunnel) -> None:
        match tunnel.direction:
            case 'h':
                shape = 'h2'
                outerline = [(25, 25), (175, 25), (175, 75), (25, 75)]
                innerline = [(30, 30), (170, 30), (170, 70), (30, 70)]
                size = [200, 100]
            case 'v':
                shape = 'v2'
                outerline = [(25, 25), (75, 25), (75, 175), (25, 175)]
                innerline = [(30, 30), (70, 30), (70, 170), (30, 170)]
                size = [100, 200]
        pos = tunnel.relation[0].pos
        super().__init__(shape, [tunnel.relation[0], tunnel.relation[1]], [tunnel], pos, size, outerline, innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        match self.shape:
            case 'h2':
                if 25 <= inside_pos[0] <= 175 and 25 <= inside_pos[1] <= 75:
                    return True
            case 'v2':
                if 25 <= inside_pos[0] <= 75 and 25 <= inside_pos[1] <= 175:
                    return True
        return False

class LCell(LargeCell):
    def __init__(self, shape, htunnel, vtunnel):
        size = [200, 200]
        tunnels = [htunnel, vtunnel]
        match shape:
            case 'ulL':
                assert(htunnel.relation[0] is vtunnel.relation[0])
                pos = htunnel.relation[0].pos
                outerline = [(25, 25), (175, 25), (175, 75), (75, 75), (75, 175), (25, 175)]
                innerline = [(30, 30), (170, 30), (170, 70), (70, 70), (70, 170), (30, 170)]
                cells = [htunnel.relation[0], htunnel.relation[1], vtunnel.relation[1]]
            case 'dlL':
                assert(htunnel.relation[0] is vtunnel.relation[1])
                pos = vtunnel.relation[0].pos
                outerline = [(25, 25), (75, 25), (75, 125), (175, 125), (175, 175), (25, 175)]
                innerline = [(30, 30), (70, 30), (70, 130), (170, 130), (170, 170), (30, 170)]
                cells = [vtunnel.relation[0], htunnel.relation[0], htunnel.relation[1]]
            case 'urL':
                assert(htunnel.relation[1] is vtunnel.relation[0])
                pos = htunnel.relation[0].pos
                outerline = [(25, 25), (175, 25), (175, 175), (125, 175), (125, 75), (25, 75)]
                innerline = [(30, 30), (170, 30), (170, 170), (130, 170), (130, 70), (30, 70)]
                cells = [htunnel.relation[0], htunnel.relation[1], vtunnel.relation[1]]
            case 'drL':
                assert(htunnel.relation[1] is vtunnel.relation[1])
                pos = (htunnel.relation[0].pos[0], vtunnel.relation[0].pos[1])
                outerline = [(125, 25), (175, 25), (175, 175), (25, 175), (25, 125), (125, 125)]
                innerline = [(130, 30), (170, 30), (170, 170), (30, 170), (30, 130), (130, 130)]
                cells = [vtunnel.relation[0], htunnel.relation[0], htunnel.relation[1]]
            case _:
                assert(0)
        super().__init__(shape, cells, tunnels, pos, size, outerline, innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        match self.shape[0]:
            case 'u':
                if 25 <= inside_pos[0] <= 175 and 25 <= inside_pos[1] <= 75:
                    return True
            case 'd':
                if 25 <= inside_pos[0] <= 175 and 125 <= inside_pos[1] <= 175:
                    return True
        match self.shape[1]:
            case 'l':
                if 25 <= inside_pos[0] <= 75 and 25 <= inside_pos[1] <= 175:
                    return True
            case 'r':
                if 125 <= inside_pos[0] <= 175 and 25 <= inside_pos[1] <= 175:
                    return True
        return False

class BlockFourCell(LargeCell):
    def __init__(self, utunnel, dtunnel, ltunnel, rtunnel):
        assert(utunnel.relation[1] is rtunnel.relation[0])
        assert(rtunnel.relation[1] is dtunnel.relation[1])
        assert(dtunnel.relation[0] is ltunnel.relation[1])
        assert(ltunnel.relation[0] is utunnel.relation[0])
        pos = utunnel.relation[0].pos
        size = [200, 200]
        outerline = [(25, 25), (175, 25), (175, 175), (25, 175)]
        innerline = [(30, 30), (170, 30), (170, 170), (30, 170)]
        cells = [utunnel.relation[0], utunnel.relation[1], dtunnel.relation[0], dtunnel.relation[1]]
        tunnels = [utunnel, dtunnel, ltunnel, rtunnel]
        super().__init__('4', cells, tunnels, pos, size, outerline, innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 25 <= inside_pos[0] <= 175 and 25 <= inside_pos[1] <= 175:
            return True
        return False
