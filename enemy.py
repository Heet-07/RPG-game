import pygame
from settings import *

# Load Orc animations
animation_orc = {
    "idle": pygame.image.load("Photo/Orc/Orc_Idle.png"),
    "walk": pygame.image.load("Photo/Orc/Orc_Walk.png"),
    "hit": pygame.image.load("Photo/Orc/Orc_Hit.png"),
    "death": pygame.image.load("Photo/Orc/Orc_Death.png"),
    "attack": pygame.image.load("Photo/Orc/Orc_Attack02.png")
}

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, attack_damage, speed, scale, target):
        super().__init__()
        self.animations = animation_orc
        self.frame_width, self.frame_height = 100, 100
        self.state = "idle"
        self.scales = scale
        self.frames = self.load_frames(self.animations[self.state])
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150  # ms per frame 

        self.alive = True
        self.speed = speed
        self.target = target
        self.health = health
        self.attack_damage = attack_damage
        self.attack_range = 70
        self.vision_range = 280
        self.damage_cooldown = 850
        self.last_attack_time = 0
        self.attacking = False
        self.side_left = True

        self.max_health = health
        self.health = health

    # Pre-scale frames when loading to improve performance
    def load_frames(self, sprite_sheet):
        frames = []
        sheet_width = sprite_sheet.get_width()
        num_frames = sheet_width // self.frame_width
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(sprite_sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
            # Scale the frame once
            frame = pygame.transform.scale(frame, (int(self.frame_width * self.scales), int(self.frame_height * self.scales)))
            frames.append(frame)
        return frames

    def set_state(self, new_state):
        if new_state != self.state and new_state in self.animations:
            self.state = new_state
            self.frames = self.load_frames(self.animations[self.state])
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            if self.state == "idle":
                self.last_attack_time = pygame.time.get_ticks()



    def take_damage(self, damage):
        """Reduce health when hit by player"""
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > self.damage_taken_cooldown:
            self.health -= damage
            self.last_damage_time = now
            if self.health <= 0:
                self.health = 0
                self.alive = False
    

    def draw_health_bar(self, screen, camera_x):
        """Draw small health bar above enemy"""
        if not self.alive:
            return
        
        bar_width = 40
        bar_height = 5
        
        # Position above enemy
        x = self.rect.centerx-20
        y = self.rect.centery-33
        
        # Only draw if on screen
        if -bar_width < x < 1024 + bar_width:
            # Background (dark red)
            pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))
            
            # Health (green)
            health_ratio = max(0, self.health / self.max_health)
            pygame.draw.rect(screen, (0, 200, 0), (x, y, bar_width * health_ratio, bar_height))
            
            # Border
            pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 1)


    def update(self):
        now = pygame.time.get_ticks()
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5

        # Flip sprite based on direction
        self.side_left = dx < 0

        # Death check
        if not self.alive:
            self.set_state("death")

        # --- ANIMATION UPDATE FIRST ---
        if now - self.last_update >= self.animation_speed:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "death":
                    self.current_frame = len(self.frames) - 1
                    self.alive = False
                else:
                    self.current_frame = 0

            # Apply flipping
            self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)

        # --- APPLY DAMAGE DURING ATTACK ---
        # if self.attacking and distance<self.attack_range:
        #     if self.rect.colliderect(self.target) :
        #         self.target.take_damage(ENEMY_ATTACK_DAMAGE)
        #         now = pygame.time.get_ticks()
                   
            

        

        # --- ATTACK LOGIC ---
        if self.attacking:
            # Stay in attack animation for 800ms
            if now - self.last_attack_time > 1000:
                self.attacking = False
                self.last_attack_time=now
                self.set_state("idle")
            else :
                if self.rect.colliderect(self.target.rect):
                    attack_hit_delay = 500
                    if now-self.last_attack_time>attack_hit_delay and distance<self.attack_range+5:
                        self.target.take_damage(self.attack_damage)
            return  # don’t move during attack


        # --- DETECT PLAYER ---
        if distance < self.attack_range:
            if now - self.last_attack_time > self.damage_cooldown:
                print("Enemy attacking!")
                self.set_state("attack")
                self.attacking = True
                self.last_attack_time = now       
            else:
                self.set_state("idle")
        elif distance < self.vision_range:
            self.set_state("walk")
            if distance != 0:
                self.rect.x += int(self.speed * dx / distance)
        else:
            self.set_state("idle")
