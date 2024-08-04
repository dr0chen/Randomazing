import pygame
from utils import *
from unit import *

class Projectile(pygame.sprite.Sprite):
    all_projectiles = pygame.sprite.Group()
    def __init__(self, owner: Unit, damage, pos: pygame.Vector2, vel: pygame.Vector2, cm):
        super().__init__()
        self.surface = pygame.Surface([10, 10])
        self.surface.fill("yellow")
        self.rect = pygame.Rect(pos, [10, 10])
        self.damage = damage
        self.vel = vel
        self.owner = owner
        Projectile.all_projectiles.add(self)
        cm.add_dynamic(self)
    def update(self):
        self.rect.topleft += self.vel
        if surpassborder(self.rect, glob_var["scene"].get_rect()):
            self.kill()
    def render(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)