import pygame
import random
from utils import *
from projectile import *
from droppeditem import *
from closearea import *
from tile import *

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
    def action(self):
        pass
    def dead(self):
        pass

class Player(Unit):
    def __init__(self, cell, speed, health, attack):
        super().__init__(cell, pygame.Vector2(CELL_WIDTH / 2, CELL_HEIGHT / 2), speed, health, attack)
        self.rect.center = cell.bound.center
        self.closearea = CloseArea(self.rect.center)
        self.acc = pygame.Vector2(0, 0)
        self.facing = [1, 0]
        self.shield = 0
        self.moving_state = 'free'
        self.rand_prob = 0
        self.safe_moves = SAFE_MOVES_TOTAL
        self.moves = 0
        self.score = 0
        self.batteries = 0
        self.attack_interval = 500
        self.items = [['Knife', float('INF')]]
        self.curr_item_idx = -1
        self.switch_item('r')
        self.attack_timer = pygame.time.get_ticks()
        self.location.player_enter(self)
    def pickup_item(self, item_name, item_cnt):
        for item in self.items:
            if item[0] == item_name:
                item[1] += item_cnt
                break
        else:
            self.items.append([item_name, item_cnt])
    def switch_item(self, direction):
        match direction:
            case 'l':
                self.curr_item_idx = (self.curr_item_idx - 1) % len(self.items)
            case 'r':
                self.curr_item_idx = (self.curr_item_idx + 1) % len(self.items)
        match self.items[self.curr_item_idx][0]:
            case 'Knife':
                self.closearea.set_func(lambda obj: obj.take_damage(random.randint(self.attack-1, self.attack+3)) if isinstance(obj, Enemy) else None)
                self.closearea.set_render(knife_render)
            case 'Key':
                self.closearea.set_func(lambda obj: self.open_chest(obj) if isinstance(obj, Chest) else None)
                self.closearea.set_render(key_render)
    def use_item(self, mouse_pos: pygame.Vector2):
        curr_item = self.items[self.curr_item_idx]
        match curr_item[0]:
            case 'Shooter':
                self.shoot_bullet(mouse_pos)
            case 'Knife':
                self.knife_attack(mouse_pos)
            case 'Health Potion':
                if self.health == self.max_health:
                    return
                self.health += 20
                self.health = min(self.health, self.max_health)
            case 'Key':
                self.closearea.activate(0, 16)
                return
        curr_item[1] -= 1
        if curr_item[1] <= 0:
            self.items.pop(self.curr_item_idx)
            self.curr_item_idx = min(self.curr_item_idx + 1, len(self.items) - 1)
            match self.items[self.curr_item_idx][0]:
                case 'Knife':
                    self.closearea.set_func(lambda obj: obj.take_damage(random.randint(self.attack-1, self.attack+3)) if isinstance(obj, Enemy) else None)
                    self.closearea.set_render(knife_render)
                case 'Key':
                    self.closearea.set_func(lambda obj: self.open_chest(obj) if isinstance(obj, Chest) else None)
                    self.closearea.set_render(key_render)
    def open_chest(self, chest):
        if chest.opened:
            return
        items = random.choice(chest.loot_table)
        for item in items:
            if type(item) is tuple:
                item[0](chest.cell, pygame.Vector2(chest.rect.center), pygame.Vector2(0, 0), item[1])
            else:
                item(chest.cell, pygame.Vector2(chest.rect.center) - chest.cell.pos, pygame.Vector2(0, 0))
        chest.opened = True
        curr_item = self.items[self.curr_item_idx]
        curr_item[1] -= 1
        if curr_item[1] <= 0:
            self.items.pop(self.curr_item_idx)
            self.curr_item_idx = min(self.curr_item_idx + 1, len(self.items) - 1)
            match self.items[self.curr_item_idx][0]:
                case 'Knife':
                    self.closearea.set_func(lambda obj: obj.take_damage(random.randint(self.attack-1, self.attack+3)) if isinstance(obj, Enemy) else None)
                    self.closearea.set_render(knife_render)
                case 'Key':
                    self.closearea.set_func(lambda obj: self.open_chest(obj) if isinstance(obj, Chest) else None)
                    self.closearea.set_render(key_render)
    def knife_attack(self, mouse_pos: pygame.Vector2):
        curr_time = pygame.time.get_ticks()
        if self.moving_state != 'free' or self.shield or curr_time - self.attack_timer <= self.attack_interval:
            return
        self.attack_timer = curr_time
        src_pos = pygame.Vector2(self.rect.center)
        dest_pos = mouse_pos
        direction = get_direction(src_pos, dest_pos)
        match direction:
            case 'u':
                start = 10
            case 'ur':
                start = -4
            case 'r':
                start = -2
            case 'dr':
                start = 0
            case 'd':
                start = 2
            case 'dl':
                start = 4
            case 'l':
                start = 6
            case 'ul':
                start = 8
        self.closearea.activate(start, start + 5)
    def shoot_bullet(self, mouse_pos: pygame.Vector2):
        curr_time = pygame.time.get_ticks()
        if self.moving_state != 'free' or self.shield or curr_time - self.attack_timer <= self.attack_interval:
            return
        self.attack_timer = curr_time
        src_pos = pygame.Vector2(self.rect.center)
        dest_pos = mouse_pos
        vel = dest_pos - src_pos
        if vel == pygame.Vector2(0, 0):
            return
        vel = vel.normalize() * 10
        Projectile(self, random.randint(self.attack, self.attack+5), self.rect.center, vel, self.location.cm)
    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= 1
            return
        # self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.dead()
    def action(self):
        grid = glob_var["grid"]
        #player get acc and calc vel
        self.acc = pygame.Vector2(0, 0)
        max_speed = self.speed
        if self.moving_state == 'free': #if free, read keyboard inputs
            if grid.should_randomize:
                grid.randomize()
            self.location = current_cells[0]
            pressed_keys = pygame.key.get_pressed()
            facing_tmp = [0, 0]
            if pressed_keys[pygame.K_a]:
                self.acc.x -= self.speed / 2
                facing_tmp[0] -= 1
            if pressed_keys[pygame.K_d]:
                self.acc.x += self.speed / 2
                facing_tmp[0] += 1
            if pressed_keys[pygame.K_w]:
                self.acc.y -= self.speed / 2
                facing_tmp[1] -= 1
            if pressed_keys[pygame.K_s]:
                self.acc.y += self.speed / 2
                facing_tmp[1] += 1
            if facing_tmp != [0, 0]:
                self.facing = facing_tmp
            if self.shield > 0:
                max_speed = 2
        elif self.moving_state == 'transition': #if in transition, move in the tunnel direction
            self.acc.x += self.facing[0] * self.speed / 2
            self.acc.y += self.facing[1] * self.speed / 2
        else:
            assert(0)
        #friction
        if self.vel != pygame.Vector2(0, 0):
            self.acc -= self.vel.normalize() * 2
        vel_tmp = self.vel + self.acc
        if self.vel.x * vel_tmp.x < 0:
            self.vel.x = 0
        else:
            self.vel.x = vel_tmp.x
        if self.vel.y * vel_tmp.y < 0:
            self.vel.y = 0
        else:
            self.vel.y = vel_tmp.y
        #no more than max_speed
        if self.vel.length() > max_speed:
            self.vel = self.vel.normalize() * max_speed
    def dead(self):
        glob_var["dead"] = True
    def move_to(self, next_cell):
        self.moving_state = 'transition'
        for obj in Projectile.all_projectiles:
            obj.kill()
        current_cells[0].player_leave(self)
        next_cell.player_enter(self)
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
        self.closearea.render(surface)
        if self.shield > 0:
            self.surface.fill("orange")
        else:
            self.surface.fill("red")
        surface.blit(self.surface, self.rect)
        super().render(surface)

class Enemy(Unit):
    def __init__(self, cell, pos: pygame.Vector2, speed, health, attack):
        super().__init__(cell, pos, speed, health, attack)
        self.timer = pygame.time.get_ticks()
        self.target = pygame.Vector2(0, 0)
        self.vel_tmp = self.vel.copy()
        cell.enemies.add(self)
        cell.cm.add_dynamic(self)
    def shoot_bullet(self, target_pos: pygame.Vector2, bullet_speed):
        src_pos = pygame.Vector2(self.rect.center)
        vel = (target_pos - src_pos).normalize() * bullet_speed
        Projectile(self, random.randint(self.attack, self.attack+2), self.rect.center, vel, current_cells[0].cm)
    def render(self, surface):
        super().render(surface)
    def action(self):
        pass
    def dead(self):
        pass

class NormalEnemy(Enemy):
    def __init__(self, cell, pos: pygame.Vector2):
        super().__init__(cell, pos, 5, 20, 5)
        self.state = 'idle'
        self.idle_interval = random.randint(300, 400)
        self.move_interval = random.randint(500, 750)
        self.shoot_interval = 250
    def render(self, surface):
        self.surface.fill("darkgreen")
        surface.blit(self.surface, self.rect)
        super().render(surface)
    def action(self):
        player = glob_var["player"]
        curr_time = pygame.time.get_ticks()
        match self.state:
            case 'idle':
                self.vel = pygame.Vector2(0, 0)
                if curr_time > self.timer + self.idle_interval:
                    self.state = 'move'
                    self.timer = curr_time
                    self.move_interval = random.randint(500, 750)
                    bias = pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
                    self.target = pygame.Vector2(player.rect.center) + (pygame.Vector2(self.rect.center) - pygame.Vector2(player.rect.center)).normalize() * 250 + bias
                    delta = self.target - pygame.Vector2(self.rect.center)
                    self.vel = delta.normalize() * min(self.speed, delta.length())
            case 'move':
                delta = self.target - pygame.Vector2(self.rect.center)
                self.vel = delta.normalize() * min(self.speed, delta.length())
                if curr_time > self.timer + self.move_interval or self.target == pygame.Vector2(self.rect.center):
                    self.state = 'shoot'
                    self.timer = curr_time
                    self.vel = pygame.Vector2(0, 0)
            case 'shoot':
                self.vel = pygame.Vector2(0, 0)
                if curr_time > self.timer + self.shoot_interval:
                    self.shoot_bullet(pygame.Vector2(player.rect.center), 7)
                    self.timer = curr_time
                    self.state = 'idle'
                    self.idle_interval = random.randint(300, 400)
    def dead(self):
        for _ in range(random.randint(1, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel, None)
        self.kill()

class KeyGuard(Enemy):
    def __init__(self, cell, pos: pygame.Vector2):
        super().__init__(cell, pos, 3, 40, 5)
        self.state = 'idle'
        self.idle_interval = random.randint(300, 400)
        self.move_interval = random.randint(600, 850)
        self.shoot_interval = 250
        self.shoot_interval2 = 100
        self.shoot_cnt = 0
    def render(self, surface):
        self.surface.fill("darkblue")
        surface.blit(self.surface, self.rect)
        super().render(surface)
    def action(self):
        player = glob_var["player"]
        curr_time = pygame.time.get_ticks()
        match self.state:
            case 'idle':
                self.vel = pygame.Vector2(0, 0)
                if curr_time > self.timer + self.idle_interval:
                    self.state = 'move'
                    self.timer = curr_time
                    self.move_interval = random.randint(600, 850)
                    bias = pygame.Vector2(random.uniform(-150, 150), random.uniform(-150, 150))
                    self.target = pygame.Vector2(player.rect.center) + (pygame.Vector2(self.rect.center) - pygame.Vector2(player.rect.center)).normalize() * 300 + bias
                    delta = self.target - pygame.Vector2(self.rect.center)
                    self.vel = delta.normalize() * min(self.speed, delta.length())
            case 'move':
                delta = self.target - pygame.Vector2(self.rect.center)
                self.vel = delta.normalize() * min(self.speed, delta.length())
                if curr_time > self.timer + self.move_interval or self.target == pygame.Vector2(self.rect.center):
                    self.state = 'shoot'
                    self.timer = curr_time
                    self.vel = pygame.Vector2(0, 0)
            case 'shoot':
                self.vel = pygame.Vector2(0, 0)
                if self.shoot_cnt == 0:
                    if curr_time > self.timer + self.shoot_interval:
                        self.target = pygame.Vector2(player.rect.center)
                        self.shoot_bullet(self.target, 9)
                        dist = (self.target - pygame.Vector2(self.rect.center)).length()
                        ortho = pygame.Vector2(self.target.y - self.rect.center[1], self.rect.center[0] - self.target.x).normalize() * dist * 0.87
                        self.shoot_bullet(self.target + ortho, 7)
                        self.shoot_bullet(self.target - ortho, 7)
                        self.shoot_cnt += 1
                        self.timer = curr_time
                else:
                    if curr_time > self.timer + self.shoot_interval2:
                        self.shoot_bullet(self.target, 10)
                        dist = (self.target - pygame.Vector2(self.rect.center)).length()
                        ortho = pygame.Vector2(self.target.y - self.rect.center[1], self.rect.center[0] - self.target.x).normalize() * dist * 0.87
                        self.shoot_bullet(self.target + ortho, 7)
                        self.shoot_bullet(self.target - ortho, 7)
                        self.shoot_cnt += 1
                        self.timer = curr_time
                if self.shoot_cnt >= 3:
                    self.shoot_cnt = 0
                    self.timer = curr_time
                    self.state = 'idle'
                    self.idle_interval = random.randint(300, 400)
    def dead(self):
        for _ in range(random.randint(2, 4)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel, None)
        for _ in range(random.randint(1, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            Key(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel)
        self.kill()

class Turret(Enemy):
    def __init__(self, cell, pos: pygame.Vector2, countercw: bool):
        super().__init__(cell, pos, 0, 50, 5)
        self.offset = 0
        self.countercw = countercw
        self.shoot_interval = 25
        self.shoot_cnt = 0
    def take_damage(self, damage):
        self.health -= 1
        if self.health <= 0:
            self.health = 0
            self.dead()
    def render(self, surface):
        self.surface.fill("darkgrey")
        surface.blit(self.surface, self.rect)
        super().render(surface)
    def action(self):
        curr_time = pygame.time.get_ticks()
        if curr_time > self.timer + self.shoot_interval:
            self.timer = curr_time
            for i in range(4):
                self.shoot_bullet(pygame.Vector2(self.rect.center) + pygame.Vector2(math.cos(math.pi*self.offset/32+math.pi*i/2), math.sin(math.pi*self.offset/32+math.pi*i/2)), 10)
            self.shoot_cnt += 1
            if self.shoot_cnt >= 4:
                self.shoot_cnt = 0
                if self.countercw:
                    self.offset = (self.offset - 1) % 32
                else:
                    self.offset = (self.offset + 1) % 32
    def dead(self):
        for _ in range(random.randint(1, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel, None)
        for _ in range(random.randint(0, 1)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            HealthPotion(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel)
        self.kill()

class Elite(Enemy):
    def __init__(self, cell, pos: pygame.Vector2):
        super().__init__(cell, pos, 10, 30, 10)
        self.state = 'idle'
        self.idle_interval = random.randint(250, 350)
        self.move_interval = random.randint(400, 600)
        self.shoot_interval = 200
    def render(self, surface):
        self.surface.fill("crimson")
        surface.blit(self.surface, self.rect)
        super().render(surface)
    def action(self):
        player = glob_var["player"]
        curr_time = pygame.time.get_ticks()
        match self.state:
            case 'idle':
                self.vel = pygame.Vector2(0, 0)
                if curr_time > self.timer + self.idle_interval:
                    self.state = 'move'
                    self.timer = curr_time
                    self.move_interval = random.randint(400, 600)
                    bias = pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
                    self.target = pygame.Vector2(player.rect.center) + (pygame.Vector2(self.rect.center) - pygame.Vector2(player.rect.center)).normalize() * 250 + bias
                    delta = self.target - pygame.Vector2(self.rect.center)
                    self.vel = delta.normalize() * min(self.speed, delta.length())
            case 'move':
                delta = self.target - pygame.Vector2(self.rect.center)
                self.vel = delta.normalize() * min(self.speed, delta.length())
                if curr_time > self.timer + self.move_interval or self.target == pygame.Vector2(self.rect.center):
                    self.state = 'shoot'
                    self.timer = curr_time
                    self.vel = pygame.Vector2(0, 0)
            case 'shoot':
                self.vel = pygame.Vector2(0, 0)
                if curr_time > self.timer + self.shoot_interval:
                    self.shoot_bullet(pygame.Vector2(player.rect.center), 7)
                    self.timer = curr_time
                    self.state = 'idle'
                    self.idle_interval = random.randint(250, 350)
    def dead(self):
        for _ in range(random.randint(1, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel, 2)
        for _ in range(random.randint(2, 3)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            ScorePoint(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel, None)
        for _ in range(random.randint(0, 2)):
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            HealthPotion(self.location, pygame.Vector2(self.rect.center) - self.location.pos, vel)
        self.kill()
