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
    def update(self):
        self.acc = pygame.Vector2(0, 0)
        max_speed = self.speed
        if self.state == 'free':
            if glob_var["grid"].should_randomize:
                glob_var["grid"].randomize()
            self.location = current_cells[0]
            pressed_keys = pygame.key.get_pressed()
            self.facing = [0, 0]
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
                self.acc.x -= self.speed / 2
                self.facing[0] -= 1
            if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
                self.acc.x += self.speed / 2
                self.facing[0] += 1
            if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
                self.acc.y -= self.speed / 2
                self.facing[1] -= 1
            if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
                self.acc.y += self.speed / 2
                self.facing[1] += 1
            if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
                max_speed = 5
        elif self.state == 'transition':
            self.acc.x += self.facing[0] * self.speed / 2
            self.acc.y += self.facing[1] * self.speed / 2
        else:
            assert(0)
        if self.vel != (0, 0):
            self.acc -= self.vel.normalize()
        vel_tmp = self.vel + self.acc
        if self.vel.x * vel_tmp.x < 0:
            self.vel.x = 0
        else:
            self.vel.x = vel_tmp.x
        if self.vel.y * vel_tmp.y < 0:
            self.vel.y = 0
        else:
            self.vel.y = vel_tmp.y
        if self.vel.length() > max_speed:
            self.vel = self.vel.normalize() * max_speed
        self.rect.left += self.vel.x
        vel_y = self.vel.y
        self.vel.y = 0
        self.location.cm.check_collisions()
        self.vel.y = vel_y
        self.rect.top += self.vel.y
        vel_x = self.vel.x
        self.vel.x = 0
        self.location.cm.check_collisions()
        self.vel.x = vel_x
        if current_cells[-1].is_including(self.rect):
            self.state = 'free'