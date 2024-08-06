import pygame
import random
from utils import *
from cell import *
from grid import *
from unit import *
from camera import *
from update import *

pygame.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.match_font('consolas'), 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

glob_var["grid"] = Grid(MAZE_SIZE, MAZE_SIZE)
current_cells.append(glob_var["grid"].cells[MAZE_SIZE // 2][MAZE_SIZE // 2])
glob_var["player"] = Player(current_cells[0], 7, 100, 10)

for cell in get_all_cells():
    cell.make_layout()

glob_var["scene"] = pygame.Surface([MAZE_SIZE * CELL_WIDTH, MAZE_SIZE * CELL_HEIGHT])
glob_var["camera"] = Camera(glob_var["scene"], current_cells[0].pos)

glob_var["grid"].randomize()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                glob_var["player"].shoot_bullet(event.pos)
    if glob_var["player"].score >= 50 and not glob_var["exitable"]:
        glob_var["grid"].set_exit()
        glob_var["exitable"] = True
    screen.fill("black")
    glob_var["grid"].render_minimap(screen)
    update()
    glob_var["camera"].follow(glob_var["player"].rect.center)
    glob_var["scene"].fill("black")
    for cell in current_cells:
        cell.render_layout(glob_var["scene"])
        cell.render_content(glob_var["scene"])
    for projectile in Projectile.all_projectiles:
        projectile.render(glob_var["scene"])
    glob_var["player"].render(glob_var["scene"])
    screen.blit(glob_var["scene"], (MAZE_SIZE * TILE_WIDTH, 0), glob_var["camera"].rect)
    score_text_surface = font.render(f'Score:{glob_var["player"].score}', True, "white")
    moves_text_surface = font.render(f'Moves:{glob_var["player"].moves}', True, "white")
    screen.blit(score_text_surface, (0, MAZE_SIZE * TILE_HEIGHT))
    screen.blit(moves_text_surface, (0, MAZE_SIZE * TILE_HEIGHT+score_text_surface.get_height()))
    if glob_var["exited"]:
        exit_text_surface = font.render('Exited', True, "lime")
        screen.blit(exit_text_surface, (0, MAZE_SIZE * TILE_HEIGHT+score_text_surface.get_height()+moves_text_surface.get_height()))
    elif glob_var["exitable"]:
        exitable_text_surface = font.render('Exitable', True, "red")
        screen.blit(exitable_text_surface, (0, MAZE_SIZE * TILE_HEIGHT+score_text_surface.get_height()+moves_text_surface.get_height()))
    pygame.display.flip()
    clock.tick(60)