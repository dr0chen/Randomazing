from cell import *
from tile import *
from unit import *

contents = {
    '1': [
        [],
        [('normalenemy', (6, 6)), 
         ('normalenemy', (10, 6))],
        [('normalenemy', (8, 6))],
        [('keyguard', (8, 6))],
        [('turret', (8, 6), True)],
        [('turret', (8, 6), False)],
        [('healthpotion', (8, 6))],
        [('chest', (8, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])]
    ],
    'h2': [
        [],
        [('normalenemy', (8, 6)),
         ('normalenemy', (24, 6))],
        [('normalenemy', (6, 6)),
         ('normalenemy', (10, 6)),
         ('normalenemy', (22, 6)),
         ('normalenemy', (26, 6))],
        [('normalenemy', (8, 6)),
         ('keyguard', (16, 6)),
         ('normalenemy', (24, 6))],
        [('healthpotion', (16, 6))],
        [('chest', (16, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 6), True),
         ('turret', (24, 6), False)],
        [('turret', (8, 6), False),
         ('turret', (24, 6), True)],
    ],
    'v2': [
        [],
        [('normalenemy', (8, 6)),
         ('normalenemy', (8, 18))],
        [('normalenemy', (8, 6)),
         ('normalenemy', (10, 6)),
         ('normalenemy', (8, 18)),
         ('normalenemy', (10, 18))],
        [('normalenemy', (8, 6)),
         ('keyguard', (8, 12)),
         ('normalenemy', (8, 18))],
        [('healthpotion', (8, 12))],
        [('chest', (8, 12), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 6), True),
         ('turret', (8, 18), False)],
        [('turret', (8, 6), False),
         ('turret', (8, 18), True)],
    ],
    'ulL': [
        [],
        [('normalenemy', (24, 6)),
         ('normalenemy', (8, 6)),
         ('normalenemy', (8, 18))],
        [('normalenemy', (24, 6)),
         ('keyguard', (8, 6)),
         ('normalenemy', (8, 18))],
        [('normalenemy', (24, 6)),
         ('normalenemy', (10, 6)),
         ('normalenemy', (8, 8)),
         ('normalenemy', (8, 18))],
        [('healthpotion', (24, 6)),
         ('healthpotion', (8, 18))],
        [('chest', (24, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (8, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (24, 6), True),
         ('turret', (8, 18), True)],
        [('turret', (24, 6), False),
         ('turret', (8, 18), False)],
    ],
    'urL': [
        [],
        [('normalenemy', (8, 6)),
         ('normalenemy', (24, 6)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('keyguard', (24, 6)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('normalenemy', (22, 6)),
         ('normalenemy', (24, 8)),
         ('normalenemy', (24, 18))],
        [('healthpotion', (8, 6)),
         ('healthpotion', (24, 18))],
        [('chest', (8, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (24, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 6), True),
         ('turret', (24, 18), True)],
        [('turret', (8, 6), False),
         ('turret', (24, 18), False)],
    ],
    'dlL': [
        [],
        [('normalenemy', (8, 6)),
         ('normalenemy', (8, 18)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('keyguard', (8, 18)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('normalenemy', (8, 16)),
         ('normalenemy', (10, 18)),
         ('normalenemy', (24, 18))],
        [('healthpotion', (8, 6)),
         ('healthpotion', (24, 18))],
        [('chest', (8, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (24, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 6), True),
         ('turret', (24, 18), True)],
        [('turret', (8, 6), False),
         ('turret', (24, 18), False)],
    ],
    'drL': [
        [],
        [('normalenemy', (8, 18)),
         ('normalenemy', (24, 18)),
         ('normalenemy', (24, 6))],
        [('normalenemy', (8, 18)),
         ('keyguard', (24, 18)),
         ('normalenemy', (24, 6))],
        [('normalenemy', (8, 18)),
         ('normalenemy', (22, 18)),
         ('normalenemy', (24, 16)),
         ('normalenemy', (24, 6))],
        [('healthpotion', (8, 18)),
         ('healthpotion', (24, 6))],
        [('chest', (8, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (24, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 18), True),
         ('turret', (24, 6), True)],
        [('turret', (8, 18), False),
         ('turret', (24, 6), False)],
    ],
    '4': [
        [],
        [('normalenemy', (8, 6)),
         ('normalenemy', (24, 6)),
         ('normalenemy', (8, 18)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('keyguard', (24, 6)),
         ('normalenemy', (8, 18)),
         ('normalenemy', (24, 18))],
        [('keyguard', (8, 6)),
         ('normalenemy', (24, 6)),
         ('normalenemy', (8, 18)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('normalenemy', (24, 6)),
         ('keyguard', (8, 18)),
         ('normalenemy', (24, 18))],
        [('normalenemy', (8, 6)),
         ('normalenemy', (24, 6)),
         ('normalenemy', (8, 18)),
         ('keyguard', (24, 18))],
        [('healthpotion', (8, 6)),
         ('healthpotion', (24, 18))],
        [('healthpotion', (24, 6)),
         ('healthpotion', (8, 18))],
        [('chest', (8, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (24, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('chest', (24, 6), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]]),
         ('chest', (8, 18), [[HealthPotion], [HealthPotion, (ScorePoint, None), (ScorePoint, None)]])],
        [('turret', (8, 6), True),
         ('turret', (24, 18), True)],
        [('turret', (24, 6), False),
         ('turret', (8, 18), False)],
    ]
}

content_weights = {
    '1': [2, 0.5, 1, 1, 0.5, 0.5, 0.5, 1],
    '2': [2, 1, 1, 0.5, 0.5, 1, 0.5, 0.5],
    'L': [2, 1, 1, 0.5, 0.5, 1, 0.5, 0.5],
    '4': [2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 0.5, 0.5]
}

def make_layout_1(cell, pos, layout, cm):
    cell.tiles.add(Wall(cell.pos, cm))
    cell.tiles.add(Wall(cell.pos + (CELL_WIDTH - 50, 0), cm))
    cell.tiles.add(Wall(cell.pos + (0, CELL_HEIGHT - 50), cm))
    cell.tiles.add(Wall(cell.pos + (CELL_WIDTH - 50, CELL_HEIGHT - 50), cm))
    directions = {
        'u': pygame.Vector2(0, -1),
        'd': pygame.Vector2(0, 1),
        'l': pygame.Vector2(-1, 0),
        'r': pygame.Vector2(1, 0)
    }
    for side in 'udlr':
        match layout[side]:
            case 'M':
                continue
            case 'W':
                for i in range(1, lengths[side]):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1], cm))
            case 'T':
                for i in range(1, lengths[side] // 2 - 2):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1], cm))
                tunnel = cell.neighbor_cells[side][0]
                for i in range(0, 4):
                    cell.tiles.add(TunnelEntry(tunnel.poses[side][i], tunnel, directions[side], cm))
                for i in range(lengths[side] // 2 + 2, lengths[side] - 1):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1], cm))
            case _:
                assert(0)