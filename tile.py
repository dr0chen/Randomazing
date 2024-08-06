import pygame
import random
from utils import *

class Tile(pygame.sprite.Sprite):
    all_tiles = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2, cm, group: str):
        super().__init__()
        self.surface = pygame.Surface([50, 50])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect(pos, [50, 50])
        Tile.all_tiles.add(self)
        match group:
            case 'static':
                cm.add_static(self)
            case 'dynamic':
                cm.add_dynamic(self)
    def render(self, surface):
        surface.blit(self.surface, self.rect)
    def handle_collision(self, player) -> bool:
        pass

class Wall(Tile):
    all_walls = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2, cm):
        super().__init__(pos, cm, 'static')
        self.surface.fill("white")
        Wall.all_walls.add(self)
    def handle_collision(self, player) -> bool:
        if colliderect(player.rect, self.rect):
            if player.vel.x > 0:
                player.rect.left = self.rect.left - 50
            if player.vel.x < 0:
                player.rect.left = self.rect.right
            if player.vel.y > 0:
                player.rect.top = self.rect.top - 50
            if player.vel.y < 0:
                player.rect.top = self.rect.bottom
            player.vel.x = 0
            player.vel.y = 0
            return True
        return False

class TunnelEntry(Tile):
    def __init__(self, pos: pygame.Vector2, tunnel, direction: pygame.Vector2, cm):
        super().__init__(pos, cm, 'static')
        self.tunnel = tunnel
        self.direction = direction
        self.poses = [pos, pos - direction * 50]
        if direction == pygame.Vector2(-1, 0) or direction == pygame.Vector2(0, -1):
            self.next_cell = tunnel.relations[0]
        else:
            self.next_cell = tunnel.relations[1]
    def render(self, surface):
        if self.tunnel.merge is not None:
            return
        if self.tunnel.opened and not self.tunnel.closed_down:
            self.rect.topleft = self.poses[0]
            self.surface.fill("black")
        else:
            self.rect.topleft = self.poses[1]
            self.surface.fill("grey")
        surface.blit(self.surface, self.rect)

class Chest(Tile):
    def __init__(self, cell, pos: pygame.Vector2, loot_table):
        super().__init__(pygame.Vector2(0, 0), cell.cm, 'dynamic')
        self.rect.center = cell.pos + pos
        self.loot_table = loot_table
        self.cell = cell
        self.opened = False
        self.func = self.opening
    def opening(self, _):
        items = random.choice(self.loot_table)
        for item in items:
            vel = pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
            if type(item) is tuple:
                item[0](self.cell, pygame.Vector2(self.rect.center), vel, item[1])
            else:
                item(self.cell, pygame.Vector2(self.rect.center), vel)
        self.opened = True
    def render(self, surface):
        if self.opened:
            self.surface.fill("darkgoldenrod")
        else:
            self.surface.fill("darkgoldenrod1")
        surface.blit(self.surface, self.rect)