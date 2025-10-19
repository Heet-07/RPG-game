import sys
import random
import pygame
from settings import *
from utils import draw_text
from level import Level
from player import Player
from enemy import Enemy

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)

        # Menu state and pixel look
        self.state = "menu"  # menu | playing
        self.menu_tick = 0
        self.pixel_size = (256, 192)  # base pixel surface (4x scale -> 1024x768)
        self.pixel_font_small = pygame.font.Font(None, 16)
        self.pixel_font_large = pygame.font.Font(None, 24)
        # Simple starfield for the menu
        self.menu_stars = [(random.randrange(self.pixel_size[0]), random.randrange(self.pixel_size[1]//2)) for _ in range(60)]

        # World / Level state
        self.level_number = 1
        self.level = None
        self.player = None
        self.enemy = None
        self.camera_x = 0

        self.load_level(self.level_number)

    def load_level(self, n: int):
        self.level_number = n
        self.level = Level(level_number=n)
        if (self.player is None) and (self.enemy is None):
            self.player = Player(64, self.level.ground_y - PLAYER_HEIGHT - 100, PLAYER_HEALTH, PLAYER_ATTACK_DAMAGE, PLAYER_SPEED, 3)
            self.enemy = Enemy(800, self.level.ground_y - ENEMY_HEIGHT - 100, ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3, self.player)
        else:
            # Reset player on ground at start
            self.player.x = 64
            self.player.y = self.level.ground_y - PLAYER_HEIGHT
            self.enemy.x = 800
            self.enemy.y = self.level.ground_y - ENEMY_HEIGHT
        self.camera_x = 0
        
        self.player.draw_health_bar(self.screen)
        self.enemy.draw_health_bar(self.screen, self.camera_x)


    def update_camera(self):
        # Follow player with a lead
        target = self.player.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, int(self.player.x))
        self.camera_x = min(self.camera_x, SCREEN_WIDTH)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state == "menu":
                    if event.key == pygame.K_RETURN:
                        # Start game
                        self.state = "playing"
                        self.load_level(self.level_number)
                elif self.state == "playing":
                    if event.key == pygame.K_1:
                        self.load_level(1)
                    elif event.key == pygame.K_2:
                        self.load_level(2)

    def update(self):
        if self.state == "menu":
            # Animate menu stars
            self.menu_tick += 1
            # Move stars slowly left; wrap around
            new_stars = []
            for x, y in self.menu_stars:
                speed = 1 if y % 3 else 2
                x -= speed
                if x < 0:
                    x = self.pixel_size[0] - 1
                    y = random.randrange(self.pixel_size[1]//2)
                new_stars.append((x, y))
            self.menu_stars = new_stars
            return

        self.player.update()
        self.enemy.update()
        self.update_camera()
        
    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        else:
            self.level.draw(self.screen, self.camera_x)
            self.screen.blit(self.player.image, self.player.rect)
            self.screen.blit(self.enemy.image, self.enemy.rect)
            
            # Draw health bar **after everything else**
            self.player.draw_health_bar(self.screen)
            self.enemy.draw_health_bar(self.screen, self.camera_x)

            # UI hint
            draw_text(self.screen, "A/D or Arrows to move, Space to attack, Esc to quit", self.font, WHITE, 16, 16)
            # Debug overlay
            # self.draw_debug()
        pygame.display.flip()

    def draw_debug(self):
        y = 44
        line_h = 20
        dbg = [
            f"fps: {self.clock.get_fps():.1f}",
            f"state: {self.state}",
            f"level: {self.level_number}",
            f"player x:{self.player.x:.1f} y:{self.player.y:.1f}",
            f"vel vx:{self.player.vx:.1f} vy:{self.player.vy:.1f}",
            f"camera_x:{self.camera_x}",
        ]
        for s in dbg:
            draw_text(self.screen, s, self.font, WHITE, 16, y)
            y += line_h

    def draw_menu(self):
        # Low-res render target for crisp pixel look
        pw, ph = self.pixel_size
        surf = pygame.Surface((pw, ph))
        # Background gradient sky
        surf.fill((40, 40, 75))
        for i in range(ph//2):
            c = 75 + i // 2
            pygame.draw.line(surf, (c, 160, 220), (0, i), (pw, i))
        # Starfield
        for x, y in self.menu_stars:
            surf.set_at((x, y), (255, 255, 255))
        
        # Silhouette hills
        pygame.draw.rect(surf, (20, 35, 60), (0, ph-40, pw, 40))
        pygame.draw.rect(surf, (15, 25, 45), (0, ph-28, pw, 28))

        # Title and prompt (pixel fonts)
        title = "Dungeon Platformer"
        prompt = "Press ENTER to Start"
        # Simple blinking
        show_prompt = (self.menu_tick // 30) % 2 == 0
        title_font = self.pixel_font_large
        small_font = self.pixel_font_small
        # Draw title centered
        title_surf = title_font.render(title, True, WHITE)
        trect = title_surf.get_rect(center=(pw//2, ph//2 - 20))
        surf.blit(title_surf, trect)
        # Prompt
        if show_prompt:
            prompt_surf = small_font.render(prompt, True, (255, 230, 120))
            prect = prompt_surf.get_rect(center=(pw//2, ph//2 + 8))
            surf.blit(prompt_surf, prect)
        # Hint
        hint = small_font.render("Esc to Quit • 1/2 choose level in-game", True, (210, 210, 210))
        hrect = hint.get_rect(center=(pw//2, ph - 14))
        surf.blit(hint, hrect)

        # Scale up to screen size with nearest-neighbor
        scaled = pygame.transform.scale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()