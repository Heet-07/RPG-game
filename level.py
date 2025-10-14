import os
import pygame
from settings import *

class Level:
    """Minimal level with a single background image and a flat ground."""
    def __init__(self, level_number: int = 1):
        self.number = level_number
        self.bg_image = None
        self.scroll_factor = 0.2  # subtle parallax for background
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT

        self._load_background()

    def _load_background(self):
        """Load a single full background for the level, if present.
        Priority (first found is used):
        1) assets/level{n}.jpg (and level_{n}.jpg/.png)
        2) assets/backgrounds/level_{n}.*
        3) pack: assets/Free Pixel Art Forest/PNG/Background layers/level_{n}.* (or full.png)
        4) assets/background.png/bg.png then any other image in assets
        If none found, bg_image stays None and we use a sky fill.
        """
        base = os.path.dirname(__file__)
        assets_dir = os.path.join(base, "assets")

        def add(paths, bucket):
            for p in paths:
                bucket.append(p)

        # 1) Assets root, explicit level file names (jpg preference as requested)
        candidates: list[str] = []
        add([
            os.path.join(assets_dir, f"level{self.number}.jpg"),
            os.path.join(assets_dir, f"level_{self.number}.jpg"),
            os.path.join(assets_dir, f"level{self.number}.png"),
            os.path.join(assets_dir, f"level_{self.number}.png"),
        ], candidates)

        # 2) assets/backgrounds/level_*.{png,jpg}
        add([
            os.path.join(base, "assets", "backgrounds", f"level_{self.number}.jpg"),
            os.path.join(base, "assets", "backgrounds", f"level{self.number}.jpg"),
            os.path.join(base, "assets", "backgrounds", f"level_{self.number}.png"),
            os.path.join(base, "assets", "backgrounds", f"level{self.number}.png"),
        ], candidates)

        # 3) Pack directory
        pack_dir = os.path.join(base, "assets", "Free Pixel Art Forest", "PNG", "Background layers")
        add([
            os.path.join(pack_dir, f"level_{self.number}.png"),
            os.path.join(pack_dir, f"level{self.number}.png"),
            os.path.join(pack_dir, "full.png"),
        ], candidates)

        # 4) Preferred generic names then any image in assets root
        add([os.path.join(assets_dir, n) for n in ("background.jpg", "bg.jpg", "background.png", "bg.png")], candidates)
        try:
            if os.path.isdir(assets_dir):
                for name in sorted(os.listdir(assets_dir)):
                    lower = name.lower()
                    if lower.endswith((".png", ".jpg", ".jpeg")):
                        candidates.append(os.path.join(assets_dir, name))
        except Exception:
            pass

        for path in candidates:
            if os.path.isfile(path):
                try:
                    lower = path.lower()
                    # Use convert() for JPEG (no alpha), convert_alpha() for PNG
                    if lower.endswith((".jpg", ".jpeg")):
                        img = pygame.image.load(path).convert()
                    else:
                        img = pygame.image.load(path).convert_alpha()
                    ih, iw = img.get_height(), img.get_width()
                    if ih > 0:
                        scale = SCREEN_HEIGHT / ih
                        img = pygame.transform.smoothscale(img, (int(iw * scale), SCREEN_HEIGHT))
                    self.bg_image = img
                    return
                except Exception:
                    continue

    def draw_background(self, surface, camera_x: int = 0):
        if self.bg_image is None:
            surface.fill(SKY_BLUE)
            return
        img = self.bg_image
        w = img.get_width()
        # Scroll based on factor, then tile horizontally
        x = -int(camera_x * self.scroll_factor) % w
        surface.blit(img, (x - w, 0))
        surface.blit(img, (x, 0))

    def draw_ground(self, surface, camera_x: int = 0):
        # Simple flat ground strip
        ground_color = (40, 60, 90)
        pygame.draw.rect(surface, ground_color, (0, self.ground_y, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Debug ground markers to show horizontal motion relative to camera
        tick_color = (90, 120, 160)
        spacing = 64
        offset = (-int(camera_x)) % spacing
        top = self.ground_y
        for x in range(offset, SCREEN_WIDTH + spacing, spacing):
            pygame.draw.line(surface, tick_color, (x, top), (x, top + 12), 2)

    def draw(self, surface, camera_x: int = 0):
        self.draw_background(surface, camera_x)
        self.draw_ground(surface, camera_x)