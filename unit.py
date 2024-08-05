import pygame
import random
from utils import *
from projectile import *
from droppeditem import *

class Unit(pygame.sprite.Sprite):
    def __init__(self, pos, speed, health, attack):
        super().__init__()
        self.surface = pygame.Surface([UNIT_WIDTH, UNIT_HEIGHT])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect(pos, [UNIT_WIDTH, UNIT_HEIGHT])
        self.speed = speed
        self.health = health
        self.attack = attack
        self.vel = pygame.Vector2(0, 0)
    def render(self, surface):
        pass
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.dead()
    def dead(self):
        pass

class Player(Unit):
    def __init__(self, cell, speed, health, attack):
        super().__init__(cell.bound.topleft, speed, health, attack)
        self.rect.center = cell.bound.center
        self.acc = pygame.Vector2(0, 0)
        self.facing = [1, 0]
        self.shield = False
        self.moving_state = 'free'
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
        self.location = cell
        self.location.player_enter(self)
    def shoot_bullet(self, mouse_pos):
        if self.moving_state != 'free' or self.shield:
            return
        src_pos = pygame.Vector2(self.rect.center)
        dest_pos = pygame.Vector2(glob_var["camera"].rect.topleft) + pygame.Vector2(mouse_pos) - pygame.Vector2(MAZE_SIZE * TILE_WIDTH, 0)
        vel = dest_pos - src_pos
        vel = vel.normalize() * 15
        Projectile(self, self.attack, self.rect.center, vel, self.location.cm)
    def dead(self):
        print("yay im dead")
    def move_to(self, next_cell):
        self.moving_state = 'transition'
        for obj in Projectile.all_projectiles:
            obj.kill()
        current_cells[0].player_leave(self)
        next_cell.player_enter(self)
        if current_cells[0].type == 'e':
            glob_var["exited"] = True
            return
        next_cell.set_type('n')
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
    def render(self, surface):
        if self.shield:
            self.surface.fill("orange")
        else:
            self.surface.fill("red")
        surface.blit(self.surface, self.rect)

class Enemy(Unit):
    def __init__(self, cell, pos: pygame.Vector2, speed, health, attack):
        super().__init__(cell.pos + pos, speed, health, attack)
        self.state = 'idle'
        self.last_shoot_time = pygame.time.get_ticks()
        self.shoot_interval = 1000
        cell.enemies.add(self)
        cell.cm.add_dynamic(self)
    def shoot_bullet(self, target_pos: pygame.Vector2):
        src_pos = pygame.Vector2(self.rect.center)
        vel = (target_pos - src_pos).normalize() * 15 + pygame.Vector2(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        Projectile(self, self.attack, self.rect.center, vel, current_cells[0].cm)
    def render(self, surface):
        self.surface.fill("green")
        surface.blit(self.surface, self.rect)
    def dead(self):
        for _ in range(random.randint(1, 3)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.rect.center, vel, current_cells[0].cm)
        self.kill()
