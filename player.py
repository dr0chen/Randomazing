from utils import *
from object import *
from cell import *
import random

class Player(Object):
    def __init__(self, speed: float):
        super().__init__()
        self.surface = pygame.Surface([50, 50])
        self.surface.fill(color="red")
        self.rect = pygame.Rect((0, 0), [TILE_WIDTH, TILE_HEIGHT])
        self.rect.center = current_cells[0].bound.center
        self.speed = speed
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.facing = [1, 0]
        self.state = 'free'
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
        self.current_cell = current_cells[0]
        self.location = current_cells[0]
        self.location.player_enter(self)
    def move_to(self, next_cell):
        self.state = 'transition'
        self.current_cell.player_leave(self)
        self.current_cell = next_cell
        self.current_cell.player_enter(self)
        match self.current_cell.type:
            case 's1':
                self.score += 1
            case 's2':
                self.score += 2
            case 's-1':
                self.score -= 1
            case 'e':
                glob_var["exited"] = True
                return
        self.current_cell.set_type('n')
        self.safe_moves -= 1
        self.moves += 1
        if glob_var["exitable"]:
            if self.safe_moves <= 0:
                self.safe_moves = 2
                glob_var["grid"].should_randomize = True
        else:
            if self.safe_moves <= 0:
                self.rand_prob = min(self.rand_prob + 5, 50)
                if random.randint(1, 100) < self.rand_prob:
                    self.rand_prob = 0
                    self.safe_moves = SAFE_MOVES_TOTAL
                    glob_var["grid"].should_randomize = True