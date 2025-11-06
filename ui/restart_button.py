import pygame
import os
import sys

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import BUTTON_FONT_SMALL


class RestartButton:
    """Reusable restart button UI element.

    Usage:
      rb = RestartButton(screen)
      # inside event loop:
      if rb.handle_event(event):
          # clicked -> perform restart action
      # after drawing the scene:
      rb.draw()
    """

    def __init__(self, screen, width=110, height=40, x=None, y=None,
                 color=(139, 90, 43), hover_color=(180, 120, 60),
                 border=(90, 60, 30), text_color=(255, 255, 255)):
        """
        Initialize the restart button.
        
        Args:
            screen: Pygame display surface
            width: Button width
            height: Button height
            x: X position (if None, will be centered)
            y: Y position (if None, will be centered)
            color: Normal button color
            hover_color: Hover button color
            border: Border color
            text_color: Text color
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = color
        self.hover_color = hover_color
        self.border = border
        self.text_color = text_color
        self.font = BUTTON_FONT_SMALL
        self.hover = False
        self._recompute_rect()

    def _recompute_rect(self):
        """Calculate button position."""
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        
        # Center if no position specified
        x = self.x if self.x is not None else (sw - self.width) // 2
        y = self.y if self.y is not None else (sh - self.height) // 2
        
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def handle_event(self, event):
        """Handle pygame events. Returns True if the restart button was clicked."""
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
        """Draw the restart button on the associated screen."""
        try:
            self._recompute_rect()
        except Exception:
            pass

        btn_color = self.hover_color if self.hover else self.color
        pygame.draw.rect(self.screen, btn_color, self.rect, border_radius=6)
        pygame.draw.rect(self.screen, self.border, self.rect, 2, border_radius=6)
        btn_text = self.font.render("Restart", True, self.text_color)
        btn_rect = btn_text.get_rect(center=self.rect.center)
        self.screen.blit(btn_text, btn_rect)
