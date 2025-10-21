"""
Stories Module - Class-based story management system
"""
import pygame
import os


class Stories:
    """
    Stories class to manage and display story sequences
    Handles loading, displaying, and transitioning between story images
    """
    
    def __init__(self, screen, max_stories=8, display_time=3000, fade_speed=5, colors=None, fps=60):
        """
        Initialize the Stories system
        
        Args:
            screen: Pygame display surface
            max_stories: Maximum number of stories (default 8)
            display_time: Time to display each story in milliseconds (default 3000)
            fade_speed: Speed of fade transitions (default 5)
            colors: Dictionary with 'BLACK' and 'WHITE' keys (optional)
            fps: Frame rate (default 60)
        """
        self.screen = screen
        self.max_stories = max_stories
        self.story_display_time = display_time
        self.fade_speed = fade_speed
        self.fps = fps
        
        # Colors - use provided or defaults
        if colors:
            self.BLACK = colors.get('BLACK', (0, 0, 0))
            self.WHITE = colors.get('WHITE', (255, 255, 255))
        else:
            self.BLACK = (0, 0, 0)
            self.WHITE = (255, 255, 255)
        
        # Screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Story state
        self.current_story = 1
        self.story_images = {}
        self.last_story_change = pygame.time.get_ticks()
        
        # Load story images
        self.load_story_images()
    
    def load_story_images(self):
        """Load and scale story images based on current screen size"""
        self.story_images = {}
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        for i in range(1, self.max_stories + 1):
            img_path = f"assets/stories/story-{i}.png"
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                # Scale image to fit screen while maintaining aspect ratio
                img_rect = img.get_rect()
                scale_factor = min(
                    self.screen_width / img_rect.width,
                    self.screen_height / img_rect.height
                )
                new_width = int(img_rect.width * scale_factor)
                new_height = int(img_rect.height * scale_factor)
                self.story_images[i] = pygame.transform.scale(img, (new_width, new_height))
            else:
                print(f"Warning: {img_path} not found")
                # Create a placeholder surface
                placeholder = pygame.Surface((self.screen_width, self.screen_height))
                placeholder.fill((50, 50, 50))
                self.story_images[i] = placeholder
    
    def draw_story(self, story_num, alpha=255):
        """Draw the current story image with optional transparency"""
        self.screen.fill(self.BLACK)
        
        if story_num in self.story_images:
            img = self.story_images[story_num].copy()
            img.set_alpha(alpha)
            
            # Center the image
            img_rect = img.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(img, img_rect)
    
    def fade_transition(self, from_story, to_story, clock):
        """Create a fade transition between two stories"""
        for alpha in range(0, 256, self.fade_speed):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.K_ESCAPE:
                    return False
            
            # Draw old story fading out
            self.screen.fill(self.BLACK)
            if from_story in self.story_images:
                img = self.story_images[from_story].copy()
                img.set_alpha(255 - alpha)
                img_rect = img.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(img, img_rect)
            
            # Draw new story fading in
            if to_story in self.story_images:
                img = self.story_images[to_story].copy()
                img.set_alpha(alpha)
                img_rect = img.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(img, img_rect)
            
            pygame.display.flip()
            clock.tick(self.fps)
        
        return True
    
    def advance_story(self, clock):
        """Advance to the next story"""
        next_story = self.current_story + 1 if self.current_story < self.max_stories else 1
        
        if self.fade_transition(self.current_story, next_story, clock):
            self.current_story = next_story
            self.last_story_change = pygame.time.get_ticks()
            return True
        return False
    
    def should_advance(self):
        """Check if enough time has passed"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_story_change > self.story_display_time
    
    def reset_timer(self):
        """Reset the story timer"""
        self.last_story_change = pygame.time.get_ticks()
    
    def reset(self):
        """Reset to first story"""
        self.current_story = 1
        self.reset_timer()
