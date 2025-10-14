import pygame

def draw_text(surface, text, font, color, x, y, center=False):
    """Draw text on a surface (helper)."""
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt, rect)