from cell import *
from tile import *

def make_layout_1(cell, layout, cm):
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
