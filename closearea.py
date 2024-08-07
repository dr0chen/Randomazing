import pygame
import pygame.gfxdraw
import math
from utils import *

lines = [pygame.Vector2(80 * math.cos(math.pi * i / 8), 80 * math.sin(math.pi * i / 8)) for i in range(16)]

def knife_render(closearea):
    pygame.draw.arc(closearea.surface, "silver", pygame.Rect((0, 0), [160, 160]), -math.pi*(closearea.end-1)/8, -math.pi*closearea.start/8, width=10)

def key_render(closearea):
    pass
    
class CloseArea(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.surface = pygame.Surface([160, 160])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.rect = pygame.Rect((0, 0), [160, 160])
        self.rect.center = pos
        self.activated = [False for _ in range(16)]
        self.timer = pygame.time.get_ticks()
        self.start = 0
        self.end = 0
        self.func = lambda _: None
        self.render_func = lambda _: None
    def set_func(self, func):
        self.func = func
    def set_render(self, render_func):
        self.render_func = render_func
    def move(self, pos):
        self.rect.center = pos
    def activate(self, start, end):
        self.start = start
        self.end = end
        for i in range(start, end):
            self.activated[i] = True
        self.timer = pygame.time.get_ticks()
    def deactivate(self, start, end):
        for i in range(start, end):
            self.activated[i] = False
    def collidewithrect(self, rect: pygame.Rect) -> bool:
        if not colliderect(self.rect, rect):
            return False
        for i in range(16):
            if not self.activated[i]:
                continue
            if collidesegmentrect(pygame.Vector2(self.rect.center), pygame.Vector2(self.rect.center) + lines[i], rect):
                return True
        return False
    def render(self, surface):
        self.surface.fill("black")
        if pygame.time.get_ticks() < self.timer + 100:
            self.render_func(self)
        surface.blit(self.surface, self.rect)