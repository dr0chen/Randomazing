from utils import *
from object import *
from grid import *

class Player(Object):
    def __init__(self):
        super().__init__()
        self.current_cell = grid.cells[(grid.w - 1) // 2][(grid.h - 1) // 2]
        self.current_cell.lock()
        self.current_cell.player_enter()
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
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
        prev_cell.player_leave()
        self.current_cell.player_enter()
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

player = Player()