import pygame
from maze_global import *
from cell import *
from tunnel import *
from grid import *
from player import *

pygame.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.match_font('consolas'), 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

glob_var["grid"].randomize()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if not glob_var["exited"] and event.type == pygame.MOUSEBUTTONUP:
            mouse = pygame.mouse.get_pos()
            glob_var["player"].move(mouse)
    if glob_var["player"].score >= 1 and not glob_var["exitable"]:
        glob_var["grid"].set_exit()
        glob_var["exitable"] = True
    screen.fill("black")
    pygame.draw.rect(screen, "white", pygame.Rect(500, 0, 800, HEIGHT))
    glob_var["grid"].render_minimap(screen)
    score_text_surface = font.render(f'Score:{glob_var["player"].score}', True, "white")
    moves_text_surface = font.render(f'Moves:{glob_var["player"].moves}', True, "white")
    screen.blit(score_text_surface, (0, glob_var["grid"].h*100-10))
    screen.blit(moves_text_surface, (SIZE*100-moves_text_surface.get_width(), glob_var["grid"].h*100-10))
    if glob_var["exited"]:
        exit_text_surface = font.render('Exited', True, "lime")
        screen.blit(exit_text_surface, (275, glob_var["grid"].h*100-10))
    elif glob_var["exitable"]:
        exitable_text_surface = font.render('Exitable', True, "red")
        screen.blit(exitable_text_surface, (245, glob_var["grid"].h*100-10))
    pygame.display.flip()
    clock.tick(60)