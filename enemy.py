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
        self.alive = True
        self.health = self.max_health = health
        self.attack_damage = attack_damage
        self.speed = speed
        self.target = target
        self.attack_range = 70
        self.vision_range = 300
        self.damage_cooldown = 800
        self.last_attack_time = 0
        self.attacking = False
        self.side_left = True
        self.alpha = 0

        self.deathTime = 0
        self.deathDelay = 800

        self.last_damage_time=0
        self.damage_taken_cooldown=500

        # Load sounds
        self.death_sound = pygame.mixer.Sound("Audio/orc_death.MP3")  # put your sound file path here
        self.death_sound.set_volume(0.6)  # optional: control volume (0.0 - 1.0)

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
            if self.state == "death":
                self.alive = False


    def take_damage(self, damage):
        """Reduce health when hit by player"""
        now = pygame.time.get_ticks()
        # if now - self.last_damage_time > self.damage_taken_cooldown:
        self.set_state("hit")
        self.health -= damage
        self.last_damage_time = now
        if self.health <= 0:
            self.health = 0
            self.alive = False
        if 0 < self.health < 2:
            self.death_sound.play()


    

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
        # if -bar_width < x < 1024 + bar_width:
            # Background (dark red)
        pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))
            
            # Health (green)
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (0, 200, 0), (x, y, bar_width * health_ratio, bar_height))
            
            # Border
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 1)


    def update(self):
        
        now = pygame.time.get_ticks()
        
        # Death check
# --- DEATH CHECK ---
        if not self.alive:
            if self.state != "death":
                self.death_sound.play()
                self.set_state("death")
                
            elif self.current_frame >= len(self.frames):
                    if self.alpha < 100:
                        self.image.set_alpha(100 - self.alpha*10)
                        self.alpha += 1
                    else:
                        self.kill()
                    
            else:
                self.last_update = now
                self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)    
                self.current_frame+=1
                # Fade out before killing
            return
        
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        print(distance)
        # Flip sprite based on direction
        self.side_left = dx < 0

        
        # --- ATTACK LOGIC ---
        if not self.attacking:
            if distance < self.attack_range:
                self.set_state("idle")
                now = pygame.time.get_ticks() 
                if now - self.last_attack_time > self.damage_cooldown:
                    self.set_state("attack")
                    self.attacking = True
                    self.last_attack_time = now
                    
            elif distance < self.vision_range:
                self.set_state("walk")
                if distance!=0:
                    self.rect.x += int(self.speed * dx / distance)
                    self.rect.y += int(self.speed * dy / distance)  
            else:
                self.set_state("idle")
        else: 
            if self.current_frame == len(self.frames)/2 and distance < self.attack_range:
                self.target.take_damage(self.attack_damage)

        self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)
        
        # --- ANIMATION UPDATE FIRST ---
        if now - self.last_update >= FPS:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "attack":
                    self.set_state("idle")
                    self.attacking = False
                else:
                    self.current_frame = 0
