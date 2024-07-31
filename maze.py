import pygame
import random

pygame.init()
pygame.font.init()

FONT = 'consolas'

SIZE = 5
SAFE_MOVES_TOTAL = SIZE + 2
WIDTH = SIZE * 100 + 800
HEIGHT = (SIZE + 1) * 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

all_small_cells = pygame.sprite.Group()
all_large_cells = pygame.sprite.Group()
all_tunnels = pygame.sprite.Group()

def get_all_cells():
    return [cell for cell in all_small_cells if cell.merge is None] + list(all_large_cells)

exitable = False
exited = False

#Work in Progress (for refactoring)
class Object(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

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
        self.type = 'n'
    def unlock(self):
        self.locked = False
    def lock(self):
        self.locked = True
    def render(self, surface: pygame.Surface):
        match self.type:
            case 'n':
                pygame.draw.polygon(self.surface, "white", self.outerline)
            case 's1':
                pygame.draw.polygon(self.surface, "cyan", self.outerline)
            case 's2':
                pygame.draw.polygon(self.surface, "yellow", self.outerline)
            case 's-1':
                pygame.draw.polygon(self.surface, "purple", self.outerline)
            case 'e':
                pygame.draw.polygon(self.surface, "lime", self.outerline)
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

#Work in progress
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

class LargeCell(Cell):
    def __init__(self, tunnels, pos, bounding_size, outerline, innerline) -> None:
        super().__init__(pos, bounding_size, outerline, innerline)
        all_large_cells.add(self)
        self.tunnels = tunnels
        self.cells = list(set([cell for cell in sum([tunnel.relation for tunnel in tunnels], ())]))
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

class H2Cell(LargeCell):
    def __init__(self, tunnel) -> None:
        outerline = [(25, 25), (175, 25), (175, 75), (25, 75)]
        innerline = [(30, 30), (170, 30), (170, 70), (30, 70)]
        pos = tunnel.relation[0].pos
        super().__init__([tunnel], pos, [200, 100], outerline, innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 25 <= inside_pos[0] <= 175 and 25 <= inside_pos[1] <= 75:
            return True
        return False

class V2Cell(LargeCell):
    def __init__(self, tunnel) -> None:
        outerline = [(25, 25), (75, 25), (75, 175), (25, 175)]
        innerline = [(30, 30), (70, 30), (70, 170), (30, 170)]
        pos = tunnel.relation[0].pos
        super().__init__([tunnel], pos, [100, 200], outerline, innerline)
    def is_inside(self, pos) -> bool:
        inside_pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if 25 <= inside_pos[0] <= 75 and 25 <= inside_pos[1] <= 175:
            return True
        return False

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
    def link(self, cell1: Cell, cell2: Cell) -> bool:
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

class Grid:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[SmallCell(i, j, (j*100, i*100)) for j in range(w)] for i in range(h)]
        self.tunnels = {
            'h': [[Tunnel('h', i, j, (75+j*100, 25+i*100)) for j in range(w - 1)] for i in range(h)],
            'v': [[Tunnel('v', i, j, (25+j*100, 75+i*100)) for j in range(w)] for i in range(h - 1)]
        }
        for i, tunnels_row in enumerate(self.tunnels['h']):
            for j, tunnel in enumerate(tunnels_row):
                tunnel.link(self.cells[i][j], self.cells[i][j + 1])
        for i, tunnels_row in enumerate(self.tunnels['v']):
            for j, tunnel in enumerate(tunnels_row):
                tunnel.link(self.cells[i][j], self.cells[i + 1][j])
    def randomize(self):
        for large_cell in all_large_cells.copy():
            if not large_cell.locked:
                large_cell.unmerge()
        for _ in range(random.randint(0, 4)):
            if random.randint(0, 1):
                tunnel = random.choice(sum(self.tunnels['h'], []))
                cell1, cell2 = tunnel.relation
                if not cell1.locked and cell1.merge is None and not cell2.locked and cell2.merge is None:
                    H2Cell(tunnel)
            else:
                tunnel = random.choice(sum(self.tunnels['v'], []))
                cell1, cell2 = tunnel.relation
                if not cell1.locked and cell1.merge is None and not cell2.locked and cell2.merge is None:
                    V2Cell(tunnel)
        ##random first search##
        all_cells = get_all_cells()
        visited = []
        queue = [(None, random.choice(all_cells))]
        while len(queue) > 0:
            prev_tunnel, cell = random.choice(queue)
            queue = [item for item in queue if item != (prev_tunnel, cell)]
            if cell in visited :
                prob = 15 if not exitable else 5
                if random.randint(1, 100) <= prob:
                    prev_tunnel.set_state(True)
                else:
                    prev_tunnel.set_state(False)
            else:
                if prev_tunnel is not None:
                    prev_tunnel.set_state(True)
                visited.append(cell)
                neighbors = [(tunnel, next_cell) for tunnel, next_cell in cell.get_neighbors() if tunnel != prev_tunnel]
                queue += neighbors
        ##random first search ends##
        for cell in all_cells:
            cell.randomize()
    def set_exit(self, player):
        all_cells = get_all_cells()
        for cell in all_cells:
            cell.set_type('n')
        candidates = []
        for i, cells_row in enumerate(self.cells):
            for j, cell in enumerate(cells_row):
                if abs(i - player.current_cell.row) + abs(j - player.current_cell.col) <= SIZE / 2 or cell.locked:
                    continue
                candidates.append(cell)
        exit_cell = random.choice(candidates)
        exit_cell.set_type('e')
        player.safe_moves = 2

grid = Grid(SIZE, SIZE)

class Player(Object):
    def __init__(self):
        super().__init__()
        self.current_cell = grid.cells[(grid.w - 1) // 2][(grid.h - 1) // 2]
        self.current_cell.lock()
        self.surface = pygame.Surface(self.current_cell.surface.get_size())
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.outerline = self.current_cell.outerline
        self.innerline = self.current_cell.innerline
        self.pos = self.current_cell.pos
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
    def render(self, surface):
        pygame.draw.polygon(self.surface, "red", self.outerline)
        pygame.draw.polygon(self.surface, "black", self.innerline)
        surface.blit(self.surface, self.pos)
    def move(self, mouse_pos):
        next_cell = None
        all_cells = get_all_cells()
        for cell in all_cells:
            if cell.is_inside(mouse_pos):
                next_cell = cell
                break
        neighbors = self.current_cell.get_neighbors()
        for tunnel, neighbor in neighbors:
            if neighbor is not next_cell or not tunnel.opened:
                continue
            break
        else:
            return
        prev_cell = self.current_cell
        self.current_cell = next_cell
        self.surface = pygame.Surface(self.current_cell.surface.get_size())
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.outerline = self.current_cell.outerline
        self.innerline = self.current_cell.innerline
        self.pos = self.current_cell.pos
        match self.current_cell.type:
            case 's1':
                self.score += 1
            case 's2':
                self.score += 2
            case 's-1':
                self.score -= 1
            case 'e':
                global exited
                exited = True
                return
        self.current_cell.set_type('n')
        prev_cell.unlock()
        self.current_cell.lock()
        if exitable:
            self.safe_moves -= 1
            self.moves += 1
            if self.safe_moves <= 0:
                self.safe_moves = 2
                grid.randomize()
        else:
            self.safe_moves -= 1
            self.moves += 1
            if self.safe_moves <= 0:
                self.rand_prob = min(self.rand_prob + 5, 50)
                if random.randint(1, 100) < self.rand_prob:
                    self.rand_prob = 0
                    self.safe_moves = SAFE_MOVES_TOTAL
                    grid.randomize()

#Work in progress
class Chaser(Object):
    pass

player = Player()
grid.randomize()

font = pygame.font.Font(pygame.font.match_font('consolas'), 30)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.MOUSEBUTTONUP:
            mouse = pygame.mouse.get_pos()
            player.move(mouse)
    if player.score >= 100 and not exitable:
        grid.set_exit(player)
        exitable = True
    screen.fill("black")
    pygame.draw.rect(screen, "white", pygame.Rect(525, 25, 750, 550))
    for cell in all_small_cells:
        cell.render(screen)
    for cell in all_large_cells:
        cell.render(screen)
    for tunnel in all_tunnels:
        tunnel.render(screen)
    player.render(screen)
    score_text_surface = font.render(f'Score:{player.score}', True, "white")
    moves_text_surface = font.render(f'Moves:{player.moves}', True, "white")
    screen.blit(score_text_surface, (0, grid.h*100-10))
    screen.blit(moves_text_surface, (SIZE * 100-moves_text_surface.get_width(), grid.h*100-10))
    if exited:
        break
    if exitable:
        exitable_text_surface = font.render('Exitable', True, "red")
        screen.blit(exitable_text_surface, (245, grid.h*100-10))
    pygame.display.flip()
    clock.tick(60)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    exit_text_surface = font.render('Exited', True, "lime")
    screen.blit(exit_text_surface, (275, grid.h*100-10))
    pygame.display.flip()