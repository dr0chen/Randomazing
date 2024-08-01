import pygame

FONT = 'consolas'

SIZE = 5
SAFE_MOVES_TOTAL = SIZE + 2
WIDTH = SIZE * 100 + 800
HEIGHT = (SIZE + 1) * 100

all_small_cells = pygame.sprite.Group()
all_large_cells = pygame.sprite.Group()
all_tunnels = pygame.sprite.Group()

def get_all_cells():
    return [cell for cell in all_small_cells if cell.merge is None] + list(all_large_cells)

exitable = False
exited = False