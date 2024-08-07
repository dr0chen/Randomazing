from cell import *
from tunnel import *
from time import sleep

class Grid(Object):
    def __init__(self, w, h):
        super().__init__()
        self.minisurface = pygame.Surface([50 * w, 50 * h])
        # self.minisurface.set_colorkey("black")
        self.minisurface.fill("black")
        self.pos = pygame.Vector2(0, 0)
        self.w = w
        self.h = h
        self.should_randomize = False
        self.cells = [[SmallCell(i, j) for j in range(w)] for i in range(h)]
        self.tunnels = {
            'h': [[Tunnel('h', i, j, self.cells[i][j], self.cells[i][j+1]) for j in range(w - 1)] for i in range(h)],
            'v': [[Tunnel('v', i, j, self.cells[i][j], self.cells[i+1][j]) for j in range(w)] for i in range(h - 1)]
        }
        self.battery_cell = None
        self.shooter_cell = None
    def randomize(self):
        ## clear dynamic objects##
        for cell in get_all_cells():
            if not cell.locked:
                cell.clear_content()
        ## clear dynamic objects end##
        ## unmerge cells ##
        for large_cell in LargeCell.all_large_cells.copy():
            if not large_cell.locked:
                large_cell.unmerge()
        ## unmerge cells end ##
        ## reset all tunnels ##
        for tunnel in Tunnel.all_tunnels:
            tunnel.set_state(False)
        if self.battery_cell:
            self.battery_cell.unset_breakable()
        if self.shooter_cell:
            self.shooter_cell.unset_breakable()
        ## reset all tunnels end ##
        ## choose and protect battery cell ##
        if not glob_var["exitable"]:
            self.battery_cell = random.choice([cell for cell in SmallCell.all_small_cells if not cell.locked])
            self.battery_cell.lock()
            self.battery_cell.lock_tunnels()
        else:
            self.battery_cell = None
        ## choose and protect battery cell end ##
        ## choose and protect shooter cell ##
        if not glob_var["has_shooter"]:
            self.shooter_cell = random.choice([cell for cell in SmallCell.all_small_cells if not cell.locked and cell is not self.battery_cell])
            self.shooter_cell.lock()
            self.shooter_cell.lock_tunnels()
        else:
            self.shooter_cell = None
        ## choose and protect shooter cell end ##
        for _ in range(random.randint(0, 4)):
            candidates = []
            match random.choice(['h2', 'v2', 'ulL', 'urL', 'dlL', 'drL', '4']):
                case 'h2':
                    for row in range(self.h):
                        for col in range(self.w-1):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row][col+1].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    BlockTwoCell(self.tunnels['h'][row][col])
                case 'v2':
                    for row in range(self.h-1):
                        for col in range(self.w):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row+1][col].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    BlockTwoCell(self.tunnels['v'][row][col])
                case 'ulL':
                    for row in range(self.h-1):
                        for col in range(self.w-1):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row][col+1].is_mergable() \
                            and self.cells[row+1][col].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    LCell('ulL', self.tunnels['h'][row][col], self.tunnels['v'][row][col])
                case 'urL':
                    for row in range(self.h-1):
                        for col in range(self.w-1):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row][col+1].is_mergable() \
                            and self.cells[row+1][col+1].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    LCell('urL', self.tunnels['h'][row][col], self.tunnels['v'][row][col+1])
                case 'dlL':
                    for row in range(self.h-1):
                        for col in range(self.w-1):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row+1][col].is_mergable() \
                            and self.cells[row+1][col+1].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    LCell('dlL', self.tunnels['h'][row+1][col], self.tunnels['v'][row][col])
                case 'drL':
                    for row in range(self.h-1):
                        for col in range(self.w-1):
                            if  self.cells[row][col+1].is_mergable() \
                            and self.cells[row+1][col].is_mergable() \
                            and self.cells[row+1][col+1].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    LCell('drL', self.tunnels['h'][row+1][col], self.tunnels['v'][row][col+1])
                case '4':
                    for row in range(self.h-1):
                        for col in range(self.w-1):
                            if  self.cells[row][col].is_mergable() \
                            and self.cells[row][col+1].is_mergable() \
                            and self.cells[row+1][col].is_mergable() \
                            and self.cells[row+1][col+1].is_mergable():
                                candidates.append((row, col))
                    row, col = random.choice(candidates)
                    BlockFourCell(self.tunnels['h'][row][col], self.tunnels['h'][row+1][col],
                                  self.tunnels['v'][row][col], self.tunnels['v'][row][col+1])
        ## remerge ends ##
        all_cells = [cell for cell in get_all_cells() if cell is not self.battery_cell and cell is not self.shooter_cell]
        ## wilson's algorithm ##
        visited = [random.choice(all_cells)]
        unvisited = [cell for cell in all_cells if cell not in visited]
        assert(len(visited) + len(unvisited) == len(all_cells))
        curr = random.choice(unvisited)
        path = [curr]
        tunnel_path = []
        while True:
            assert(len(visited) + len(unvisited) == len(all_cells))
            candidates = [(tunnel, neighbor) for tunnel, neighbor in curr.get_neighbors() if neighbor is not self.battery_cell and neighbor is not self.shooter_cell]
            tunnel, next_cell = random.choice(candidates)
            if next_cell not in visited:
                if next_cell in path:
                    idx = path.index(next_cell)
                    path = path[0:idx + 1]
                    tunnel_path = tunnel_path[:idx]
                else:
                    path.append(next_cell)
                    tunnel_path.append(tunnel)
            else:
                tunnel_path.append(tunnel)
                for cell in path:
                    visited.append(cell)
                    if cell not in unvisited:
                        print(cell.row, cell.col)
                    unvisited.remove(cell)
                for tunnel in tunnel_path:
                    tunnel.set_state(True)
                if len(unvisited) == 0:
                    break
                next_cell = random.choice(unvisited)
                path = [next_cell]
                tunnel_path = []
            curr = next_cell
        ## wilson's algorithm ends ##
        for tunnel in Tunnel.all_tunnels:
            if random.randint(1, 100) <= 20:
                tunnel.set_state(True)
        ## randomize content for each cell ##
        for cell in all_cells:
            cell.randomize()
            cell.make_content()
        ## randomize content for each cell ends ##
        ## set battery cell ##
        if self.battery_cell:
            self.battery_cell.unlock()
            self.battery_cell.unlock_tunnels()
            self.battery_cell.set_breakable()
        ## set battery cell end ##
        ## set shooter cell ##
        if self.shooter_cell:
            self.shooter_cell.unlock()
            self.shooter_cell.unlock_tunnels()
            self.shooter_cell.set_breakable()
        ## set shooter cell end ##
        self.should_randomize = False
    def set_exit(self):
        all_cells = get_all_cells()
        for cell in all_cells:
            cell.set_content([])
        candidates = []
        for cell in all_cells:
            if abs(cell.row - current_cells[0].row) + abs(cell.col - current_cells[0].col) <= MAZE_SIZE / 2 or cell.locked:
                continue
            candidates.append(cell)
        exit_cell = random.choice(candidates)
        exit_cell.set_content([])
        exit_cell.lock()
        glob_var["player"].safe_moves = 2
    def render_minimap(self, surface):
        color = "black"
        all_cells = get_all_cells()
        for cell in all_cells:
            # match cell.type:
            #     case 'n':
            #         color = "black"
            #     case 's1':
            #         color = "cyan"
            #     case 's2':
            #         color = "yellow"
            #     case 's-1':
            #         color = "purple"
            #     case 'e':
            #         color = "lime"
            if cell.has_player:
                pygame.draw.polygon(cell.minisurface, "red", cell.outerline)
            else:
                pygame.draw.polygon(cell.minisurface, "white", cell.outerline)
            pygame.draw.polygon(cell.minisurface, color, cell.innerline)
            self.minisurface.blit(cell.minisurface, cell.minipos)
        for tunnel in Tunnel.all_tunnels:
            if not tunnel.opened or tunnel.merge:
                continue
            tunnel.minisurface.fill("black")
            pygame.draw.polygon(tunnel.minisurface, "black", tunnel.outerline)
            self.minisurface.blit(tunnel.minisurface, tunnel.minipos)
            surface.blit(self.minisurface, self.pos)