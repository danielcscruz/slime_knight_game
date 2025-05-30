import random
from pgzero.builtins import Rect
from enemy import Enemy
from grid import arena1

arena = arena1
game_state = 'menu'

# Animações
knight_idle = ['k_idle_1', 'k_idle_2', 'k_idle_3', 'k_idle_4']
knight_roll = [
    'k_roll_1', 'k_roll_2', 'k_roll_3', 'k_roll_4',
    'k_roll_5', 'k_roll_6', 'k_roll_7', 'k_roll_8'
]
knight_hit = [
    'k_hit_1', 'k_hit_2', 'k_hit_3', 'k_hit_4',
    'k_kill_1', 'k_kill_2', 'k_kill_3', 'k_kill_4'
]
knight_idle_flip = ['k_idle_1_flip', 'k_idle_2_flip', 'k_idle_3_flip', 'k_idle_4_flip']
knight_roll_flip = [
    'k_roll_1_flip', 'k_roll_2_flip', 'k_roll_3_flip', 'k_roll_4_flip',
    'k_roll_5_flip', 'k_roll_6_flip', 'k_roll_7_flip', 'k_roll_8_flip'
]
knight_hit_flip = [
    'k_hit_1_flip', 'k_hit_2_flip', 'k_hit_3_flip', 'k_hit_4_flip',
    'k_kill_1_flip', 'k_kill_2_flip', 'k_kill_3_flip', 'k_kill_4_flip'
]

slug_idle = ['s_idle_1', 's_idle_2', 's_idle_3', 's_idle_4']
slug_idle_flip = ['s_idle_1_flip', 's_idle_2_flip', 's_idle_3_flip', 's_idle_4_flip']


# Estado do personagem
knight_pos_arena_x = 0
knight_pos_arena_y = 0
frame_atual = 0
frame_contador = 0
velocidade_idle = 16
frame_roll = 0
hit_roll = 0
is_flipped = False
is_falling = False
is_hit = False
rolling = False

knight = Actor(knight_idle[frame_atual], pos=(440, 150))

roll_distance = 100
roll_direction = 1
roll_step = 5
roll_progress = 0

WIDTH = 880
HEIGHT = 400

enemies = []
spawn_timer = 0
spawn_interval = 120

sound_enabled = True
sound_button_rect = Rect((740, 20), (120, 40))  


# Sistema de pontuação e dificuldade
score = 0
points_per_kill = 10
difficulty_timer = 0
difficulty_increase_interval = 300  


current_music = None

def draw():
    if game_state == 'menu':
        draw_arena()
        screen.draw.text(
            "Clique para começar",
            center=(440, 100),
            fontname="tiny5", 
            fontsize=32, 
            color="white"
        )
        screen.draw.text(
            "Utilize as setas para jogar e espaço para rolar e atacar o inimigo",
            center=(440, 200),
            fontname="tiny5",
            fontsize=15,
            color="white"
        )
        screen.draw.rect(sound_button_rect, "white")
        text = "Som: ON" if sound_enabled else "Som: OFF"
        screen.draw.text(
            text,
            center=sound_button_rect.center,
            fontname="tiny5",
            fontsize=20,
            color="white"
        )

    elif game_state == 'playing':
        draw_game()
    elif game_state == 'game_over':
        draw_arena()
        screen.draw.text(
            "Game Over! Clique para reiniciar.",
            center=(440, 200), fontname="tiny5",
            fontsize=35,
            color="red"
        )
        screen.draw.text(
            f"Score Final: {score}",
            center=(440, 250),
            fontname="tiny5",
            fontsize=25,
            color="white"
        )

def on_mouse_down(pos):
    global game_state, sound_enabled

    if game_state == 'menu':
        if sound_button_rect.collidepoint(pos):
            sound_enabled = not sound_enabled
            if sound_enabled:
                change_music("menu_jingle.wav")
            else:
                music.stop()
        else:
            start_game()
    
    elif game_state == 'game_over':
        go_to_menu()

def draw_game():
    draw_arena()
    knight.draw()
    screen.draw.text(
        f"Score: {score}",
        (WIDTH - 150, 10),
        fontname="tiny5", 
        fontsize=20,
        color="white"
    )
    for enemy in enemies:
        enemy.draw()

def draw_arena():
    screen.fill((138,220,255))
    for r, row in enumerate(arena):
        for c, char in enumerate(row):
            x = c * 16
            y = r * 16
            if char == "W":
                screen.blit("tile", (x, y))
            if char == "X":
                screen.blit("tile3", (x, y))
            if char == "4":
                screen.blit("water0", (x, y))
            if char == "A":
                screen.blit("water1", (x, y))

def draw_game_over():
    screen.draw.text(
        "Fim de Jogo",
        center=(400, 300),
        fontname="tiny5",
        fontsize=80
    )
    screen.draw.text(
        "Pressione ENTER para voltar ao menu",
        center=(400, 400),
        fontname="tiny5",
        fontsize=48
    )

def update():
    global spawn_timer, difficulty_timer, spawn_interval, points_per_kill

    if game_state == 'playing':
        update_game()
        spawn_timer += 1
        difficulty_timer += 1
        
        if difficulty_timer >= difficulty_increase_interval:
            difficulty_timer = 0
            if spawn_interval > 30:
                spawn_interval = max(30, spawn_interval - 10)
            points_per_kill += 5
        
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            spawn_enemy()

        for enemy in enemies:
            enemy.update()

def change_music(new_music):
    global current_music
    if current_music != new_music:
        music.stop()
        if new_music:
            music.play(new_music)
            music.set_volume(0.4)
        current_music = new_music


def on_key_down(key):
    global rolling, frame_roll
    if game_state == 'playing':
        if key == keys.SPACE and not rolling and not is_hit:
            start_roll()
        if key == keys.UP and not rolling and not is_hit:
            jump()

def start_game():
    global game_state
    if sound_enabled:
        sounds.start.play()
        change_music("game_jingle.wav")
    game_state = 'playing'
    reset_game()

def go_to_menu():
    global game_state
    game_state = 'menu'
    change_music("menu_jingle.wav")

def start_roll():
    global rolling, frame_roll
    rolling = True
    frame_roll = 0
    
    distance = -roll_distance if is_flipped else roll_distance
    final_x = knight.x + distance
    
    if check_collision(dx=distance):
        max_distance = 0
        step = 5 if not is_flipped else -5
        test_distance = 0
        
        while abs(test_distance) < abs(distance):
            if check_collision(dx=test_distance + step):
                break
            test_distance += step
            max_distance = test_distance
        
        distance = max_distance
    
    if sound_enabled:
            sounds.roll.play()
    
    if distance != 0:
        animate(knight, pos=(knight.x + distance, knight.y),
                duration=0.5, on_finished=end_roll)
    else:
        end_roll()
        
    clock.schedule_interval(update_roll_frame, 0.05)

def jump():
    if not check_collision(dy=-75) and is_on_ground():
        if sound_enabled:
                sounds.jump.play()
        animate(knight, pos=(knight.x, knight.y - 75), duration=0.3)

def knight_enemy_collision(knight_pos, enemy_pos):
    knight_center_x = knight_pos[0]
    knight_center_y = knight_pos[1]
    enemy_center_x = enemy_pos[0] 
    enemy_center_y = enemy_pos[1]
    
    distance = ((knight_center_x - enemy_center_x) ** 2 +
                (knight_center_y - enemy_center_y) ** 2) ** 0.5
    
    return distance < 20

def update_game():
    global frame_atual, frame_contador, is_flipped, is_falling, enemies, is_hit, score

    for enemy in enemies[:]: 
        enemy.update()
        
        if knight_enemy_collision(knight.center, enemy.actor.center):
            if rolling:
                enemies.remove(enemy) 
                if sound_enabled:
                    sounds.kill.play()  
                score += points_per_kill  
            else:
                if not is_hit: 
                    take_hit()

    frame_contador += 1
    if frame_contador >= velocidade_idle:
        frame_contador = 0
        frame_atual = (frame_atual + 1) % len(knight_idle)

    if not rolling and not is_hit:
        knight.image = knight_idle_flip[frame_atual] if is_flipped else knight_idle[frame_atual]

        if keyboard.left:
            move_knight(-1)
        if keyboard.right:
            move_knight(1)

    if not is_on_ground():
        if not check_collision(dy=2):
            knight.y += 2
            is_falling = True
        else:
            is_falling = False
    else:
        is_falling = False

def take_hit():
    global is_hit, hit_roll
    is_hit = True
    hit_roll = 0

    if sound_enabled:
            sounds.gameover.play()

    clock.schedule_interval(update_hit_frame, 0.15)

def update_roll_frame():
    global frame_roll
    knight.image = knight_roll_flip[frame_roll] if is_flipped else knight_roll[frame_roll]
    frame_roll += 1
    if frame_roll >= len(knight_roll):
        frame_roll = 0

def update_hit_frame():
    global hit_roll, is_hit
    current_frame = knight_hit_flip[hit_roll] if is_flipped else knight_hit[hit_roll]
    knight.image = current_frame
    hit_roll += 1

    if hit_roll >= len(knight_hit):
        clock.unschedule(update_hit_frame)
        game_over()

def end_roll():
    global rolling
    rolling = False
    clock.unschedule(update_roll_frame)

def is_on_ground():
    hitbox_size = 20
    check_y = knight.centery + hitbox_size//2 + 2
    check_x = knight.centerx
    
    col = int(check_x // 16)
    row = int(check_y // 16)
    
    if row >= len(arena) or col >= len(arena[0]) or col < 0 or row < 0:
        return False

    return arena[row][col] == "W" or arena[row][col] == "X"

def move_knight(dx):
    global is_flipped

    speed = 5  

    if not check_collision(dx=dx * speed):
        knight.x += dx * speed

    if dx < 0:
        is_flipped = True
    elif dx > 0:
        is_flipped = False

def check_collision(dx=0, dy=0):
    hitbox_size = 20
    future_x = knight.centerx + dx
    future_y = knight.centery + dy
    
    future_rect = Rect(
        future_x - hitbox_size//2, 
        future_y - hitbox_size//2, 
        hitbox_size, 
        hitbox_size
    )

    for r, row in enumerate(arena):
        for c, char in enumerate(row):
            if char == "W" or char == "X":
                tile_rect = Rect(c * 16, r * 16, 16, 16)
                if future_rect.colliderect(tile_rect):
                    return True
    
    if future_x - hitbox_size//2 < 0 or future_x + hitbox_size//2 > WIDTH:
        return True
    if future_y - hitbox_size//2 < 0 or future_y + hitbox_size//2 > HEIGHT:
        return True
        
    return False

def game_over():
    global game_state
    game_state = 'game_over'
    change_music("menu_jingle.wav")

def spawn_enemy():
    x = random.randint(50, WIDTH - 50)
    y = 50  
    enemy = Enemy(x, y)
    enemies.append(enemy)

def reset_game():
    global enemies, spawn_timer, knight, is_hit, rolling, frame_atual, hit_roll, frame_roll, score
    global difficulty_timer, spawn_interval, points_per_kill
    
    enemies = []
    spawn_timer = 0
    difficulty_timer = 0
    is_hit = False
    rolling = False
    frame_atual = 0
    hit_roll = 0
    frame_roll = 0
    score = 0 
    
    spawn_interval = 120
    points_per_kill = 10
    
    knight.pos = (440, 150)
    knight.image = knight_idle[0]

    clock.unschedule(update_hit_frame)
    clock.unschedule(update_roll_frame)

def on_start():
    change_music("menu_jingle.wav")

on_start()