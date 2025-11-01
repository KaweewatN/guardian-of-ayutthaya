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
from board.board import Board
from ui.quit_button import QuitButton
from events.rock_paper_scissors.rock_paper_scissors import RockPaperScissors
from events.guess.guess import GuessGame

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
        # Always use fullscreen with fixed size
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        pygame.display.set_caption("Story Game")

        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # Start at the menu (start button)

        # Initialize modules
        self.menu = GameStart(self.screen)
        self.board = Board(self.screen)

        colors_config = {'BLACK': BLACK, 'WHITE': WHITE}
        self.stories = Stories(
            screen=self.screen,
            max_stories=8,
            display_time=3000,
            fade_speed=5,
            colors=colors_config,
            fps=FPS
        )

        self.instruction_font = pygame.font.SysFont('Times New Roman', 24, bold=True)
        # Reusable quit button UI
        self.quit_button = QuitButton(self.screen)
        
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Let the quit button process the event (returns True if clicked)
            try:
                if self.quit_button.handle_event(event):
                    self.running = False
                    return
            except Exception:
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "stories":
                        self.game_state = "menu"
                        self.stories.reset()
                    elif self.game_state == "board":
                        self.game_state = "menu"
                    else:
                        self.running = False

                elif event.key == pygame.K_SPACE and self.game_state == "stories":
                    # Manual skip
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "board"

            # Mouse events
            if self.game_state == "menu":
                if self.menu.handle_event(event):
                    # Start button pressed -> show stories first
                    self.stories.reset()
                    self.game_state = "stories"
            elif self.game_state == "board":
                if self.board.handle_event(event):
                    # Launch the rock-paper-scissors mini-game (blocking until finished)
                    # Use block number 17
                    self.run_rock_paper_scissors(17)
            elif self.game_state == "stories":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "board"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "board"
            # (quit handled above by quit_button.handle_event)
            # No VIDEORESIZE handling needed
                    
    def update(self):
        """Update game logic"""
        if self.game_state == "stories":
            # Check if it's time to auto-advance
            if self.stories.should_advance():
                advanced = self.stories.advance_story(self.clock)
                if not advanced and self.stories.finished:
                    self.game_state = "board"

    def run_rock_paper_scissors(self, block_number=6):
        """Run the RockPaperScissors mini-game in a blocking loop until it returns a result."""
        try:
            rps = RockPaperScissors(self.screen, block_number)
        except Exception as e:
            print(f"Failed to start RockPaperScissors: {e}")
            return

        running_rps = True
        while running_rps and self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                # Allow quit button to work while in mini-game
                try:
                    if self.quit_button.handle_event(event):
                        self.running = False
                        running_rps = False
                        break
                except Exception:
                    pass

                # Pass event to mini-game
                res = rps.handle_event(event)
                if isinstance(res, dict) and res.get("result") in ("win", "lose"):
                    # Mini-game finished with a result
                    running_rps = False
                    break

            # Draw mini-game
            rps.draw()
            # Draw quit button on top
            try:
                self.quit_button.draw()
            except Exception:
                pass
            pygame.display.flip()

        # After mini-game returns, optionally handle rewards or state
        return
                    
    def run_guess_game(self, block_number=9):
        """Run the Guess mini-game in a blocking loop until it returns a result.

        Default block_number is 9 to match available guess assets.
        """
        try:
            guess = GuessGame(self.screen, block_number)
        except Exception as e:
            print(f"Failed to start GuessGame: {e}")
            return

        running_guess = True
        while running_guess and self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                # Allow quit button to work while in mini-game
                try:
                    if self.quit_button.handle_event(event):
                        self.running = False
                        running_guess = False
                        break
                except Exception:
                    pass

                # Pass event to mini-game
                res = guess.handle_event(event)
                if isinstance(res, dict) and res.get("result") in ("win", "lose"):
                    # Mini-game finished with a result
                    running_guess = False
                    break

            # Draw mini-game
            guess.draw()
            # Draw quit button on top
            try:
                self.quit_button.draw()
            except Exception:
                pass
            pygame.display.flip()

        # After mini-game returns, optionally handle rewards or state
        return
                    
    def draw(self):
        """Draw the current game state"""
        if self.game_state == "menu":
            self.menu.draw()
        elif self.game_state == "board":
            self.screen.fill(BLACK)
            self.board.draw()
        elif self.game_state == "stories":
            self.stories.draw_story(self.stories.current_story)

            # Draw ESC instruction (bigger font, lower position)
            instruction_text = self.instruction_font.render(
                "Press ESC to return to menu | SPACE or CLICK to skip", True, WHITE)
            instruction_rect = instruction_text.get_rect(
                center=(self.screen_width // 2, self.screen_height + 70)
            )

            # Semi-transparent background
            bg_rect = instruction_rect.inflate(40, 20)
            s = pygame.Surface((bg_rect.width, bg_rect.height))
            s.set_alpha(128)
            s.fill(BLACK)
            self.screen.blit(s, bg_rect)
            self.screen.blit(instruction_text, instruction_rect)

        # Draw reusable quit button (always on top)
        try:
            self.quit_button.draw()
        except Exception:
            pass

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
