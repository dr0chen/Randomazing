import pygame
from utils import *
from cell import *
from projectile import *
from droppeditem import *

def update():
    player = glob_var["player"]
    grid = glob_var["grid"]

    #player get acc and calc vel
    player.acc = pygame.Vector2(0, 0)
    max_speed = player.speed
    if player.moving_state == 'free': #if free, read keyboard inputs
        if grid.should_randomize:
            grid.randomize()
        player.location = current_cells[0]
        pressed_keys = pygame.key.get_pressed()
        facing_tmp = [0, 0]
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            player.acc.x -= player.speed / 2
            facing_tmp[0] -= 1
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            player.acc.x += player.speed / 2
            facing_tmp[0] += 1
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            player.acc.y -= player.speed / 2
            facing_tmp[1] -= 1
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            player.acc.y += player.speed / 2
            facing_tmp[1] += 1
        if facing_tmp != [0, 0]:
            player.facing = facing_tmp
        if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            max_speed = 2
            player.shield = True
        else:
            player.shield = False
    elif player.moving_state == 'transition': #if in transition, move in the tunnel direction
        player.acc.x += player.facing[0] * player.speed / 2
        player.acc.y += player.facing[1] * player.speed / 2
    else:
        assert(0)

    #player friction
    if player.vel != pygame.Vector2(0, 0):
        player.acc -= player.vel.normalize()
    vel_tmp = player.vel + player.acc
    if player.vel.x * vel_tmp.x < 0:
        player.vel.x = 0
    else:
        player.vel.x = vel_tmp.x
    if player.vel.y * vel_tmp.y < 0:
        player.vel.y = 0
    else:
        player.vel.y = vel_tmp.y
    #no more than max_speed
    if player.vel.length() > max_speed:
        player.vel = player.vel.normalize() * max_speed
    #item friction
    for item in DroppedItems.all_items:
        item.acc = pygame.Vector2(0, 0)
        if item.vel != pygame.Vector2(0, 0):
            item.acc -= item.vel.normalize()
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
        for item in DroppedItems.all_items:
            item.vel.y = item.vel_tmp.y

        #then move along y
        #player
        player.rect.top += player.vel.y
        player.vel.x = 0
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
        for item in DroppedItems.all_items:
            item.vel.x = item.vel_tmp.x
    
    #don't handle collisions when in tunnel
    else:
        player.rect.center += player.vel
        for projectile in Projectile.all_projectiles:
            projectile.rect.center += projectile.vel
        for item in DroppedItems.all_items:
            item.rect.center += item.vel

    #enemies action
    curr_time = pygame.time.get_ticks()
    for enemy in current_cells[0].enemies:
        if curr_time > enemy.last_shoot_time + enemy.shoot_interval:
            enemy.shoot_bullet(pygame.Vector2(glob_var["player"].rect.center))
            enemy.last_shoot_time = curr_time

    #player moving_state recover from transition
    if current_cells[-1].is_including(player.rect):
        player.moving_state = 'free'
    #current_cells update
    if player.moving_state == 'free' and len(current_cells) > 1:
        current_cells.pop(0)