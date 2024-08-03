from cell import *
from tile import *

def make_layout_1(cell, layout):
    cell.tiles.add(Wall(cell.pos))
    cell.tiles.add(Wall(cell.pos + (CELL_WIDTH - 50, 0)))
    cell.tiles.add(Wall(cell.pos + (0, CELL_HEIGHT - 50)))
    cell.tiles.add(Wall(cell.pos + (CELL_WIDTH - 50, CELL_HEIGHT - 50)))
    for side in 'udlr':
        match layout[side]:
            case 'M':
                continue
            case 'W':
                for i in range(1, lengths[side]):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1]))
            case 'T':
                for i in range(1, lengths[side] // 2 - 2):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1]))
                for i in range(lengths[side] // 2 + 2, lengths[side] - 1):
                    cell.tiles.add(Wall(cell.pos + i * deltas[side][0] + deltas[side][1]))
            case _:
                assert(0)
