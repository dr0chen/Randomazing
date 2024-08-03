import pygame
from utils import *
from camera import *

class Tile(pygame.sprite.Sprite):
    all_tiles = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2):
        super().__init__()
        self.surface = pygame.Surface([50, 50])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect(pos, [50, 50])
        Tile.add(self)
    def render(self, surface):
        surface.blit(self.surface, self.rect)
    def handle_collision(self, player) -> bool:
        pass

class Wall(Tile):
    all_walls = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2):
        super().__init__(pos)
        self.surface.fill("white")
        self.add(Wall.all_walls)
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
    def __init__(self, pos: pygame.Vector2, tunnel, direction: pygame.Vector2):
        super().__init__(pos)
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
        if self.tunnel.opened:
            self.rect.topleft = self.poses[0]
            self.surface.fill("black")
        else:
            self.rect.topleft = self.poses[1]
            self.surface.fill("grey")
        surface.blit(self.surface, self.rect)
    def handle_collision(self, player) -> bool:
        if self.tunnel.merge is not None:
            return False
        if colliderect(player.rect, self.rect):
            if self.tunnel.opened:
                if player.vel * self.direction > 0:
                    player.facing = [self.direction.x, self.direction.y]
                    player.location = self.tunnel
                    next_cell = self.next_cell if self.next_cell.merge is None else self.next_cell.merge
                    if next_cell in current_cells:
                        current_cells.remove(next_cell)
                    current_cells.append(next_cell)
                    switch_cell(next_cell)
            else:
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
