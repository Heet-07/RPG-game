import pygame
from settings import *

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing_right = True
        self.want_jump = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def handle_input(self, keys):
        # Horizontal input
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        self.vx = 0
        if left:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if right:
            self.vx = PLAYER_SPEED
            self.facing_right = True
        # Jump (pressed during this frame will be picked up in update if on ground)
        self.want_jump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

    def update(self, level):
        # Apply gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # Horizontal move
        self.x += self.vx

        # Vertical move
        self.y += self.vy

        # Ground collision (flat ground)
        ground_y = level.ground_y
        if self.y + self.h >= ground_y:
            self.y = ground_y - self.h
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Handle jump after ground resolution
        if self.want_jump and self.on_ground:
            self.vy = PLAYER_JUMP_POWER
            self.on_ground = False
        self.want_jump = False

    def draw(self, surface, camera_x: int = 0):
        # Simple rectangle player
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y)
        pygame.draw.rect(surface, BLUE, (draw_x, draw_y, self.w, self.h))
        pygame.draw.rect(surface, WHITE, (draw_x, draw_y, self.w, self.h), 2)