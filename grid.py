from cell import *
from tunnel import *

class Grid(Object):
    def __init__(self, w, h):
        super().__init__()
        self.surface = pygame.Surface([50 * w, 50 * h])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.w = w
        self.h = h
        self.cells = [[SmallCell(i, j, (j*50, i*50)) for j in range(w)] for i in range(h)]
        self.tunnels = {
            'h': [[Tunnel('h', i, j, (25+j*50, i*50)) for j in range(w - 1)] for i in range(h)],
            'v': [[Tunnel('v', i, j, (j*50, 25+i*50)) for j in range(w)] for i in range(h - 1)]
        }
        for i, tunnels_row in enumerate(self.tunnels['h']):
            for j, tunnel in enumerate(tunnels_row):
                tunnel.link(self.cells[i][j], self.cells[i][j + 1])
        for i, tunnels_row in enumerate(self.tunnels['v']):
            for j, tunnel in enumerate(tunnels_row):
                tunnel.link(self.cells[i][j], self.cells[i + 1][j])
    def randomize(self):
        ## remerge cells ##
        for large_cell in all_large_cells.copy():
            if not large_cell.locked:
                large_cell.unmerge()
        for _ in range(random.randint(0, 4)):
            match random.choice(['2', 'L', '4']):
                case '2':
                    if random.randint(0, 1):
                        tunnel = random.choice(sum(self.tunnels['h'], []))
                    else:
                        tunnel = random.choice(sum(self.tunnels['v'], []))
                    cell1, cell2 = tunnel.relation
                    if cell1.is_mergable() and cell2.is_mergable():
                        BlockTwoCell(tunnel)
                case 'L':
                    row, col = random.randint(0, self.h-2), random.randint(0, self.w-2)
                    ul_mergable = self.cells[row][col].is_mergable()
                    ur_mergable = self.cells[row][col+1].is_mergable()
                    dl_mergable = self.cells[row+1][col].is_mergable()
                    dr_mergable = self.cells[row+1][col+1].is_mergable()
                    u_mergable = ul_mergable and ur_mergable
                    d_mergable = dl_mergable and dr_mergable
                    l_mergable = ul_mergable and dl_mergable
                    r_mergable = ur_mergable and dr_mergable
                    htunnels =  [('u', self.tunnels['h'][row][col])] if u_mergable else [] + \
                                [('d', self.tunnels['h'][row+1][col])] if d_mergable else []
                    vtunnels =  [('l', self.tunnels['v'][row][col])] if l_mergable else [] + \
                                [('r', self.tunnels['v'][row][col+1])] if r_mergable else []
                    if len(htunnels) == 0 or len(vtunnels) == 0:
                        break
                    if len(htunnels) == 1:
                        LCell(htunnels[0][0] + vtunnels[0][0] + 'L', htunnels[0][1], vtunnels[0][1])
                        break
                    i, j = random.randint(0, 1), random.randint(0, 1)
                    LCell(htunnels[i][0] + vtunnels[j][0] + 'L', htunnels[i][1], vtunnels[j][1])
                case '4':
                    row, col = random.randint(0, self.h-2), random.randint(0, self.w-2)
                    if  self.cells[row][col].is_mergable() and \
                        self.cells[row+1][col].is_mergable() and \
                        self.cells[row][col+1].is_mergable() and \
                        self.cells[row+1][col+1].is_mergable():
                        BlockFourCell(self.tunnels['h'][row][col], self.tunnels['h'][row+1][col], \
                                      self.tunnels['v'][row][col], self.tunnels['v'][row][col+1])
        ## remerge ends ##
        ## random first search ##
        all_cells = get_all_cells()
        visited = []
        queue = [(None, random.choice(all_cells))]
        while len(queue) > 0:
            prev_tunnel, cell = random.choice(queue)
            queue = [item for item in queue if item != (prev_tunnel, cell)]
            if cell in visited :
                prob = 15 if not glob_var["exitable"] else 5
                if random.randint(1, 100) <= prob:
                    prev_tunnel.set_state(True)
                else:
                    prev_tunnel.set_state(False)
            else:
                if prev_tunnel is not None:
                    prev_tunnel.set_state(True)
                visited.append(cell)
                neighbors = [(tunnel, next_cell) for tunnel, next_cell in cell.get_neighbors() if tunnel != prev_tunnel]
                queue += neighbors
        ## random first search ends ##
        ## randomize type for each cell ##
        for cell in all_cells:
            cell.randomize()
        ## randomize type for each cell ends ##
    def set_exit(self):
        all_cells = get_all_cells()
        for cell in all_cells:
            cell.set_type('n')
        candidates = []
        for cell in all_cells:
            if abs(cell.row - glob_var["player"].current_cell.row) + abs(cell.col - glob_var["player"].current_cell.col) <= SIZE / 2 or cell.locked:
                continue
            candidates.append(cell)
        exit_cell = random.choice(candidates)
        exit_cell.set_type('e')
        exit_cell.lock()
        glob_var["player"].safe_moves = 2
    def render_minimap(self, surface):
        for cell in get_all_cells():
            match cell.type:
                case 'n':
                    color = "white"
                case 's1':
                    color = "cyan"
                case 's2':
                    color = "yellow"
                case 's-1':
                    color = "purple"
                case 'e':
                    color = "lime"
            if cell.has_player:
                pygame.draw.polygon(cell.surface, "red", cell.outerline)
            else:
                pygame.draw.polygon(cell.surface, "black", cell.outerline)
            pygame.draw.polygon(cell.surface, color, cell.innerline)
            surface.blit(cell.surface, cell.pos)
        for tunnel in all_tunnels:
            if not tunnel.opened or tunnel.merge is not None:
                continue
            pygame.draw.polygon(tunnel.surface, "white", tunnel.outerline)
            surface.blit(tunnel.surface, tunnel.pos)

glob_var["grid"] = Grid(SIZE, SIZE)