import os
import pygame
import random
from settings import *
from enemy import Enemy


class Level:
    """Level with two parallax layers (rear + mid) and platforms."""
    def __init__(self, level_number: int = 1):
        from game_platform import Platform
        self.number = level_number
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.grass_pattern = self._generate_grass_pattern()

        self.enemies = pygame.sprite.Group()

        # Platforms
        self.platforms = pygame.sprite.Group()
        self.layouts = {
            1: [
                (600, self.ground_y - 170, 800, 40),
                (950, self.ground_y - 130, 100, 150)
            ],
            2: [
                (600, self.ground_y - 170, 450, 40),
                (950, self.ground_y - 130, 100, 150),
                (1250, self.ground_y - 280, 300, 40),
                (1500, self.ground_y - 240, 50, 260),
                (1550, self.ground_y - 150, 600, 40),
                (1750, self.ground_y - 380, 550, 40),
                (2250, self.ground_y - 340, 50, 360),
                (2300, self.ground_y - 180 , 100, 40)
            ],
            3: [
                (600, self.ground_y - 80, 50, 100),
                (600, self.ground_y - 130, 150, 50),
                (750, self.ground_y - 230, 50, 150),
                (750, self.ground_y - 280, 400, 50),
                (1150, self.ground_y - 100, 200, 120),
                (1350, self.ground_y - 280, 500, 50),
                (1850, self.ground_y - 380, 50, 150),
                (2000, self.ground_y - 430, 400, 50),
                
            ],
        }
        
        self.enemy={
            1 :[
                (750, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (700, self.ground_y - ENEMY_HEIGHT - 350, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (950, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3)
            ],
            2 :[
                (650, self.ground_y - ENEMY_HEIGHT - 300, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (750, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (750, self.ground_y - ENEMY_HEIGHT - 300, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (1300, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (1300, self.ground_y - ENEMY_HEIGHT - 500, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (1500, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
            ],
            3 :[
                (750, self.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (1550, self.ground_y - ENEMY_HEIGHT - 400, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (2200, self.ground_y - ENEMY_HEIGHT - 550, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3),
                (2400, self.ground_y - ENEMY_HEIGHT - 500, ENEMY_HEALTH*10, ENEMY_ATTACK_DAMAGE*5, PLAYER_SPEED, 5),
            ]
        }
        
        for p in self.layouts.get(self.number, []):
            self.platforms.add(Platform(*p))
        
        self.layers = []
        self._load_background_layers()

    # ----------------------------------------------------------------------
    def _load_background_layers(self):
        """Load level-specific parallax backgrounds (rear & mid)."""
        bg_dir = os.path.join(os.getcwd(), "assets", "backgrounds")
        print(f"📁 Background folder: {bg_dir}")



        # Expected filenames (use your exact files)
        layer_files = [
            (f"level{self.number}rear.png", 0.3),  # rear = far = slower
            (f"level{self.number}mid.png", 0.6),   # mid = closer = faster
        ]

        for name, speed in layer_files:
            path = os.path.join(bg_dir, name)
            if os.path.isfile(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    scale = SCREEN_HEIGHT / img.get_height()
                    img = pygame.transform.smoothscale(
                        img, (int(img.get_width() * scale), SCREEN_HEIGHT)
                    )
                    self.layers.append((img, speed))
                except Exception as e:
                    print(f"Failed to load {name}:", e)

        # Fallback (if missing files)
        if not self.layers:
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            surf.fill(SKY_BLUE)
            self.layers.append((surf, 0.2))

    # ----------------------------------------------------------------------
    def draw_background(self, surface, camera_x: int = 0):
        """Draw parallax background layers."""
        for img, speed in self.layers:
            w = img.get_width()
            x = -int(camera_x * speed) % w
            surface.blit(img, (x - w, 0))
            surface.blit(img, (x, 0))

    """def draw_ground(self, surface, camera_x: int = 0):
        '''Draw simple flat ground.'''
        ground_color = (40, 60, 90)
        pygame.draw.rect(surface, (40, 60, 90), (0 - camera_x, self.ground_y, WORLD_WIDTH, GROUND_HEIGHT))

        tick_color = (90, 120, 160)
        spacing = 64
        offset = (-int(camera_x)) % spacing
        for x in range(offset, SCREEN_WIDTH + spacing, spacing):
            pygame.draw.line(surface, tick_color, (x, self.ground_y), (x, self.ground_y + 12), 2)"""
    
    def _generate_grass_pattern(self):
        """Pre-generate a static grass pattern and dirt patches once per level."""
        grass = []
        patch = []

        random.seed(self.number)  # unique but consistent per level
        for x in range(0, WORLD_WIDTH, 8):
            height = 6 + random.randint(-2, 2)
            grass.append((x, height))

        for _ in range(40):  # dirt detail
            px = random.randint(0, WORLD_WIDTH)
            pw = random.randint(20, 60)
            py = random.randint(4, GROUND_HEIGHT - 8)
            patch.append((px, pw, py))

        return {"grass": grass, "patch": patch}

    
    def draw_ground(self, surface, camera_x: int = 0):
        """Draw polished static ground with pre-generated grass and patches."""
        # Dirt gradient
        top_color = (60, 90, 40)
        bottom_color = (30, 50, 20)
        for y in range(GROUND_HEIGHT):
            ratio = y / GROUND_HEIGHT
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b),
                            (0, self.ground_y + y),
                            (SCREEN_WIDTH, self.ground_y + y))

        # Grass top — STATIC, pre-generated
        for gx, height in self.grass_pattern["grass"]:
            screen_x = gx - camera_x
            if -8 <= screen_x <= SCREEN_WIDTH:
                pygame.draw.rect(surface, (80, 200, 80),
                                (screen_x, self.ground_y - height, 8, height))

        # Optional soft shadow for depth
        for gx, height in self.grass_pattern["grass"]:
            screen_x = gx - camera_x
            if -8 <= screen_x <= SCREEN_WIDTH:
                pygame.draw.rect(surface, (40, 80, 40),
                                (screen_x, self.ground_y - 2, 8, 2))

        # Dirt patches for texture
        for px, pw, py in self.grass_pattern["patch"]:
            screen_x = px - camera_x
            if -pw <= screen_x <= SCREEN_WIDTH:
                pygame.draw.rect(surface, (40, 70, 40),
                                (screen_x, self.ground_y + py, pw, 4))



    def draw_platforms(self, surface, camera_x: int = 0):
        """Draw all platforms relative to camera, only if visible."""
        for p in self.platforms:
            screen_x = p.rect.x - camera_x
            # if -200 < screen_x < SCREEN_WIDTH + 200:  # simple cull
            surface.blit(p.image, (screen_x, p.rect.y))


    def draw(self, surface, camera_x: int = 0):
        """Render order: background → ground → platforms."""
        self.draw_background(surface, camera_x)
        self.draw_ground(surface, camera_x)
        self.draw_platforms(surface, camera_x)

    def spawn_enemy(self, player):
        for e in self.enemy.get(self.number, []):
            self.enemies.add(Enemy(*e, player))