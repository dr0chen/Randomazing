import pygame
import random
from utils import *
from projectile import *
from droppeditem import *

class Unit(pygame.sprite.Sprite):
    def __init__(self, cell, pos: pygame.Vector2, speed, health, attack):
        super().__init__()
        self.surface = pygame.Surface([UNIT_WIDTH, UNIT_HEIGHT])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.hb_surface = pygame.Surface([HB_WIDTH, HB_HEIGHT])
        self.hb_surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect((0, 0), [UNIT_WIDTH, UNIT_HEIGHT])
        self.rect.center = cell.pos + pos
        self.speed = speed
        self.max_health = health
        self.health = health
        self.attack = attack
        self.vel = pygame.Vector2(0, 0)
        self.location = cell
    def render(self, surface):
        if self.health == self.max_health:
            return
        dest = pygame.Rect(self.rect.topleft, [HB_WIDTH, HB_HEIGHT])
        dest.center = pygame.Vector2(self.rect.center) - pygame.Vector2(0, UNIT_HEIGHT / 2 + 10)
        self.hb_surface.fill("black")
        pygame.draw.rect(self.hb_surface, "red", pygame.Rect((0, 0), [HB_WIDTH * self.health / self.max_health, HB_HEIGHT]))
        surface.blit(self.hb_surface, dest)
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.dead()
    def dead(self):
        pass

class Player(Unit):
    def __init__(self, cell, speed, health, attack):
        super().__init__(cell, pygame.Vector2(CELL_WIDTH / 2, CELL_HEIGHT / 2), speed, health, attack)
        self.rect.center = cell.bound.center
        self.acc = pygame.Vector2(0, 0)
        self.facing = [1, 0]
        self.shield = False
        self.moving_state = 'free'
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
        self.shooting_interval = 500
        self.items = [['shooter', float('INF')]]
        self.curr_item_idx = 0
        self.last_shoot_time = pygame.time.get_ticks()
        self.location.player_enter(self)
    def pickup_item(self, item_name, item_cnt):
        for item in self.items:
            if item[0] == item_name:
                item[1] += item_cnt
                break
        else:
            self.items.append([item_name, item_cnt])
    def switch_item(self):
        self.curr_item_idx = (self.curr_item_idx + 1) % len(self.items)
    def use_item(self, mouse_pos):
        curr_item = self.items[self.curr_item_idx]
        match curr_item[0]:
            case 'shooter':
                self.shoot_bullet(mouse_pos)
            case 'knife':
                pass
            case 'health_potion':
                if self.health == self.max_health:
                    return
                self.health += self.health
                self.health = min(self.health, self.max_health)
            case 'key':
                pass
        curr_item[1] -= 1
        if curr_item[1] <= 0:
            self.items.pop(self.curr_item_idx)
            self.curr_item_idx = min(self.curr_item_idx + 1, len(self.items) - 1)
    def shoot_bullet(self, mouse_pos):
        curr_time = pygame.time.get_ticks()
        if self.moving_state != 'free' or self.shield or curr_time - self.last_shoot_time <= self.shooting_interval:
            return
        self.last_shoot_time = curr_time
        src_pos = pygame.Vector2(self.rect.center)
        dest_pos = pygame.Vector2(glob_var["camera"].rect.topleft) + pygame.Vector2(mouse_pos) - pygame.Vector2(MAZE_SIZE * TILE_WIDTH, 0)
        vel = dest_pos - src_pos
        if vel == pygame.Vector2(0, 0):
            return
        vel = vel.normalize() * 10
        Projectile(self, self.attack, self.rect.center, vel, self.location.cm)
    def take_damage(self, damage):
        if self.shield:
            return
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.dead()
    def dead(self):
        print("yay im dead")
    def move_to(self, next_cell):
        self.moving_state = 'transition'
        for obj in Projectile.all_projectiles:
            obj.kill()
        current_cells[0].player_leave(self)
        next_cell.player_enter(self)
        if current_cells[0].content == 'e':
            glob_var["exited"] = True
            return
        next_cell.set_content('n')
        self.safe_moves -= 1
        self.moves += 1
        if glob_var["exitable"]:
            if self.safe_moves <= 0:
                self.rand_prob = 50
                if random.randint(1, 100) < self.rand_prob:
                    self.rand_prob = 0
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
        super().render(surface)

class Enemy(Unit):
    def __init__(self, cell, pos: pygame.Vector2, speed, health, attack):
        super().__init__(cell, pos, speed, health, attack)
        self.state = 'idle'
        self.timer = pygame.time.get_ticks()
        self.idle_interval = 125
        self.move_interval = 500
        self.shoot_interval = 125
        self.target = pygame.Vector2(0, 0)
        self.vel_tmp = self.vel.copy()
        cell.enemies.add(self)
        cell.cm.add_dynamic(self)
    def shoot_bullet(self, target_pos: pygame.Vector2):
        src_pos = pygame.Vector2(self.rect.center)
        vel = (target_pos - src_pos).normalize() * 10 + pygame.Vector2(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
        Projectile(self, self.attack, self.rect.center, vel, current_cells[0].cm)
    def render(self, surface):
        self.surface.fill("green")
        surface.blit(self.surface, self.rect)
        super().render(surface)
    def dead(self):
        for _ in range(random.randint(1, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel)
        self.kill()