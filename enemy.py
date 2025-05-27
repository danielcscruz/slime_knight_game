from pgzero.actor import Actor
from pgzero.builtins import Rect
from grid import arena1

class Enemy:
    def __init__(self, x, y):
        self.actor = Actor('s_idle_1', pos=(x, y))
        self.speed = 1
        self.gravity = 3 
        self.frame = 0
        self.frame_counter = 0
        self.animation_speed = 20
        self.direction = 1  
        
        # Animações
        self.idle_frames = ['s_idle_1', 's_idle_2', 's_idle_3', 's_idle_4']
        self.idle_frames_flip = ['s_idle_1_flip', 's_idle_2_flip', 's_idle_3_flip', 's_idle_4_flip']
        
    def check_collision(self, dx=0, dy=0):
        hitbox_size = 12  
        future_x = self.actor.centerx + dx
        future_y = self.actor.centery + dy
        
        future_rect = Rect(
            future_x - hitbox_size//2, 
            future_y - hitbox_size, 
            hitbox_size, 
            hitbox_size
        )

        for r, row in enumerate(arena1):
            for c, char in enumerate(row):
                if char == "W" or char == "X":
                    tile_rect = Rect(c * 16, r * 16, 16, 16)
                    if future_rect.colliderect(tile_rect):
                        return True
        
        if future_x - hitbox_size//2 < 0 or future_x + hitbox_size//2 > 880:
            return True
        if future_y - hitbox_size//2 < 0 or future_y + hitbox_size//2 > 400:
            return True
            
        return False

    def is_on_ground(self):
        hitbox_size = 12
        check_y = self.actor.centery + hitbox_size//2 + 2
        check_x = self.actor.centerx
        
        col = int(check_x // 16)
        row = int(check_y // 16)

        if row >= len(arena1) or col >= len(arena1[0]) or col < 0 or row < 0:
            return False

        return arena1[row][col] == "W" or arena1[row][col] == "X"

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % len(self.idle_frames)
        
        if self.direction == 1:
            self.actor.image = self.idle_frames[self.frame]
        else:
            self.actor.image = self.idle_frames_flip[self.frame]

        if not self.is_on_ground():
            if not self.check_collision(dy=self.gravity):
                self.actor.y += self.gravity
            return

        move_x = self.speed * self.direction
        
        if self.check_collision(dx=move_x):
            self.direction *= -1
        else:
            future_ground_check_x = self.actor.centerx + move_x
            future_ground_check_y = self.actor.centery + 20
            
            col = int(future_ground_check_x // 16)
            row = int(future_ground_check_y // 16)
            
            if (row >= len(arena1) or col >= len(arena1[0]) or col < 0 or row < 0 or 
                (arena1[row][col] != "W" and arena1[row][col] != "X")):
                self.direction *= -1
            else:
                self.actor.x += move_x

    def draw(self):
        self.actor.draw()
        