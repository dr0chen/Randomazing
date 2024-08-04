from utils import *
from player import *
from tile import *

class CollisionStrategy:
    def handle_collision(self, obj1, obj2):
        pass

class PlayerWallCollision:
    def handle_collision(self, player, wall):
        if not colliderect(player.rect, wall.rect):
            return
        if player.vel.x > 0:
            player.rect.left = wall.rect.left - 50
        if player.vel.x < 0:
            player.rect.left = wall.rect.right
        if player.vel.y > 0:
            player.rect.top = wall.rect.top - 50
        if player.vel.y < 0:
            player.rect.top = wall.rect.bottom
        player.vel.x = 0
        player.vel.y = 0

class PlayerTunnelEntryCollision:
    def handle_collision(self, player, tunnel_entry):
        if tunnel_entry.tunnel.merge or not colliderect(player.rect, tunnel_entry.rect):
            return
        if tunnel_entry.tunnel.opened:
            if player.vel * tunnel_entry.direction > 0:
                player.facing = [tunnel_entry.direction.x, tunnel_entry.direction.y]
                player.location = tunnel_entry.tunnel
                next_cell = tunnel_entry.next_cell if tunnel_entry.next_cell.merge is None else tunnel_entry.next_cell.merge
                if next_cell in current_cells:
                    current_cells.remove(next_cell)
                current_cells.append(next_cell)
                switch_cell(next_cell)
        else:
            if player.vel.x > 0:
                player.rect.left = tunnel_entry.rect.left - 50
            if player.vel.x < 0:
                player.rect.left = tunnel_entry.rect.right
            if player.vel.y > 0:
                player.rect.top = tunnel_entry.rect.top - 50
            if player.vel.y < 0:
                player.rect.top = tunnel_entry.rect.bottom
            player.vel.x = 0
            player.vel.y = 0

class CollisionManager:
    def __init__(self):
        self.static_objects = []
        self.dynamic_objects = []
        self.strategies = {}
    def add_static(self, object):
        self.static_objects.append(object)
    def add_dynamic(self, object):
        self.dynamic_objects.append(object)
    def remove(self, object):
        if object in self.static_objects:
            self.static_objects.remove(object)
        else:
            self.dynamic_objects.remove(object)
    def register_strategy(self, type1, type2, strategy):
        self.strategies[(type1, type2)] = strategy
    def get_strategy(self, object1, object2):
        return self.strategies.get((type(object1), type(object2)))
    def check_collisions(self):
        for obj1 in self.dynamic_objects:
            for obj2 in self.static_objects + self.dynamic_objects:
                strategy = self.get_strategy(obj1, obj2)
                if strategy:
                    strategy.handle_collision(obj1, obj2)

def update():
    player = glob_var["player"]
    cm = player.location.cm
    player.acc = pygame.Vector2(0, 0)
    max_speed = player.speed
    if player.state == 'free':
        if glob_var["grid"].should_randomize:
            glob_var["grid"].randomize()
        player.location = current_cells[0]
        pressed_keys = pygame.key.get_pressed()
        player.facing = [0, 0]
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            player.acc.x -= player.speed / 2
            player.facing[0] -= 1
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            player.acc.x += player.speed / 2
            player.facing[0] += 1
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            player.acc.y -= player.speed / 2
            player.facing[1] -= 1
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            player.acc.y += player.speed / 2
            player.facing[1] += 1
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            max_speed = 5
    elif player.state == 'transition':
        player.acc.x += player.facing[0] * player.speed / 2
        player.acc.y += player.facing[1] * player.speed / 2
    else:
        assert(0)
    if player.vel != (0, 0):
        player.acc -= player.vel.normalize()
    vel_tmp = player.vel + player.acc
    if player.vel.x * vel_tmp.x < 0:
        player.vel.x = 0
    else:
        player.vel.x = vel_tmp.x
    if player.vel.y * vel_tmp.y < 0:
        player.vel.y = 0
    else:
        player.vel.y = vel_tmp.y
    if player.vel.length() > max_speed:
        player.vel = player.vel.normalize() * max_speed
    player.rect.left += player.vel.x
    vel_y = player.vel.y
    player.vel.y = 0
    cm.check_collisions()
    player.vel.y = vel_y
    player.rect.top += player.vel.y
    vel_x = player.vel.x
    player.vel.x = 0
    cm.check_collisions()
    player.vel.x = vel_x
    if current_cells[-1].is_including(player.rect):
        player.state = 'free'