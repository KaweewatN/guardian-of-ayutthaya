import pygame
import os
import sys

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import BUTTON_FONT_SMALL


class QuitButton:
    """Reusable quit button UI element.

    Usage:
      qb = QuitButton(screen)
      # inside event loop:c
      if qb.handle_event(event):
          # clicked -> perform quit action
      # after drawing the scene:
      qb.draw()
    """

    def __init__(self, screen, width=110, height=40, margin_x=30, margin_y=25,
                 color=(139, 90, 43), hover_color=(180, 120, 60),
                 border=(90, 60, 30), text_color=(255, 255, 255),
                 font_name='Arial', font_size=20, bold=True, position='left'):
        self.screen = screen
        self.width = width
        self.height = height
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.color = color
        self.hover_color = hover_color
        self.border = border
        self.text_color = text_color
        # Use centralized font system
        self.font = BUTTON_FONT_SMALL
        self.hover = False
        self.position = position  # 'left' or 'right'
        self._recompute_rect()

    def _recompute_rect(self):
        sw = self.screen.get_width()
        if self.position == 'left':
            # Position on left side
            self.rect = pygame.Rect(
                self.margin_x,
                self.margin_y,
                self.width,
                self.height,
            )
        else:
            # Position on right side (original behavior)
            self.rect = pygame.Rect(
                sw - self.margin_x - self.width,
                self.margin_y,
                self.width,
                self.height,
            )

    def handle_event(self, event):
        """Handle pygame events. Returns True if the quit button was clicked."""
        # Update rect in case screen changed externally
        try:
            self._recompute_rect()
        except Exception:
            pass

        if event.type == pygame.MOUSEMOTION:
            try:
                self.hover = self.rect.collidepoint(event.pos)
            except Exception:
                self.hover = False
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                if self.rect.collidepoint(event.pos):
                    return True
            except Exception:
                return False

        return False

    def draw(self):
        """Draw the quit button on the associated screen."""
        try:
            self._recompute_rect()
        except Exception:
            pass

        qb_color = self.hover_color if self.hover else self.color
        pygame.draw.rect(self.screen, qb_color, self.rect, border_radius=6)
        pygame.draw.rect(self.screen, self.border, self.rect, 2, border_radius=6)
        qb_text = self.font.render("Quit", True, self.text_color)
        qb_rect = qb_text.get_rect(center=self.rect.center)
        self.screen.blit(qb_text, qb_rect)
