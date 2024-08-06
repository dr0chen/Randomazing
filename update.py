import pygame
import random
from utils import *
from cell import *
from grid import *
from unit import *
from camera import *
from infotab import *

def init():
    pygame.init()
    pygame.font.init()

    glob_var["font"] = pygame.font.Font(pygame.font.match_font('consolas'), 20)
    glob_var["screen"] = pygame.display.set_mode((WIDTH, HEIGHT))
    glob_var["clock"] = pygame.time.Clock()
    glob_var["timer"] = pygame.time.get_ticks()

    glob_var["grid"] = Grid(MAZE_SIZE, MAZE_SIZE)
    current_cells.append(glob_var["grid"].cells[MAZE_SIZE // 2][MAZE_SIZE // 2])
    glob_var["player"] = Player(current_cells[0], 7, 100, 10)
    glob_var["infotab"] = Infotab(glob_var["font"], glob_var["player"])

    for cell in get_all_cells():
        cell.make_layout()

    glob_var["scene"] = pygame.Surface([MAZE_SIZE * CELL_WIDTH, MAZE_SIZE * CELL_HEIGHT])
    glob_var["camera"] = Camera(glob_var["scene"], current_cells[0].pos)

    glob_var["grid"].randomize()

def poll_event():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if glob_var["dead"] or glob_var["time_up"] or glob_var["exited"]:
            continue
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                glob_var["player"].use_item(event.pos)
            elif event.button == pygame.BUTTON_RIGHT:
                glob_var["player"].switch_item()

def update():
    player = glob_var["player"]
    grid = glob_var["grid"]
    camera = glob_var["camera"]
    grid = glob_var["grid"]

    #global status check
    if glob_var["timer"] // 1000 >= glob_var["timelimit_1"] and not glob_var["exitable"]:
        glob_var["time_up"] = True
    elif glob_var["timer"] // 1000 >= glob_var["timelimit_2"] and glob_var["exitable"]:
        glob_var["time_up"] = True
    
    if glob_var["dead"] or glob_var["time_up"] or glob_var["exited"]:
        return
    if player.batteries >= 10 and not glob_var["exitable"]:
        grid.set_exit()
        glob_var["exitable"] = True

    #if enemies in cell, close down
    if len(current_cells[0].enemies) > 0:
        current_cells[0].close_down()
    #else, open up
    else:
        current_cells[0].open_up()
    
    #units action
    for enemy in current_cells[0].enemies:
        enemy.action()
    player.action()
    
    #item friction
    for item in DroppedItems.all_items:
        item.acc = pygame.Vector2(0, 0)
        if item.vel != pygame.Vector2(0, 0):
            item.acc -= item.vel.normalize() * 0.8
        vel_tmp = item.vel + item.acc
        if item.vel.x * vel_tmp.x < 0:
            item.vel.x = 0
        else:
            item.vel.x = vel_tmp.x
        if item.vel.y * vel_tmp.y < 0:
            item.vel.y = 0
        else:
            item.vel.y = vel_tmp.y
    
    #don't handle collisions when in tunnel
    if isinstance(player.location, Cell):
        cm = player.location.cm

        #first move along x
        #player
        vel_tmp = player.vel.copy()
        player.rect.left += player.vel.x
        player.vel.y = 0
        #enemies
        for enemy in current_cells[0].enemies:
            enemy.vel_tmp = enemy.vel.copy()
            enemy.rect.left += enemy.vel.x
            enemy.vel.y = 0
        #projectiles
        for projectile in Projectile.all_projectiles:
            projectile.rect.left += projectile.vel.x
        #items
        for item in DroppedItems.all_items:
            item.vel_tmp = item.vel.copy()
            item.rect.left += item.vel.x
            item.vel.y = 0
        #first collision check
        cm.check_collisions()
        #vel recover
        player.vel.y = vel_tmp.y
        for enemy in current_cells[0].enemies:
            enemy.vel.y = enemy.vel_tmp.y
        for item in DroppedItems.all_items:
            item.vel.y = item.vel_tmp.y

        #then move along y
        #player
        player.rect.top += player.vel.y
        player.vel.x = 0
        #enemies
        for enemy in current_cells[0].enemies:
            enemy.rect.top += enemy.vel.y
            enemy.vel.x = 0
        #projectiles
        for projectile in Projectile.all_projectiles:
            projectile.rect.top += projectile.vel.y
        #items
        for item in DroppedItems.all_items:
            item.rect.top += item.vel.y
            item.vel.x = 0
        #second collision check
        cm.check_collisions()
        #vel recover
        player.vel.x = vel_tmp.x
        for enemy in current_cells[0].enemies:
            enemy.vel.x = enemy.vel_tmp.x
        for item in DroppedItems.all_items:
            item.vel.x = item.vel_tmp.x
    
    #don't handle collisions when in tunnel
    else:
        player.rect.center += player.vel
        for projectile in Projectile.all_projectiles:
            projectile.rect.center += projectile.vel
        for item in DroppedItems.all_items:
            item.rect.center += item.vel

    #player moving_state recover from transition
    if current_cells[-1].is_including(player.rect):
        player.moving_state = 'free'
    #current_cells update
    if player.moving_state == 'free' and len(current_cells) > 1:
        current_cells.pop(0)
    
    #camera movement
    camera.follow(player.rect.center)

    #timer update
    glob_var["timer"] = pygame.time.get_ticks()

def render():
    screen = glob_var["screen"]
    grid = glob_var["grid"]
    scene = glob_var["scene"]
    player = glob_var["player"]
    camera = glob_var["camera"]
    infotab = glob_var["infotab"]

    #objects rendering
    screen.fill("black")
    scene.fill("black")
    grid.render_minimap(screen)
    for cell in current_cells:
        cell.render_layout(scene)
        cell.render_content(scene)
    for projectile in Projectile.all_projectiles:
        projectile.render(scene)
    player.render(scene)
    screen.blit(scene, (MAZE_SIZE * TILE_WIDTH, 0), glob_var["camera"].rect)
    infotab.render(screen)

    #flip!
    pygame.display.flip()