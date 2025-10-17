import pygame
from settings import *

# saving frames for different actions
animation_soldier={
    "walk": pygame.image.load("Photo/Soldier/Soldier_Walk.png"),
    "idle": pygame.image.load("Photo/Soldier/Soldier_Idle.png"),
    "attack": pygame.image.load("Photo/Soldier/Soldier_Attack01.png"),
    "death": pygame.image.load("Photo/Soldier/Soldier_Death.png"),
    "hit": pygame.image.load("Photo/Soldier/Soldier_Hit.png")
}


class Player(pygame.sprite.Sprite):
    #initalize player
    def __init__(self, x, y, health, attack_damage, speed, scale):
        super().__init__()
        self.animations=animation_soldier
        self.frame_width, self.frame_height=(100, 100)
        
        self.state="idle"
        self.frames=self.load_frame(self.animations[self.state], scale)
        self.current_frame=0
        self.image=self.frames[self.current_frame]
        self.scale(scale)
        self.mask=pygame.mask.from_surface(self.image, 0)
        self.rect=self.image.get_rect(topleft=(x, y))
        self.last_update=pygame.time.get_ticks()
        self.alive=True
        self.speed=speed
        self.side_left=False
        self.scales=scale
        self.health=health
        self.attack_damage=attack_damage
        self.attacking = False
    
    # magnify size of player    
    def scale(self, scale):
        self.image=pygame.transform.scale(self.image, (scale*100, scale*100))
        
    # load frames for given action     
    def load_frame(self, sprite_sheet, scale):
        frames=[]
        sheet_width=sprite_sheet.get_width()
        num_frames=sheet_width//self.frame_width
        for i in range(num_frames):
            frame=pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(sprite_sheet, (0, 0), (i * self.frame_width, 0, self.frame_width, self.frame_height))
            # pygame.transform.scale(frame, (self.scales*100, self.scales*100))
            frames.append(pygame.transform.scale(frame, (scale*100, scale*100)))
        return frames
    
    # set the new state of player 
    def set_state(self,new_state):
        if new_state != self.state and new_state in self.animations:
            self.state = new_state
            self.frames = self.load_frame(self.animations[self.state], self.scales)
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            
    # update the player        
    def update(self):
        
        self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)
        self.mask=pygame.mask.from_surface(self.image, 0)
        
        # handling the key inputs for player
        keys = pygame.key.get_pressed()
        if not self.attacking:
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.side_left=False
                self.set_state("walk")
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.side_left=True
                self.set_state("walk")
            elif keys[pygame.K_SPACE]:
                self.set_state("attack")
                self.attacking = True
            else:
                self.set_state("idle")
            
        
        # setting the player state
        now = pygame.time.get_ticks()
        if now - self.last_update >=FPS:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "attack":
                    self.attacking = False
                    self.set_state("idle")
                elif self.state == "death":
                    self.current_frame = len(self.frames) - 1
                    self.alive = False
                else:
                    self.current_frame = 0
                