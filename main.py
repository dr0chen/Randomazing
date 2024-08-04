import pygame
from utils import *
from cell import *
from tunnel import *
from grid import *
from player import *
from camera import *
from tile import *
from layout import *

pygame.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.match_font('consolas'), 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()


glob_var["grid"] = Grid(MAZE_SIZE, MAZE_SIZE)
current_cells.append(glob_var["grid"].cells[MAZE_SIZE // 2][MAZE_SIZE // 2])
glob_var["player"] = Player(10)

for cell in get_all_cells():
    cell.make_layout()

scene = pygame.Surface([MAZE_SIZE * CELL_WIDTH, MAZE_SIZE * CELL_HEIGHT])
glob_var["camera"] = Camera(scene, current_cells[0].pos)

glob_var["grid"].randomize()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
    if glob_var["player"].score >= 1 and not glob_var["exitable"]:
        glob_var["grid"].set_exit()
        glob_var["exitable"] = True
    screen.fill("black")
    glob_var["grid"].render_minimap(screen)
    player_move(glob_var["player"], glob_var["player"].location.cm)
    glob_var["camera"].follow(glob_var["player"].rect.center)
    scene.fill("brown")
    for cell in current_cells:
        cell.render_layout(scene)
    scene.blit(glob_var["player"].surface, glob_var["player"].rect)
    screen.blit(scene, (MAZE_SIZE * TILE_WIDTH, 0), glob_var["camera"].rect)
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