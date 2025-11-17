"""
Tutorial Button UI Component
Shows a button to open the tutorial at any time during gameplay
"""
import pygame
import os
import sys


class TutorialButton:
    """Tutorial button that can be placed on the board"""
    
    def __init__(self, screen, position='left', margin_x=110, margin_y=20):
        """
        Initialize tutorial button
        
        Args:
            screen: Pygame display surface
            position: 'left' or 'right' side of screen
            margin_x: Horizontal margin from edge (base position)
            margin_y: Vertical margin from top (same as other buttons)
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.position = position
        self.margin_x = margin_x
        self.margin_y = margin_y
        
        # Button state
        self.hovered = False
        self.visible = True
        
        # Colors matching sound button style
        self.button_color = (139, 90, 43)  # Same brown as sound button
        self.hover_color = (180, 120, 60)  # Same hover as sound button
        self.border_color = (90, 60, 30)  # Same border as sound button
        self.text_color = (255, 255, 255)
        
        # Load icon (info symbol)
        self.icon = None
        self.load_icon()
        
        # Create button rectangle - same size as sound button
        self.button_size = 50  # Same as sound button (50x50)
        self.create_button()
    
    def load_icon(self):
        """Load or create info icon (sized for 50x50 button)"""
        # Create a simple "i" info icon
        self.icon_surface = pygame.Surface((36, 36), pygame.SRCALPHA)
        
        # Draw circle background
        pygame.draw.circle(self.icon_surface, (255, 255, 255), (18, 18), 16, 3)
        
        # Draw "i" letter
        font = pygame.font.SysFont('Arial', 26, bold=True)
        text = font.render('i', True, (255, 255, 255))
        text_rect = text.get_rect(center=(18, 18))
        self.icon_surface.blit(text, text_rect)
    
    def create_button(self):
        """Create button rectangle based on position (5px left of sound button position)"""
        # Sound button is at margin_x=70, so tutorial button at margin_x - 5 from sound position
        # That means: 70 - 50 (button width) - 5 (gap) = 15
        if self.position == 'left':
            x = 170 
        else:
            x = self.screen_width - self.margin_x - self.button_size
        
        y = self.margin_y
        
        self.button_rect = pygame.Rect(x, y, self.button_size, self.button_size)
    
    def handle_event(self, event):
        """
        Handle mouse events
        
        Args:
            event: Pygame event
            
        Returns:
            bool: True if tutorial should open, False otherwise
        """
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.button_rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.button_rect.collidepoint(event.pos):
                    return True  # Open tutorial
        
        return False
    
    def draw(self):
        """Draw the tutorial button"""
        if not self.visible:
            return
        
        # Choose color based on hover state
        color = self.hover_color if self.hovered else self.button_color
        
        # Draw button background
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=10)
        
        # Draw button border (same style as sound button)
        pygame.draw.rect(self.screen, self.border_color, self.button_rect, 3, border_radius=10)
        
        # Draw icon in center
        if self.icon_surface:
            icon_rect = self.icon_surface.get_rect(center=self.button_rect.center)
            self.screen.blit(self.icon_surface, icon_rect)
    
    def set_visible(self, visible):
        """Set button visibility"""
        self.visible = visible
    
    def is_hovered(self):
        """Check if button is currently hovered"""
        return self.hovered


# Test the button
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Tutorial Button Test")
    clock = pygame.time.Clock()
    
    # Create tutorial button
    tutorial_button = TutorialButton(screen, position='left', margin_x=140)
    
    print("=" * 60)
    print("Tutorial Button - Test Mode")
    print("=" * 60)
    print("Hover over the button to see hover effect")
    print("Click the button to trigger tutorial open")
    print("=" * 60)
    
    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if tutorial_button.handle_event(event):
                print("Tutorial button clicked!")
        
        # Draw
        screen.fill((50, 50, 50))
        tutorial_button.draw()
        pygame.display.flip()
    
    pygame.quit()
