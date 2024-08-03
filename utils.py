import pygame

FONT = 'consolas'

MAZE_SIZE = 5
SAFE_MOVES_TOTAL = MAZE_SIZE + 2
CELL_WIDTH = 800
CELL_HEIGHT = 600
TILE_WIDTH = 50
TILE_HEIGHT = 50
WIDTH = MAZE_SIZE * TILE_WIDTH + CELL_WIDTH
HEIGHT = max(MAZE_SIZE * TILE_HEIGHT + 100, CELL_HEIGHT)

current_cells = []

deltas = {
    'u': [pygame.Vector2(50, 0), pygame.Vector2(0, 0)], 
    'd': [pygame.Vector2(50, 0), pygame.Vector2(0, CELL_HEIGHT - 50)], 
    'l': [pygame.Vector2(0, 50), pygame.Vector2(0, 0)], 
    'r': [pygame.Vector2(0, 50), pygame.Vector2(CELL_WIDTH - 50, 0)]
}
lengths = {
    'u': 16,
    'd': 16,
    'l': 12,
    'r': 12
}

glob_var = {
    "exitable": False,
    "exited": False,
    "grid": None,
    "player": None,
    "camera": None
}

def colliderect(r1: pygame.Rect, r2: pygame.Rect):
    if r1.right <= r2.left or r2.right <= r1.left or r1.top >= r2.bottom or r2.top >= r1.bottom:
        return False
    return True

def collideborder(r: pygame.Rect, b: pygame.Rect):
    if r.left >= b.left and r.right <= b.right and r.top >= b.top and r.bottom <= b.bottom:
        return False
    return True

def is_inside(p: pygame.Vector2, r:pygame.Rect):
    return r.left <= p.x <= r.right and r.top <= p.y <= r.bottom

def switch_cell(cell):
    glob_var["camera"].set_bound(cell.bound)
    if glob_var["player"].state != 'transition':
        glob_var["player"].move_to(cell)