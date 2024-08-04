import pygame
from utils import *
from player import *
from tile import *

class CollisionStrategy:
    def handle_collision(self, obj1, obj2):
        pass

class PlayerWallCollision(CollisionStrategy):
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

class PlayerTunnelEntryCollision(CollisionStrategy):
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

class ProjectileWallCollision(CollisionStrategy):
    def handle_collision(self, projectile, wall):
        if colliderect(projectile.rect, wall.rect):
            projectile.kill()

class ProjectileTunnelEntryCollision(CollisionStrategy):
    def handle_collision(self, projectile, tunnel_entry):
        if colliderect(projectile.rect, tunnel_entry.rect):
            projectile.kill()

class CollisionManager:
    def __init__(self):
        self.static_objects = pygame.sprite.Group()
        self.dynamic_objects = pygame.sprite.Group()
        self.strategies = {}
    def add_static(self, object):
        self.static_objects.add(object)
    def add_dynamic(self, object):
        self.dynamic_objects.add(object)
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
            for obj2 in list(self.static_objects) + list(self.dynamic_objects):
                strategy = self.get_strategy(obj1, obj2)
                if strategy:
                    strategy.handle_collision(obj1, obj2)