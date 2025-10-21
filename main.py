"""
Main Game Entry Point
Integrates all game modules including the story system
"""
import pygame
import sys
import os

# Add module directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module', 'games'))

# Import game modules
from game_start.game_start import GameStart
from stories import Stories

# Initialize Pygame
pygame.init()

# ==================== CONFIGURATION ====================
# Screen settings
FULLSCREEN = True
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Frame rate
FPS = 60


# ==================== MAIN GAME CLASS ====================
class Game:
    """Main game controller"""
    
    def __init__(self):
        """Initialize the game"""
        # Setup screen
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            
        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("Story Game")
        
        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # "menu" or "playing"
        
        # Initialize modules
        # Use GameStart from module/games/game_start/game_start.py
        self.menu = GameStart(self.screen)
        
        # Use Stories class from module/games/stories/stories.py
        # Pass shared configuration to avoid duplication
        colors_config = {'BLACK': BLACK, 'WHITE': WHITE}
        self.stories = Stories(
            screen=self.screen,
            max_stories=8,
            display_time=3000,
            fade_speed=5,
            colors=colors_config,
            fps=FPS
        )
        
        # Font for instructions
        self.small_font = pygame.font.SysFont('Times New Roman', 20, bold=True)
        
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "menu"
                        self.stories.reset()
                    else:
                        self.running = False
                        
                elif event.key == pygame.K_SPACE and self.game_state == "playing":
                    # Manual skip
                    if not self.stories.advance_story(self.clock):
                        self.running = False
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "playing" and event.button == 1:
                    # Manual skip with click
                    if not self.stories.advance_story(self.clock):
                        self.running = False
                        
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen_width, self.screen_height = event.w, event.h
                self.screen = pygame.display.set_mode(
                    (self.screen_width, self.screen_height),
                    pygame.RESIZABLE
                )
                self.menu.update_screen_size(self.screen)
                self.stories.screen = self.screen
                self.stories.load_story_images()
            
            # Handle menu events
            if self.game_state == "menu":
                if self.menu.handle_event(event):
                    self.game_state = "playing"
                    self.stories.reset()
                    
    def update(self):
        """Update game logic"""
        if self.game_state == "playing":
            # Check if it's time to auto-advance
            if self.stories.should_advance():
                if not self.stories.advance_story(self.clock):
                    self.running = False
                    
    def draw(self):
        """Draw the current game state"""
        if self.game_state == "menu":
            # Draw start menu from module/games/game_start
            self.menu.draw()
        elif self.game_state == "playing":
            # Draw stories from module/games/stories - using Stories class
            self.stories.draw_story(self.stories.current_story)
            
            # Draw ESC instruction
            instruction_text = self.small_font.render("Press ESC to return to menu | SPACE or CLICK to skip", True, WHITE)
            instruction_rect = instruction_text.get_rect(
                center=(self.screen_width // 2, self.screen_height - 30)
            )
            
            # Semi-transparent background
            bg_rect = instruction_rect.inflate(20, 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height))
            s.set_alpha(128)
            s.fill(BLACK)
            self.screen.blit(s, bg_rect)
            self.screen.blit(instruction_text, instruction_rect)
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
        self.quit()
        
    def quit(self):
        """Clean up and quit"""
        pygame.quit()
        sys.exit()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    print("=" * 60)
    print("Story Game - Module Integration")
    print("=" * 60)
    print("Modules loaded:")
    print("  ✓ module/games/game_start/game_start.py - GameStart class")
    print("  ✓ module/games/stories/stories.py - Stories class")
    print("=" * 60)
    
    game = Game()
    game.run()
