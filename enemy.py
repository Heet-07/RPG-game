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
        self.animations = animation_orc # initialize animation frames
        self.frame_width, self.frame_height = 100, 100 # set dimension of enemy rect
        self.state = "idle" # give the current state of enemy
        self.scales = scale
        self.frames = self.load_frames(self.animations[self.state]) # load the image according to current frame 
        self.current_frame = 0 # track of current frame in animation
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image) # make mask of enemy
        self.last_update = pygame.time.get_ticks() # track when last state updated
        self.alive = True # give enemy status of alive or not
        self.max_health = health # maximum health of enemy
        self.health = health # current health of enemy
        self.attack_damage = attack_damage # attack power of enemy
        self.speed = speed # enemy movment speed
        self.target = target # set the opponent of enemy
        self.scale = scale
        self.attack_range = 70 # when player is in this range then enemy will attack
        self.vision_range = 300 # when player is in this range then enemy will approach him
        self.damage_cooldown = 250 # take cooldown time between 2 consicutive attack
        self.last_attack_time = 0 # track of when enemy last time attack
        self.attacking = False # check whether enemy is attacking or not
        self.hitted = False # check whether enemy taking damage or not
        self.side_left = True # check whether side the enemy face
        self.alpha = 0

        # Load sounds
        if self.scale == 3:
            self.death_sound = pygame.mixer.Sound("Audio/orc_death1.MP3") # set death sound for normal goblin
        else:
            self.death_sound = pygame.mixer.Sound("Audio/orc_boss_death.MP3") # set death sound for boss goblin
        self.death_sound.set_volume(0.6) # set the volume for death sound

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

    # set the new state for enemy
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
                self.death_sound.play() # play death sound when enemy is dead
            if self.state == "hit":
                self.hitted = True

    # reduce damage when enemy is hitted by the player
    def take_damage(self, damage):
        now = pygame.time.get_ticks()
        if not self.hitted:
            self.set_state("hit")
            self.health -= damage
            if self.health <= 0 and self.alive:
                self.health = 0
                self.set_state("death")

    # update the enemy at each frame
    def update(self):
        
        # set the enemy on the ground and apply gravity on them
        if self.scales == 3:
            if self.rect.y >= SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100:
                self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100
            else:
                self.rect.y += 10 * GRAVITY
        else:
            if self.rect.y >=SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT*5 - 22:
                self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT*5 - 22
            else:
                self.rect.y += 10 * GRAVITY
        now = pygame.time.get_ticks()
        
        # Death check
        if not self.alive:            
            if self.current_frame >= len(self.frames):
                    if self.alpha < 100:
                        self.image.set_alpha(100 - 2*self.alpha)
                        self.alpha += 1
                    else:
                        self.kill()
            else:
                self.last_update = now
                self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)    
                self.current_frame+=1
            return
        
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5

        # Flip sprite based on direction
        self.side_left = dx < 0

        
        # attack logic
        if not self.attacking and not self.hitted and self.target.alive:
            if distance < self.attack_range: # then enemy will attack
                self.set_state("idle")
                now = pygame.time.get_ticks() 
                if now - self.last_attack_time > self.damage_cooldown:
                    self.set_state("attack")
                    self.attacking = True
                    self.last_attack_time = now
                    
            elif distance < self.vision_range: # then enemy approach the player
                self.set_state("walk")
                if distance!=0:
                    self.rect.x += int(self.speed * dx / distance)
            else:
                self.set_state("idle")
        elif self.attacking: 
            if self.current_frame == len(self.frames)/2 and distance < self.attack_range: # when enemy's sword connet with player
                self.target.take_damage(self.attack_damage)

        # update the image and mask
        self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)
        self.mask = pygame.mask.from_surface(self.image)
        
        # animation logic
        if now - self.last_update >= FPS:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "attack":
                    self.set_state("idle")
                    self.attacking = False
                elif self.state == "hit":
                    self.set_state("idle")
                    self.hitted = False
                else:
                    self.current_frame = 0
    