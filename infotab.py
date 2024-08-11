import pygame
from utils import *

class Infotab(pygame.sprite.Sprite):
    def __init__(self, font, player):
        super().__init__()
        self.surface = pygame.Surface([MAZE_SIZE * TILE_WIDTH, HEIGHT - MAZE_SIZE * TILE_HEIGHT])
        self.surface.set_colorkey("black")
        self.surface.fill("black")
        self.font = font
        self.player = player
        self.rect = pygame.Rect((0, MAZE_SIZE * TILE_HEIGHT), [MAZE_SIZE * TILE_WIDTH, HEIGHT - MAZE_SIZE * TILE_HEIGHT])
    def render(self, surface):
        self.surface.fill("black")
        texts = []
        texts.append(self.font.render(f'Score:{self.player.score}', True, "white"))
        texts.append(self.font.render(f'Moves:{self.player.moves}', True, "white"))
        if glob_var["dead"]:
            texts.append(self.font.render(f'Dead', True, "red"))
        elif glob_var["time_up"]:
            texts.append(self.font.render(f'Time up', True, "red"))
        elif glob_var["exited"]:
            texts.append(self.font.render(f'Exited', True, "green"))
        elif glob_var["exitable"]:
            texts.append(self.font.render(f'Exit appeared', True, "red"))
        else:
            texts.append(self.font.render(f'Batteries:{self.player.batteries}/10', True, "blue"))
        texts.append(self.font.render(f'Health:{self.player.health}/{self.player.max_health}', True, "white"))
        texts.append(self.font.render(f'Current Item:', True, "white"))
        texts.append(self.font.render(f'{self.player.items[self.player.curr_item_idx][0]} x {self.player.items[self.player.curr_item_idx][1]}', True, "white"))
        if glob_var["exitable"]:
            remaining_seconds = glob_var["timelimit_2"] - (glob_var["timer"] - glob_var["timer_start"]) // 1000
        else:
            remaining_seconds = glob_var["timelimit_1"] - (glob_var["timer"] - glob_var["timer_start"]) // 1000
        if remaining_seconds < 60:
            color = "red"
        else:
            color = "white"
        texts.append(self.font.render(f'Remaining time: {remaining_seconds // 60}:{remaining_seconds % 60}', True, color))
        if glob_var["paused"]:
            texts.append(self.font.render('Paused', True, "white"))
        h_total = 5
        for text in texts:
            self.surface.blit(text, (0, h_total))
            h_total += text.get_height() + 5
        surface.blit(self.surface, self.rect)