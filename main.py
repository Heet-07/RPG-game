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
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)

        # Menu state and pixel look
        self.state = "menu"  # menu | playing | level_complete | game_complete | level_select
        self.level_completed = {}  # e.g. {1: True, 2: False, 3: False}
        for i in range(1, TOTAL_LEVELS + 1):
            self.level_completed[i] = False

        self.menu_tick = 0
        self.pixel_size = (256, 192)
        self.pixel_font_small = pygame.font.Font(None, 16)
        self.pixel_font_large = pygame.font.Font(None, 24)
        self.menu_stars = [
            (random.randrange(self.pixel_size[0]), random.randrange(self.pixel_size[1] // 2))
            for _ in range(60)
        ]

        # --- define world/level state BEFORE load_level() ---
        self.level_number = 1
        self.level = None
        self.player = None
        self.enemy = None
        self.camera_x = 0

        self.lastDamage = 0
        self.damageCooldown = 500  

        # --- now it's safe to load level ---
        self.load_level(self.level_number)


    def load_level(self, n: int):
        self.level_number = n
        self.level = Level(level_number=n)

        # Create player (preserve health logic if needed)
        if self.player is None:
            self.player = Player(64, self.level.ground_y - PLAYER_HEIGHT - 100,
                                PLAYER_HEALTH, PLAYER_ATTACK_DAMAGE, PLAYER_SPEED, 3)
        else:
            # Reset player position and health
            self.player.x = 64
            self.player.y = self.level.ground_y - PLAYER_HEIGHT
            self.player.health = PLAYER_HEALTH

        # --- Always create a new enemy ---
        self.enemy = Enemy(800, self.level.ground_y - ENEMY_HEIGHT - 100,
                        ENEMY_HEALTH, ENEMY_ATTACK_DAMAGE, ENEMY_SPEED, 3, self.player)

        self.camera_x = 0


    def update_camera(self):
        """Follow player horizontally with smooth offset."""
        player_center_x = self.player.rect.centerx
        target = player_center_x - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(target, WORLD_WIDTH - SCREEN_WIDTH))


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
                    elif event.key == pygame.K_4:
                        self.state = "level_select"

                elif self.state == "playing":
                    if event.key == pygame.K_1:
                        self.load_level(1)
                    elif event.key == pygame.K_2:
                        self.load_level(2)
                    elif event.key == pygame.K_3:
                        self.load_level(3)
                    elif event.key == pygame.K_4:
                        self.state = "level_select"
                elif self.state == "level_complete":
                    if event.key == pygame.K_n:
                        # Go to next level or loop back to 1
                        next_level = self.level_number + 1 if self.level_number < TOTAL_LEVELS else 1
                        self.load_level(next_level)
                        self.state = "playing"
                    elif event.key == pygame.K_l:
                        self.state = "level_select"
                    elif event.key == pygame.K_m:
                        self.state = "menu"

                elif self.state == "level_select":
                    if event.key == pygame.K_m:
                        self.state = "menu"
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        level_choice = int(event.unicode)

                        # Can only play a level if it is unlocked (previous completed) or already completed
                        if self.level_completed.get(level_choice - 1, True) or self.level_completed[level_choice]:
                            self.load_level(level_choice)
                            self.state = "playing"


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

        hit_platform = pygame.sprite.spritecollide(self.player, self.level.platforms, False, pygame.sprite.collide_mask)

        if hit_platform:
            for p in hit_platform:
                if self.player.rect.centerx >= p.rect.left and self.player.rect.centerx <=p.rect.right:
                    if self.player.rect.centery <= p.rect.bottom:
                            self.player.rect.y -= 10 * GRAVITY
                            self.player.jump_speed = PLAYER_JUMP_POWER
                            self.player.jumping = False
                    elif self.player.rect.centery >= p.rect.top:
                        self.player.jump_speed = - 5
                else:
                    if self.player.rect.centerx >= p.rect.centerx:
                        self.player.rect.x += self.player.speed
                    else:
                        self.player.rect.x -= self.player.speed

        for enemy in self.level.enemies:
            enemy_hit_platforms = pygame.sprite.spritecollide(enemy, self.level.platforms, False, pygame.sprite.collide_mask)
            for p in enemy_hit_platforms:
                if enemy.rect.centerx >= p.rect.left and enemy.rect.centerx <=p.rect.right:
                    if enemy.rect.centery <= p.rect.bottom:
                         enemy.rect.y -= 10 * GRAVITY
                else:
                    if enemy.rect.centerx >= p.rect.centerx:
                     enemy.rect.x += enemy.speed
                    else:
                     enemy.rect.x -= enemy.speed

        self.level.enemies.update()
        self.player.update()
        self.enemy.update()
        self.update_camera()

        # --- LEVEL TRANSITION CHECK ---
        # When all enemies are dead AND player reaches end of level width
        end_x = WORLD_WIDTH - 100  # near the right edge (you can tweak)

        if not self.enemy.alive and self.player.rect.right >= end_x and self.state == "playing":
            # Mark level as completed
            self.level_completed[self.level_number] = True
            self.state = "level_complete"

        
    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "level_complete":
            self.draw_level_complete()
        
        elif self.state == "level_select":
            self.draw_level_select()

    
        else:
            self.level.draw(self.screen, self.camera_x)
            self.screen.blit(self.player.image, self.player.rect)
            self.screen.blit(self.enemy.image, self.enemy.rect)

            self.player.draw_health_bar(self.screen)
            if self.enemy.alive:
                self.enemy.draw_health_bar(self.screen, self.camera_x)

            draw_text(self.screen, "A/D or Arrows to move, Space to attack, Esc to quit",
                    self.font, WHITE, 16, 16)

        pygame.display.flip()

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

        
    def draw_level_complete(self):
        self.screen.fill((30, 30, 60))
        draw_text(self.screen, f"Level {self.level_number} Complete!", self.font, GREEN,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, center=True)

        # If next level exists
        if self.level_number < 4:
            draw_text(self.screen, "Press N for Next Level", self.font, WHITE,
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10, center=True)
        else:
            draw_text(self.screen, "All levels completed!", self.font, GREEN,
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10, center=True)
            draw_text(self.screen, "Press N to Replay from Level 1", self.font, WHITE,
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)

        draw_text(self.screen, "Press L for Level Select", self.font, WHITE,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, center=True)
        draw_text(self.screen, "Press M to return to Main Menu", self.font, WHITE,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90, center=True)

        
    def draw_level_select(self):
        self.screen.fill((25, 25, 45))
        draw_text(self.screen, "Select Level", self.font, WHITE,
                SCREEN_WIDTH // 2, 100, center=True)

        y_offset = 200
        for i in range(1, TOTAL_LEVELS + 1):
            status = "Completed" if self.level_completed[i] else "Locked" if not self.level_completed.get(i - 1, True) else "Unlocked"
            color = GREEN if status == "Completed" else WHITE if status == "Unlocked" else GRAY
            draw_text(self.screen, f"Level {i}: {status}", self.font, color,
                    SCREEN_WIDTH // 2, y_offset, center=True)
            y_offset += 50

        draw_text(self.screen, "Press 1/2/3 to play unlocked or completed levels", self.font, WHITE,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, center=True)
        draw_text(self.screen, "Press M to return to Main Menu", self.font, WHITE,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, center=True)




    def player_attack(self):
        if self.player.attacking:
            attack_block = self.player.get_attack_rect()
            now = pygame.time.get_ticks()
            if (attack_block is not None) and ((now-self.lastDamage) > self.damageCooldown):
                if attack_block.colliderect(self.enemy.rect) :
                    self.lastDamage = now
                    self.enemy.take_damage(PLAYER_ATTACK_DAMAGE)

    def run(self):
        # print("🟢 Entering run loop")
        while True:
            # you can keep this commented after debugging to avoid spam
            # print("loop")
            self.handle_events()
            self.draw()
            self.update()
            self.player_attack()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()


