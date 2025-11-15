"""
Main Game Entry Point
Integrates all game modules including the story system
"""
import pygame
import sys
import os

# Add module directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module', 'games'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module', 'settings'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module'))

# Import game modules
from game_start.game_start import GameStart
from stories import Stories
from character_select.character_select import CharacterSelect
from tutorial.tutorial import Tutorial
from board.board import Board
from ui.sound_button import SoundButton
from ui.settings_button import SettingsButton
from ui.tutorial_button import TutorialButton
from events.rock_paper_scissors.rock_paper_scissors import RockPaperScissors
from events.guess.guess import GuessGame
from game_state import game_state

# Initialize Pygame
pygame.init()

# ==================== CONFIGURATION ====================
# Screen settings
FULLSCREEN = False
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 832

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
        # Create windowed mode with specified size
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        pygame.display.set_caption("Guardian of Ayutthaya")

        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # Flow: menu -> stories -> character_select -> tutorial -> board

        # Initialize modules
        self.menu = GameStart(self.screen)
        self.character_select = CharacterSelect(self.screen)
        self.tutorial = Tutorial(self.screen)
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
        # Sound toggle button (positioned on left side with 60px padding)
        self.sound_button = SoundButton(self.screen, position='left', margin_x=70, quit_button_width=0)
        # Settings button with popup (positioned on right side) - includes quit and restart
        self.settings_button = SettingsButton(self.screen, position='left', margin_x=30)
        # Tutorial button (positioned 5px to the left of sound button, same vertical position)
        self.tutorial_button = TutorialButton(self.screen, position='left', margin_y=20)
        
        # Tutorial overlay state
        self.showing_tutorial_overlay = False
        
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Let the sound button process the event
            try:
                self.sound_button.handle_event(event)
            except Exception:
                pass
            
            # Let the settings button process the event (returns 'quit' or 'restart')
            try:
                settings_result = self.settings_button.handle_event(event)
                if settings_result == 'quit':
                    self.running = False
                    return
                elif settings_result == 'restart':
                    self.restart_game()
                    return
            except Exception:
                pass
            
            # Handle tutorial button (only on board screen)
            if self.game_state == "board" and not self.showing_tutorial_overlay:
                try:
                    if self.tutorial_button.handle_event(event):
                        # Open tutorial overlay
                        self.showing_tutorial_overlay = True
                        self.tutorial.reset()
                        self.tutorial.set_skip_returns_to_game(True)
                except Exception:
                    pass
            
            # Handle tutorial overlay events
            if self.showing_tutorial_overlay:
                if self.tutorial.handle_event(event):
                    # Tutorial finished or skipped - return to game
                    self.showing_tutorial_overlay = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_state == "stories":
                    # Manual skip
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "character_select"

            # Mouse events
            if self.game_state == "menu":
                if self.menu.handle_event(event):
                    # Start button pressed -> show stories first
                    self.stories.reset()
                    self.game_state = "stories"
            elif self.game_state == "character_select":
                result = self.character_select.handle_event(event)
                if result:
                    if result.get('confirmed'):
                        # Character selected - save to global state and go to tutorial
                        game_state.set_character(
                            result['character_id'],
                            result['character_data']
                        )
                        # Reload the character image in the board
                        self.board.reload_character()
                        # Reset tutorial before showing
                        self.tutorial.reset()
                        self.game_state = "tutorial"
                    elif result.get('cancelled'):
                        # Go back to menu
                        self.game_state = "menu"
            elif self.game_state == "tutorial":
                if self.tutorial.handle_event(event):
                    # Tutorial finished, go to board
                    self.game_state = "board"
            elif self.game_state == "board":
                board_result = self.board.handle_event(event)
                if isinstance(board_result, dict):
                    if board_result.get('result') == 'endgame-choice':
                        choice = board_result.get('choice')
                        if choice == 'restart':
                            self.restart_game()
                        elif choice == 'quit':
                            self.running = False
                        return
                elif board_result:
                    # Launch the rock-paper-scissors mini-game (blocking until finished)
                    # Use block number 17
                    self.run_rock_paper_scissors(17)
            elif self.game_state == "stories":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "character_select"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    advanced = self.stories.advance_story(self.clock)
                    if not advanced and self.stories.finished:
                        self.game_state = "character_select"
            # (quit handled by settings_button.handle_event)
            # No VIDEORESIZE handling needed
                    
    def update(self):
        """Update game logic"""
        # Update sound button (checks if music needs to restart)
        try:
            self.sound_button.update()
        except Exception:
            pass
        
        if self.game_state == "board":
            try:
                self.board.update()
            except Exception as exc:
                print(f"Warning: Board update failed: {exc}")
        elif self.game_state == "character_select":
            # Update character selection animations
            self.character_select.update()
        elif self.game_state == "stories":
            # Check if it's time to auto-advance
            if self.stories.should_advance():
                advanced = self.stories.advance_story(self.clock)
                if not advanced and self.stories.finished:
                    self.game_state = "character_select"

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
                # Allow settings button to work while in mini-game
                try:
                    settings_result = self.settings_button.handle_event(event)
                    if settings_result == 'quit':
                        self.running = False
                        running_rps = False
                        break
                    elif settings_result == 'restart':
                        self.restart_game()
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
            # Draw settings button on top
            try:
                self.settings_button.draw()
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
                # Allow settings button to work while in mini-game
                try:
                    settings_result = self.settings_button.handle_event(event)
                    if settings_result == 'quit':
                        self.running = False
                        running_guess = False
                        break
                    elif settings_result == 'restart':
                        self.restart_game()
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
            # Draw settings button on top
            try:
                self.settings_button.draw()
            except Exception:
                pass
            pygame.display.flip()

        # After mini-game returns, optionally handle rewards or state
        return
                    
    def draw(self):
        """Draw the current game state"""
        if self.game_state == "menu":
            self.menu.draw()
        elif self.game_state == "character_select":
            self.character_select.draw()
        elif self.game_state == "tutorial":
            self.tutorial.draw()
        elif self.game_state == "board":
            self.screen.fill(BLACK)
            self.board.draw()
            # Draw tutorial button on board
            try:
                self.tutorial_button.draw()
            except Exception:
                pass
            # Draw tutorial overlay if showing
            if self.showing_tutorial_overlay:
                self.tutorial.draw()
        elif self.game_state == "stories":
            self.stories.draw_story(self.stories.current_story)

            # Draw instruction (bigger font, lower position)
            instruction_text = self.instruction_font.render(
                "SPACE or CLICK to skip", True, WHITE)
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

        # Draw sound button (always on top)
        try:
            self.sound_button.draw()
        except Exception:
            pass
        
        # Draw settings button (always on top, right side)
        try:
            self.settings_button.draw()
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
    
    def restart_game(self):
        """Restart the game by resetting all components to initial state"""
        print("Restarting game...")
        
        # Reset game state
        self.game_state = "menu"
        
        # Reset global game state
        game_state.reset()
        
        # Reinitialize modules
        self.menu = GameStart(self.screen)
        self.character_select = CharacterSelect(self.screen)
        self.tutorial.reset()
        self.board = Board(self.screen)
        self.stories.reset()
        
        # Reset tutorial overlay state
        self.showing_tutorial_overlay = False
        
        print("Game restarted successfully!")
        
    def quit(self):
        """Clean up and quit"""
        # Cleanup sound
        try:
            self.sound_button.cleanup()
        except Exception:
            pass
        
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
