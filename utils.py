import pygame
import math

FONT = 'consolas'

MAZE_SIZE = 5
SAFE_MOVES_TOTAL = MAZE_SIZE + 2
CELL_WIDTH = 800
CELL_HEIGHT = 600
TILE_WIDTH = 50
TILE_HEIGHT = 50
UNIT_WIDTH = 30
UNIT_HEIGHT = 30
ITEM_WIDTH = 20
ITEM_HEIGHT = 20
HB_WIDTH = 35
HB_HEIGHT = 5
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
directions = {
    'u': (math.radians(67.5), math.radians(112.5)),
    'ur': (math.radians(22.5), math.radians(67.5)),
    'r': (math.radians(-22.5), math.radians(22.5)),
    'dr': (math.radians(-67.5), math.radians(-22.5)),
    'd': (math.radians(-112.5), math.radians(-67.5)),
    'dl': (math.radians(-157.5), math.radians(-112.5)),
    'l': (math.radians(157.5), math.radians(-157.5)),
    'ul': (math.radians(112.5), math.radians(157.5)),
}

glob_var = {
    "exitable": False,
    "exited": False,
    "dead": False,
    "time_up": False,
    "has_shooter": False,
    "grid": None,
    "player": None,
    "scene": None,
    "camera": None,
    "font": None,
    "screen": None,
    "infotab": None,
    "clock": None,
    "timer_start": None,
    "timer": None,
    "timelimit_1": 1200,
    "timelimit_2": 120
}

def collidesegment(p1: pygame.Vector2, p2: pygame.Vector2, ps1: pygame.Vector2, ps2: pygame.Vector2, direction: str):
    match direction:
        case 'h':
            if not (min(p1.y, p2.y) <= ps1.y <= max(p1.y, p2.y)):
                return False
            if p2.y == p1.y:
                if max(p1.x, p2.x) < min(ps1.x, ps2.x) or max(ps1.x, ps2.x) < min(p1.x, p2.x):
                    return False
                else:
                    return True
            t = (ps1.y - p1.y) / (p2.y - p1.y)
            if not (0 <= t <= 1):
                return False
            x = p1.x + t * (p2.x - p1.x)
            if min(ps1.x, ps2.x) <= x <= max(ps1.x, ps2.x):
                return True
        case 'v':
            if not (min(p1.x, p2.x) <= ps1.x <= max(p1.x, p2.x)):
                return False
            if p2.x == p1.x:
                if max(p1.y, p2.y) < min(ps1.y, ps2.y) or max(ps1.y, ps2.y) < min(p1.y, p2.y):
                    return False
                else:
                    return True
            t = (ps1.x - p1.x) / (p2.x - p1.x)
            if not (0 <= t <= 1):
                return False
            y = p1.y + t * (p2.y - p1.y)
            if min(ps1.y, ps2.y) <= y <= max(ps1.y, ps2.y):
                return True
        case _:
            assert(0)
    
    return False

def collidesegmentrect(start: pygame.Vector2, end: pygame.Vector2, r: pygame.Rect):
    if collidesegment(start, end, pygame.Vector2(r.topleft), pygame.Vector2(r.topright), 'h'):
        return True
    if collidesegment(start, end, pygame.Vector2(r.bottomleft), pygame.Vector2(r.bottomright), 'h'):
        return True
    if collidesegment(start, end, pygame.Vector2(r.topright), pygame.Vector2(r.bottomright), 'v'):
        return True
    if collidesegment(start, end, pygame.Vector2(r.topleft), pygame.Vector2(r.bottomleft), 'v'):
        return True
    return False

def colliderect(r1: pygame.Rect, r2: pygame.Rect):
    if r1.right <= r2.left or r2.right <= r1.left or r1.top >= r2.bottom or r2.top >= r1.bottom:
        return False
    return True

def surpassborder(r: pygame.Rect, b: pygame.Rect):
    return r.left >= b.right or r.right <= b.left or r.top >= b.bottom or r.bottom <= b.top

def is_inside(p: pygame.Vector2, r:pygame.Rect):
    return r.left <= p.x <= r.right and r.top <= p.y <= r.bottom

def switch_cell(cell):
    glob_var["camera"].set_bound(cell.bound)
    if glob_var["player"].moving_state != 'transition':
        glob_var["player"].move_to(cell)

def get_direction(src_pos: pygame.Vector2, dest_pos: pygame.Vector2):
    if dest_pos.x == src_pos.x:
        if dest_pos.y <= src_pos.y:
            return 'u'
        else:
            return 'd'
    angle = -math.atan((dest_pos.y - src_pos.y) / (dest_pos.x - src_pos.x))
    if dest_pos.x < src_pos.x:
        if dest_pos.y >= src_pos.y:
            angle -= math.pi
        else:
            angle += math.pi
    for direction, (min_angle, max_angle) in directions.items():
        if min_angle <= angle < max_angle:
            return direction
    return 'l'

def get_subclasses(cls: type):
    subcls = [cls]
    curr = 0
    while curr < len(subcls):
        subcls += subcls[curr].__subclasses__()
        curr += 1
    return subcls