"""
Sound Toggle Button
Manages background music playback and provides a toggle UI
"""
import pygame
import os


class SoundButton:
    """
    Reusable sound toggle button UI element.
    
    Controls background music playback with visual feedback.
    
    Usage:
        sb = SoundButton(screen)
        # inside event loop:
        sb.handle_event(event)
        # in update loop:
        sb.update()
        # after drawing the scene:
        sb.draw()
    """
    
    def __init__(self, screen, width=50, height=50, margin_x=20, margin_y=20,
                 color=(139, 90, 43), hover_color=(180, 120, 60),
                 border=(90, 60, 30), position='left', quit_button_width=110):
        """
        Initialize the sound button.
        
        Args:
            screen: Pygame display surface
            width: Button width in pixels
            height: Button height in pixels
            margin_x: Base margin from edge (will be adjusted for position)
            margin_y: Margin from top
            color: Normal button color (RGB)
            hover_color: Button color when hovered (RGB)
            border: Border color (RGB)
            position: 'left' or 'right' - position on screen
            quit_button_width: Width of quit button for spacing calculation
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
        self.quit_button_width = quit_button_width
        self.hover = False
        
        # Sound state
        self.sound_on = True
        self.music_loaded = False
        
        # Load and start music
        self.load_music()
        
        # Load icon images (if available)
        self.icon_on = None
        self.icon_off = None
        self.load_icons()
        
        # Calculate position
        self._recompute_rect()
    
    def load_music(self):
        """Load and play the background music."""
        music_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assets', 'audio',
            'theme-soundtrack.mp3'
        )
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)  # 50% volume
                pygame.mixer.music.play(-1)  # Loop indefinitely (-1 means infinite loop)
                self.music_loaded = True
                self.sound_on = True
                print(f"Loaded background music: theme-soundtrack.mp3")
            except Exception as e:
                print(f"Error loading music: {e}")
                self.music_loaded = False
        else:
            print(f"Warning: theme-soundtrack.mp3 not found at {music_path}")
            self.music_loaded = False
    
    def load_icons(self):
        """Load sound on/off icons from assets folder."""
        icon_path_on = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assets', 'core',
            'sound_on.png'
        )
        icon_path_off = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assets', 'core',
            'sound_off.png'
        )
        
        # Try to load sound_on icon
        if os.path.exists(icon_path_on):
            try:
                img = pygame.image.load(icon_path_on).convert_alpha()
                self.icon_on = pygame.transform.smoothscale(img, (int(self.width * 0.6), int(self.height * 0.6)))
            except Exception as e:
                print(f"Error loading sound_on icon: {e}")
        
        # Try to load sound_off icon
        if os.path.exists(icon_path_off):
            try:
                img = pygame.image.load(icon_path_off).convert_alpha()
                self.icon_off = pygame.transform.smoothscale(img, (int(self.width * 0.6), int(self.height * 0.6)))
            except Exception as e:
                print(f"Error loading sound_off icon: {e}")
    
    def _recompute_rect(self):
        """Calculate button position based on screen size and quit button."""
        sw = self.screen.get_width()
        
        if self.position == 'left':
            # Position to the right of the quit button with 30px margin
            x = self.margin_x + self.quit_button_width + 30
            self.rect = pygame.Rect(
                x,
                self.margin_y,
                self.width,
                self.height,
            )
        else:
            # Position on right side
            self.rect = pygame.Rect(
                sw - self.margin_x - self.width,
                self.margin_y,
                self.width,
                self.height,
            )
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        if not self.music_loaded:
            return
        
        self.sound_on = not self.sound_on
        
        if self.sound_on:
            pygame.mixer.music.unpause()
            print("Music: ON")
        else:
            pygame.mixer.music.pause()
            print("Music: OFF")
    
    def update(self):
        """Update button state. Call this every frame."""
        # Check if music has ended (shouldn't happen with -1 loop, but just in case)
        if self.music_loaded and self.sound_on:
            if not pygame.mixer.music.get_busy():
                # Music stopped, restart it
                pygame.mixer.music.play(-1)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            bool: True if the button was clicked, False otherwise
        """
        # Update rect in case screen changed
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
                    self.toggle_sound()
                    return True
            except Exception:
                return False
        
        return False
    
    def draw_icon(self):
        """Draw the appropriate icon (sound on or off)."""
        icon = self.icon_on if self.sound_on else self.icon_off
        
        if icon:
            # Center icon in button
            icon_rect = icon.get_rect(center=self.rect.center)
            self.screen.blit(icon, icon_rect)
        else:
            # Fallback: draw simple shapes if icons not available
            center_x = self.rect.centerx
            center_y = self.rect.centery
            
            if self.sound_on:
                # Draw speaker shape (sound on)
                # Triangle for speaker
                points = [
                    (center_x - 10, center_y - 8),
                    (center_x - 10, center_y + 8),
                    (center_x - 2, center_y + 4),
                    (center_x - 2, center_y - 4)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 255), points)
                
                # Sound waves
                pygame.draw.arc(self.screen, (255, 255, 255), 
                              (center_x + 2, center_y - 6, 8, 12), -0.5, 0.5, 2)
                pygame.draw.arc(self.screen, (255, 255, 255), 
                              (center_x + 6, center_y - 10, 12, 20), -0.5, 0.5, 2)
            else:
                # Draw speaker with X (sound off)
                # Triangle for speaker
                points = [
                    (center_x - 10, center_y - 8),
                    (center_x - 10, center_y + 8),
                    (center_x - 2, center_y + 4),
                    (center_x - 2, center_y - 4)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 255), points)
                
                # X mark
                pygame.draw.line(self.screen, (255, 100, 100), 
                               (center_x + 4, center_y - 6), 
                               (center_x + 12, center_y + 6), 3)
                pygame.draw.line(self.screen, (255, 100, 100), 
                               (center_x + 4, center_y + 6), 
                               (center_x + 12, center_y - 6), 3)
    
    def draw(self):
        """Draw the sound button on the screen."""
        try:
            self._recompute_rect()
        except Exception:
            pass
        
        # Choose button color based on hover state
        btn_color = self.hover_color if self.hover else self.color
        
        # Draw button background
        pygame.draw.rect(self.screen, btn_color, self.rect, border_radius=8)
        
        # Draw button border
        pygame.draw.rect(self.screen, self.border, self.rect, 3, border_radius=8)
        
        # Draw icon
        self.draw_icon()
    
    def cleanup(self):
        """Stop and cleanup music. Call this when closing the game."""
        if self.music_loaded:
            pygame.mixer.music.stop()
