import pygame
from utils import *

class Camera:
    def __init__(self, scene, init_pos):
        self.rect = pygame.Rect(init_pos.x, init_pos.y, CELL_WIDTH, CELL_HEIGHT)
        self.bound = self.rect
        self.scene = scene
    def set_bound(self, bound):
        self.bound = bound
    def follow(self, pos):
        dest = self.rect.copy()
        dest.center = pos
        dest.left = max(dest.left, self.bound.left)
        dest.right = min(dest.right, self.bound.right)
        dest.top = max(dest.top, self.bound.top)
        dest.bottom = min(dest.bottom, self.bound.bottom)
        delta = pygame.Vector2(dest.center) - pygame.Vector2(self.rect.center)
        speed = delta.length()
        if speed > 0:
            delta = delta.normalize() * max(speed * 0.15, min(2, speed))
        self.rect.center += delta