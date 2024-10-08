import pygame
from utils import *
from unit import *
from tile import *
from projectile import *
from droppeditem import *
from closearea import *

class CollisionStrategy:
    def handle_collision(self, obj1, obj2):
        pass

class StopStrategy(CollisionStrategy):
    def handle_collision(self, obj1, obj2):
        if colliderect(obj1.rect, obj2.rect):
            if obj1.vel.x > 0:
                obj1.rect.left = obj2.rect.left - obj1.rect.w
            if obj1.vel.x < 0:
                obj1.rect.left = obj2.rect.right
            if obj1.vel.y > 0:
                obj1.rect.top = obj2.rect.top - obj1.rect.h
            if obj1.vel.y < 0:
                obj1.rect.top = obj2.rect.bottom
            obj1.vel.x = 0
            obj1.vel.y = 0

class ChestStrategy(StopStrategy):
    def handle_collision(self, obj, chest):
        if not chest.opened and colliderect(obj.rect, chest.rect):
            super().handle_collision(obj, chest)

class TunnelStrategy(StopStrategy):
    def handle_collision(self, player, tunnel_entry):
        if tunnel_entry.tunnel.merge:
            return
        if colliderect(player.rect, tunnel_entry.rect):
            if tunnel_entry.tunnel.opened and not tunnel_entry.tunnel.merge and not tunnel_entry.tunnel.closed_down:
                if player.vel * tunnel_entry.direction > 0:
                    player.facing = [tunnel_entry.direction.x, tunnel_entry.direction.y]
                    player.vel = player.speed * pygame.Vector2(player.facing)
                    player.location = tunnel_entry.tunnel
                    next_cell = tunnel_entry.next_cell if not tunnel_entry.next_cell.merge else tunnel_entry.next_cell.merge
                    if next_cell in current_cells:
                        current_cells.remove(next_cell)
                    current_cells.append(next_cell)
                    switch_cell(next_cell)
            else:
                super().handle_collision(player, tunnel_entry)

class VanishStrategy(CollisionStrategy):
    def handle_collision(self, obj1, obj2):
        if colliderect(obj1.rect, obj2.rect):
            obj1.kill()

class BreakStrategy(VanishStrategy):
    def handle_collision(self, obj, tunnel_entry):
        if colliderect(obj.rect, tunnel_entry.rect):
            if tunnel_entry.tunnel.breakable and not tunnel_entry.tunnel.opened and not tunnel_entry.tunnel.closed_down:
                tunnel_entry.tunnel.opened = True
            super().handle_collision(obj, tunnel_entry)

class CloseAreaBreakStrategy(CollisionStrategy):
    def handle_collision(self, closearea, tunnel_entry):
        if closearea.collidewithrect(tunnel_entry.rect):
            if tunnel_entry.tunnel.breakable and not tunnel_entry.tunnel.opened and not tunnel_entry.tunnel.closed_down:
                tunnel_entry.tunnel.opened = True

class CloseAreaStrategy(CollisionStrategy):
    def handle_collision(self, closearea, obj):
        if closearea.collidewithrect(obj.rect):
            closearea.func(obj)

class FuncStrategy(CollisionStrategy):
    def handle_collision(self, obj1, obj2):
        if colliderect(obj1.rect, obj2.rect):
            obj1.func(obj2)

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
    def register_strategy(self, type1: type, type2: type, strategy: CollisionStrategy):
        typ_lst1 = get_subclasses(type1)
        typ_lst2 = get_subclasses(type2)
        for typ1 in typ_lst1:
            for typ2 in typ_lst2:
                self.strategies[(typ1, typ2)] = strategy
    def get_strategy(self, object1, object2):
        return self.strategies.get((type(object1), type(object2)))
    def check_collisions(self):
        for obj1 in self.dynamic_objects:
            for obj2 in list(self.static_objects) + list(self.dynamic_objects):
                strategy = self.get_strategy(obj1, obj2)
                if strategy:
                    strategy.handle_collision(obj1, obj2)

ss = StopStrategy()
ts = TunnelStrategy()
vs = VanishStrategy()
bs = BreakStrategy()
fs = FuncStrategy()
cs = ChestStrategy()
cas = CloseAreaStrategy()
cabs = CloseAreaBreakStrategy()

def deploy_cm() -> CollisionManager:
    cm = CollisionManager()
    cm.register_strategy(Unit, Wall, ss)
    cm.register_strategy(Unit, Chest, cs)
    cm.register_strategy(Player, TunnelEntry, ts)
    cm.register_strategy(Enemy, TunnelEntry, ss)
    cm.register_strategy(Projectile, Wall, vs)
    cm.register_strategy(Projectile, TunnelEntry, bs)
    cm.register_strategy(DroppedItems, Wall, ss)
    cm.register_strategy(DroppedItems, TunnelEntry, ss)
    cm.register_strategy(DroppedItems, Player, fs)
    cm.register_strategy(Projectile, Unit, fs)
    cm.register_strategy(CloseArea, Chest, cas)
    cm.register_strategy(CloseArea, Enemy, cas)
    cm.register_strategy(CloseArea, TunnelEntry, cabs)
    cm.register_strategy(Exit, Player, fs)
    return cm