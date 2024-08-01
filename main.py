import pygame
from utils import *
from cell import *
from tunnel import *
from grid import *
from player import *

pygame.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.match_font('consolas'), 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

grid.randomize()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if exited:
            continue
        if event.type == pygame.MOUSEBUTTONUP:
            mouse = pygame.mouse.get_pos()
            player.move(mouse)
    if player.score >= 100 and not exitable:
        grid.set_exit(player)
        exitable = True
    screen.fill("black")
    pygame.draw.rect(screen, "white", pygame.Rect(525, 25, 750, 550))
    for cell in all_small_cells:
        cell.render(screen)
    for cell in all_large_cells:
        cell.render(screen)
    for tunnel in all_tunnels:
        tunnel.render(screen)
    score_text_surface = font.render(f'Score:{player.score}', True, "white")
    moves_text_surface = font.render(f'Moves:{player.moves}', True, "white")
    screen.blit(score_text_surface, (0, grid.h*100-10))
    screen.blit(moves_text_surface, (SIZE * 100-moves_text_surface.get_width(), grid.h*100-10))
    if exited:
        exit_text_surface = font.render('Exited', True, "lime")
        screen.blit(exit_text_surface, (275, grid.h*100-10))
    elif exitable:
        exitable_text_surface = font.render('Exitable', True, "red")
        screen.blit(exitable_text_surface, (245, grid.h*100-10))
    pygame.display.flip()
    clock.tick(60)