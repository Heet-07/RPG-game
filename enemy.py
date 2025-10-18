import pygame
from settings import *

animation_orc={
    "idle": pygame.image.load("Photo/Orc/Orc_Idle.png"),
    "walk": pygame.image.load("Photo/Orc/Orc_Walk.png"),
    "hit": pygame.image.load("Photo/Orc/Orc_Hit.png"),
    "death": pygame.image.load("Photo/Orc/Orc_Death.png"),
    "attack": pygame.image.load("Photo/Orc/Orc_Attack02.png")
} 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, attack_damage,speed, scale, target):
        super().__init__()
        self.animations = animation_orc
        self.frame_width, self.frame_height = (100, 100)
        self.state = "idle"
        self.frames = self.load_frames(self.animations[self.state])
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y)) 
        self.mask = pygame.mask.from_surface(self.image, 0)       
        self.last_update = pygame.time.get_ticks()
        self.alive = True
        self.health = health
        self.attack_damage = attack_damage
        self.speed = speed
        self.target = target
        self.attack_range = 80
        self.vision_range = 300
        self.damage_cooldown = 1500
        self.last_attack_time = 0
        self.scales=scale
        self.attacking = False
        self.side_left = True
    
    def scale(self, scale):
        self.image=pygame.transform.scale(self.image, (scale*100, scale*100))
        self.mask = pygame.mask.from_surface(self.image, 0) 
    
    def load_frames(self, sprite_sheet):
        frames = []
        sheet_width = sprite_sheet.get_width()
        num_frames = sheet_width // self.frame_width
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(sprite_sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
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

    def update(self):
        
        self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)
        
        if not self.alive:
            self.set_state("death")
            
        dx = self.target.rect.x - self.rect.x
        dy = self.target.rect.y - self.rect.y
        
        if(dx<0):
            self.side_left = True
        else:
            self.side_left = False
        
        distance = (dx**2 + dy**2)**0.5
        
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

        now = pygame.time.get_ticks()
        if now - self.last_update >= FPS:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "attack":
                    self.set_state("idle")
                    self.attacking = False
                elif self.state == "death":
                    self.current_frame = len(self.frames) - 1
                    self.alive = False
                else:
                    self.current_frame = 0

        self.scale(self.scales)