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
        self.now = pygame.time.get_ticks()
        
        # ADDED: Health tracking variables
        self.max_health=health
        self.health=health
        self.attack_damage=attack_damage
        self.attacking = False
        self.last_attack = 0
        self.hitted = False
        self.jumping = False
        self.jump_speed = PLAYER_JUMP_POWER
        # ADDED: Attack hitbox variables
        self.attack_rect = None
        self.last_damage_time = 0
        self.damage_cooldown = 800  # ms between damage to same enemy


        # Load sounds
        self.hit = pygame.mixer.Sound("Audio/player_hit1.mp3")  
        self.hit.set_volume(0.3)
    
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
    
    def jump(self):
        if self.rect.y > SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100 and self.jumping:
            self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100
            self.jump_speed = PLAYER_JUMP_POWER
            self.jumping = False
        elif self.jumping:
            self.rect.y -= self.jump_speed
            if self.jump_speed >= -10* GRAVITY:
                self.jump_speed -= GRAVITY

    # set the new state of player 
    def set_state(self,new_state):
        if new_state != self.state and new_state in self.animations:
            self.state = new_state
            self.frames = self.load_frame(self.animations[self.state], self.scales)
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            if self.state == "death":
                self.alive = False
            if self.state == "hit":
                self.hitted = True
    

    def get_attack_rect(self):
        # if self.attacking:
            # attack_rect = pygame.Rect(self.rect.x, self.rect.y, 100, 28)
            # attack_rect.width = 2
            # if self.side_left:
            #     attack_rect.right = self.rect.left 
            # else:
            #     attack_rect.left = self.rect.right
                
            # return attack_rect
        # return None    
        pass


    # ADDED: Take damage from enemy
    def take_damage(self, damage):
        if self.alive:
            self.set_state("hit")
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.set_state("death")
                
    
    
    # ADDED: Draw health bar on screen
    def draw_health_bar(self, screen):
        bar_width = 200
        bar_height = 20
        x = 20
        y = 50
        
        # Background (dark red)
        pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))
        
        # Health (green)
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (0, 200, 0), (x, y, bar_width * health_ratio, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        # Text
        font = pygame.font.Font(None, 16)
        text = font.render(f"Player HP: {(self.health)}/{(self.max_health)}", True, WHITE)
        # text = font.render("HP", True, WHITE)
        screen.blit(text, (x + 10, y + 2))
        pygame.draw.rect(screen, SKY_BLUE, (x, y+40, bar_width, bar_height), 2)
        if self.now - self.last_attack <= 1500:
            pygame.draw.rect(screen, SKY_BLUE, (x, y+40, bar_width*(self.now - self.last_attack)/1500, bar_height))
        else:
            pygame.draw.rect(screen, SKY_BLUE, (x, y+40, bar_width, bar_height))
    
    # update the player        
    def update(self):
        
        self.now = pygame.time.get_ticks()
        
        if not self.alive and self.current_frame == len(self.frames):
            return
        
        if self.rect.y >= SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100 and not self.jumping:
            self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 100
        elif not self.jumping:
            self.rect.y += 10 * GRAVITY        
        # handling the key inputs for player
        keys = pygame.key.get_pressed()
        if not self.attacking and self.alive and not self.hitted:
            
            if keys[pygame.K_SPACE]:
                self.jumping = True
                
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                self.side_left=False
                self.set_state("walk")
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                self.side_left=True
                self.set_state("walk")
            elif keys[pygame.K_z] and self.now - self.last_attack > 1500:
                self.set_state("attack")
                self.last_attack = self.now
                self.hit.play()
                self.attacking = True
            else:
                self.set_state("idle")
                
            if self.jumping:
                self.jump()

        
        # setting the player state
        if self.now - self.last_update >=FPS:
            self.last_update = self.now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.state == "attack":
                    self.attacking = False
                    self.set_state("idle")
                elif self.state == "hit":
                    self.set_state("idle")
                    self.hitted = False
                elif self.state == "death":
                    self.current_frame = len(self.frames) - 1
                else:
                    self.current_frame = 0
                    
                    
        self.image = pygame.transform.flip(self.frames[self.current_frame], self.side_left, False)
        self.mask=pygame.mask.from_surface(self.image, 0)