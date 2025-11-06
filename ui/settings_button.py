"""
Settings Button and Popup
Provides a settings button that opens a popup with quit and restart options
"""
import pygame
import os
import sys

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import BUTTON_FONT_SMALL, TEXT_FONT_BOLD, HINT_FONT


class SettingsButton:
    """
    Settings button with popup menu.
    
    When clicked, displays a popup with Quit and Restart buttons.
    
    Usage:
        sb = SettingsButton(screen)
        # inside event loop:
        result = sb.handle_event(event)
        if result == 'quit':
            # Handle quit
        elif result == 'restart':
            # Handle restart
        # after drawing the scene:
        sb.draw()
    """
    
    def __init__(self, screen, width=50, height=50, margin_x=20, margin_y=20,
                 color=(139, 90, 43), hover_color=(180, 120, 60),
                 border=(90, 60, 30), position='right'):
        """
        Initialize the settings button.
        
        Args:
            screen: Pygame display surface
            width: Button width in pixels
            height: Button height in pixels
            margin_x: Margin from edge
            margin_y: Margin from top
            color: Normal button color (RGB)
            hover_color: Button color when hovered (RGB)
            border: Border color (RGB)
            position: 'left' or 'right' - position on screen
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.color = color
        self.hover_color = hover_color
        self.border = border
        self.position = position
        self.hover = False
        
        # Popup state
        self.popup_visible = False
        self.popup_width = 400
        self.popup_height = 300
        
        # Button dimensions for popup buttons
        self.popup_button_width = 180
        self.popup_button_height = 60
        self.popup_button_spacing = 30
        
        # Hover states for popup buttons
        self.quit_button_hover = False
        self.restart_button_hover = False
        
        # Fonts
        self.button_font = BUTTON_FONT_SMALL
        self.title_font = TEXT_FONT_BOLD
        
        # Calculate positions
        self._recompute_positions()
    
    def _recompute_positions(self):
        """Calculate button and popup positions."""
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        
        # Settings button position
        if self.position == 'right':
            x = sw - self.margin_x - self.width
        else:
            x = self.margin_x
        
        self.rect = pygame.Rect(x, self.margin_y, self.width, self.height)
        
        # Popup position (centered on screen)
        self.popup_rect = pygame.Rect(
            (sw - self.popup_width) // 2,
            (sh - self.popup_height) // 2,
            self.popup_width,
            self.popup_height
        )
        
        # Calculate button positions within popup
        center_x = self.popup_rect.centerx
        center_y = self.popup_rect.centery
        
        # Restart button (top) - with 20px additional top margin
        self.restart_button_rect = pygame.Rect(
            center_x - self.popup_button_width // 2,
            center_y - self.popup_button_height - self.popup_button_spacing // 2 + 20,
            self.popup_button_width,
            self.popup_button_height
        )
        
        # Quit button (bottom) - adjusted to maintain spacing
        self.quit_button_rect = pygame.Rect(
            center_x - self.popup_button_width // 2,
            center_y + self.popup_button_spacing // 2 + 20,
            self.popup_button_width,
            self.popup_button_height
        )
    
    def toggle_popup(self):
        """Toggle the popup visibility."""
        self.popup_visible = not self.popup_visible
        if self.popup_visible:
            print("Settings popup opened")
        else:
            print("Settings popup closed")
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            str or None: 'quit', 'restart', or None
        """
        # Update positions in case screen changed
        try:
            self._recompute_positions()
        except Exception:
            pass
        
        if event.type == pygame.MOUSEMOTION:
            try:
                if self.popup_visible:
                    # Check hover on popup buttons
                    self.quit_button_hover = self.quit_button_rect.collidepoint(event.pos)
                    self.restart_button_hover = self.restart_button_rect.collidepoint(event.pos)
                else:
                    # Check hover on settings button
                    self.hover = self.rect.collidepoint(event.pos)
            except Exception:
                self.hover = False
                self.quit_button_hover = False
                self.restart_button_hover = False
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                if self.popup_visible:
                    # Check clicks on popup buttons
                    if self.quit_button_rect.collidepoint(event.pos):
                        self.popup_visible = False
                        return 'quit'
                    elif self.restart_button_rect.collidepoint(event.pos):
                        self.popup_visible = False
                        return 'restart'
                    # Check if clicked outside popup to close it
                    elif not self.popup_rect.collidepoint(event.pos):
                        self.popup_visible = False
                        return None
                else:
                    # Check click on settings button
                    if self.rect.collidepoint(event.pos):
                        self.toggle_popup()
                        return None
            except Exception:
                return None
        
        # Handle ESC key to close popup
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.popup_visible:
                self.popup_visible = False
                return None
        
        return None
    
    def draw_settings_icon(self):
        """Draw a gear/cog icon for settings."""
        center_x = self.rect.centerx
        center_y = self.rect.centery
        radius = min(self.width, self.height) // 3
        
        # Draw gear shape
        # Outer circle
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius, 3)
        
        # Inner circle
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius // 2, 3)
        
        # Gear teeth (8 teeth)
        import math
        num_teeth = 8
        tooth_length = radius // 2
        
        for i in range(num_teeth):
            angle = (2 * math.pi * i) / num_teeth
            start_x = center_x + int(radius * math.cos(angle))
            start_y = center_y + int(radius * math.sin(angle))
            end_x = center_x + int((radius + tooth_length) * math.cos(angle))
            end_y = center_y + int((radius + tooth_length) * math.sin(angle))
            
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (start_x, start_y), (end_x, end_y), 3)
    
    def draw_popup(self):
        """Draw the settings popup with quit and restart buttons."""
        # Draw overlay (semi-transparent background)
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)  # Semi-transparent
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup background
        popup_color = (240, 230, 220)  # Light beige
        pygame.draw.rect(self.screen, popup_color, self.popup_rect, border_radius=20)
        
        # Draw popup border
        border_color = (90, 60, 30)
        pygame.draw.rect(self.screen, border_color, self.popup_rect, 4, border_radius=20)
        
        # Draw title
        title_text = self.title_font.render("Settings", True, (60, 40, 20))
        title_rect = title_text.get_rect(centerx=self.popup_rect.centerx, 
                                         top=self.popup_rect.top + 30)
        self.screen.blit(title_text, title_rect)
        
        # Draw restart button
        restart_color = self.hover_color if self.restart_button_hover else self.color
        pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border, self.restart_button_rect, 3, border_radius=10)
        restart_text = self.button_font.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Draw quit button
        quit_color = self.hover_color if self.quit_button_hover else self.color
        pygame.draw.rect(self.screen, quit_color, self.quit_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.border, self.quit_button_rect, 3, border_radius=10)
        quit_text = self.button_font.render("Quit", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Draw hint text
        hint_text = HINT_FONT.render("Press ESC or click outside to close", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(centerx=self.popup_rect.centerx,
                                       bottom=self.popup_rect.bottom - 10)
        self.screen.blit(hint_text, hint_rect)
    
    def draw(self):
        """Draw the settings button and popup (if visible)."""
        try:
            self._recompute_positions()
        except Exception:
            pass
        
        # Draw popup if visible (drawn first so button appears on top)
        if self.popup_visible:
            self.draw_popup()
        
        # Draw settings button
        btn_color = self.hover_color if self.hover else self.color
        pygame.draw.rect(self.screen, btn_color, self.rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border, self.rect, 3, border_radius=8)
        
        # Draw settings icon (gear)
        self.draw_settings_icon()


# Example usage / testing
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Settings Button Test")
    clock = pygame.time.Clock()
    
    # Create settings button
    settings_button = SettingsButton(screen, position='right')
    
    running = True
    print("=" * 60)
    print("Settings Button Test")
    print("=" * 60)
    print("Click the settings button to open the popup")
    print("Click Restart or Quit in the popup to test")
    print("Press ESC to close popup or quit test")
    print("=" * 60)
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not settings_button.popup_visible:
                    running = False
            
            # Handle settings button events
            result = settings_button.handle_event(event)
            if result == 'quit':
                print("Quit button clicked!")
                running = False
            elif result == 'restart':
                print("Restart button clicked!")
                # In real game, would restart the game here
        
        # Draw
        screen.fill((245, 235, 220))  # Light background
        
        # Draw some example content
        font = pygame.font.SysFont('Arial', 32)
        text = font.render("Settings Button Example", True, (60, 40, 20))
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
        
        # Draw settings button
        settings_button.draw()
        
        pygame.display.flip()
    
    pygame.quit()
