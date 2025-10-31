import pygame


class QuitButton:
    """Reusable quit button UI element.

    Usage:
      qb = QuitButton(screen)
      # inside event loop:
      if qb.handle_event(event):
          # clicked -> perform quit action
      # after drawing the scene:
      qb.draw()
    """

    def __init__(self, screen, width=110, height=40, margin_x=70, margin_y=20,
                 color=(180, 50, 50), hover_color=(220, 80, 80),
                 border=(120, 30, 30), text_color=(255, 255, 255),
                 font_name='Arial', font_size=20, bold=True):
        self.screen = screen
        self.width = width
        self.height = height
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.color = color
        self.hover_color = hover_color
        self.border = border
        self.text_color = text_color
        self.font = pygame.font.SysFont(font_name, font_size, bold=bold)
        self.hover = False
        self._recompute_rect()

    def _recompute_rect(self):
        sw = self.screen.get_width()
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
        qb_text = self.font.render("QUIT", True, self.text_color)
        qb_rect = qb_text.get_rect(center=self.rect.center)
        self.screen.blit(qb_text, qb_rect)
