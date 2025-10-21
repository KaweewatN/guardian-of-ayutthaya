"""
Game Start Module
Handles the start menu/splash screen
"""
import pygame
import os
import sys

# Add constant directory to path for font imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
from fonts import BUTTON_FONT


class GameStart:
    """Start menu with background and start button"""
    
    def __init__(self, screen):
        """
        Initialize the game start screen
        
        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BUTTON_COLOR = (200, 155, 91)  # #C89B5B
        self.BUTTON_HOVER_COLOR = (220, 175, 111)  # Lighter version for hover
        self.BUTTON_TEXT_COLOR = (75, 42, 12)  # #4B2A0C
        self.BUTTON_BORDER_COLOR = (168, 107, 39)  # #A86B27
        
        # Load story-1 as background
        self.background = None
        self.load_background()
        
        # Create fonts - imported from fonts module
        self.button_font = BUTTON_FONT
        
        # Button settings
        self.button_width = 250
        self.button_height = 70
        self.button_border_thickness = 5  # Thicker border
        self.button_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        self.button_rect.center = (self.screen_width // 2, self.screen_height - 120)
        self.button_hovered = False
        
    def load_background(self):
        """Load the Home background image"""
        bg_path = "assets/core/home.png"
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path)
            img_rect = img.get_rect()
            scale_factor = min(
                self.screen_width / img_rect.width,
                self.screen_height / img_rect.height
            )
            new_width = int(img_rect.width * scale_factor)
            new_height = int(img_rect.height * scale_factor)
            self.background = pygame.transform.scale(img, (new_width, new_height))
        else:
            print(f"Warning: {bg_path} not found")
            self.background = None
            
    def draw(self):
        """Draw the start menu"""
        self.screen.fill(self.BLACK)
        
        # Draw background
        if self.background:
            bg_rect = self.background.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            # Create darkened version
            darkened = self.background.copy()
            dark_overlay = pygame.Surface(darkened.get_size())
            dark_overlay.fill(self.BLACK)
            dark_overlay.set_alpha(20)
            darkened.blit(dark_overlay, (0, 0))
            self.screen.blit(darkened, bg_rect)
        
        # Draw start button
        color = self.BUTTON_HOVER_COLOR if self.button_hovered else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BUTTON_BORDER_COLOR, self.button_rect, self.button_border_thickness, border_radius=10)
        
        # Draw button text
        button_text = self.button_font.render("START", True, self.BUTTON_TEXT_COLOR)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
    def handle_event(self, event):
        """
        Handle menu events
        
        Args:
            event: Pygame event
            
        Returns:
            bool: True if start button was clicked, False otherwise
        """
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.button_hovered:
                return True
                
        return False
    
    def update_screen_size(self, screen):
        """Update menu for new screen size"""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.load_background()
        self.button_rect.center = (self.screen_width // 2, self.screen_height - 120)
