import pygame
import random
from utils import *

class DroppedItems(pygame.sprite.Sprite):
    all_items = pygame.sprite.Group()
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2):
        super().__init__()
        self.surface = pygame.Surface([ITEM_WIDTH, ITEM_HEIGHT])
        self.rect = pygame.Rect((0, 0), [ITEM_WIDTH, ITEM_HEIGHT])
        self.rect.center = cell.pos + pos
        self.vel = vel
        self.vel_tmp = vel.copy()
        self.acc = pygame.Vector2(0, 0)
        cell.cm.add_dynamic(self)
        self.func = self.picked_up
        DroppedItems.all_items.add(self)
    def render(self, surface):
        pass
    def picked_up(self, player):
        pass

class ScorePoint(DroppedItems):
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2, score):
        super().__init__(cell, pos, vel)
        if not score:
            self.score = random.randint(1, 2)
        else:
            self.score = score
    def render(self, surface):
        match self.score:
            case 1:
                self.surface.fill("cyan")
            case 2:
                self.surface.fill("yellow")
        surface.blit(self.surface, self.rect)
    def picked_up(self, player):
        player.score += self.score
        self.kill()

class Battery(DroppedItems):
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2):
        super().__init__(cell, pos, vel)
    def render(self, surface):
        self.surface.fill("blue")
        surface.blit(self.surface,self.rect)
    def picked_up(self, player):
        player.batteries += 1
        self.kill()

class HealthPotion(DroppedItems):
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2):
        super().__init__(cell, pos, vel)
    def render(self, surface):
        self.surface.fill("pink")
        surface.blit(self.surface, self.rect)
    def picked_up(self, player):
        player.pickup_item("Health Potion", 1)
        self.kill()

class Key(DroppedItems):
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2):
        super().__init__(cell, pos, vel)
    def render(self, surface):
        self.surface.fill("brown")
        surface.blit(self.surface, self.rect)
    def picked_up(self, player):
        player.pickup_item("Key", 1)
        self.kill()

class Shooter(DroppedItems):
    def __init__(self, cell, pos: pygame.Vector2, vel: pygame.Vector2):
        super().__init__(cell, pos, vel)
    def render(self, surface):
        self.surface.fill("gold")
        surface.blit(self.surface, self.rect)
    def picked_up(self, player):
        player.pickup_item("Shooter", 1)
        glob_var["has_shooter"] = True
        self.kill()    