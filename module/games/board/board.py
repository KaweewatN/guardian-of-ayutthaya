import pygame

class Board:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.button_rect = pygame.Rect(0, 0, 400, 100)
        self.button_rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.button_color = (100, 200, 100)
        self.button_hover_color = (150, 255, 150)
        self.button_text_color = (0, 0, 0)
        self.button_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.button_hovered = False

    def draw(self):
        color = self.button_hover_color if self.button_hovered else self.button_color
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=20)
        text = self.button_font.render('Play Rock-Paper-Scissors', True, self.button_text_color)
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = self.button_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.button_hovered:
                return True  # Button clicked
        return False
