import pygame
from utils import *

class DroppedItems(pygame.sprite.Sprite):
    all_items = pygame.sprite.Group()
    def __init__(self, pos: pygame.Vector2, vel: pygame.Vector2, cm):
        super().__init__()
        self.surface = pygame.Surface([ITEM_WIDTH, ITEM_HEIGHT])
        self.rect = pygame.Rect(pos, [ITEM_WIDTH, ITEM_HEIGHT])
        self.vel = vel
        self.vel_tmp = vel.copy()
        self.acc = pygame.Vector2(0, 0)
        self.cm = cm
        self.cm.add_dynamic(self)
        self.func = self.picked_up
        DroppedItems.all_items.add(self)
    def render(self, surface):
        pass
    def picked_up(self, player):
        pass

class ScorePoint(DroppedItems):
    def __init__(self, pos: pygame.Vector2, vel: pygame.Vector2, cm):
        super().__init__(pos, vel, cm)
        self.score = 1
    def render(self, surface):
        self.surface.fill("cyan")
        surface.blit(self.surface, self.rect)
    def picked_up(self, player):
        player.score += self.score
        self.kill()