import pygame
import os
import sys


class Board:
    def __init__(self, screen, event_block=6):
        """Board with a button that launches Rock-Paper-Scissors mini-game.

        Args:
            screen: Pygame display surface
            event_block: block number passed to the RPS game (default 6)
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        # Two buttons: Rock-Paper-Scissors (top) and Guess (below)
        self.button_rect = pygame.Rect(0, 0, 500, 100)
        self.button_rect.center = (self.screen_width // 2, self.screen_height // 2 - 60)
        self.button_rect_guess = pygame.Rect(0, 0, 500, 100)
        self.button_rect_guess.center = (self.screen_width // 2, self.screen_height // 2 + 80)
        self.button_color = (100, 200, 100)
        self.button_hover_color = (150, 255, 150)
        self.button_text_color = (0, 0, 0)
        self.button_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.button_hovered = False
        self.button_hovered_guess = False

        # Event/game wiring
        self.event_block = event_block
        self.active_game = None  # When set, a mini-game instance runs modally

        # Try to import the RockPaperScissors mini-game dynamically.
        # We add the events/rock_paper_scissors folder to sys.path so the module
        # can be imported regardless of the workspace pythonpath.
        # Try package-style import for RockPaperScissors, then fallback
        try:
            from events.rock_paper_scissors.rock_paper_scissors import RockPaperScissors
            self.RockPaperScissors = RockPaperScissors
        except Exception:
            try:
                rps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'events', 'rock_paper_scissors'))
                if rps_dir not in sys.path:
                    sys.path.insert(0, rps_dir)
                from rock_paper_scissors import RockPaperScissors
                self.RockPaperScissors = RockPaperScissors
            except Exception as e:
                print(f"Warning: could not import RockPaperScissors: {e}")
                self.RockPaperScissors = None

        # Try package-style import for GuessGame, then fallback
        try:
            from events.guess.guess import GuessGame
            self.GuessGame = GuessGame
        except Exception:
            try:
                guess_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'events', 'guess'))
                if guess_dir not in sys.path:
                    sys.path.insert(0, guess_dir)
                from guess import GuessGame
                self.GuessGame = GuessGame
            except Exception as e:
                print(f"Warning: could not import GuessGame: {e}")
                self.GuessGame = None

    def draw(self):
        # If a mini-game is active, let it draw itself
        if self.active_game:
            try:
                self.active_game.draw()
            except Exception as e:
                print(f"Error drawing active game: {e}")
            return
        # Draw both buttons when no active mini-game
        color1 = self.button_hover_color if self.button_hovered else self.button_color
        pygame.draw.rect(self.screen, color1, self.button_rect, border_radius=20)
        text1 = self.button_font.render('Play Rock-Paper-Scissors', True, self.button_text_color)
        text1_rect = text1.get_rect(center=self.button_rect.center)
        self.screen.blit(text1, text1_rect)

        color2 = self.button_hover_color if self.button_hovered_guess else self.button_color
        pygame.draw.rect(self.screen, color2, self.button_rect_guess, border_radius=20)
        text2 = self.button_font.render('Play Guess (Quiz)', True, self.button_text_color)
        text2_rect = text2.get_rect(center=self.button_rect_guess.center)
        self.screen.blit(text2, text2_rect)

    def handle_event(self, event):
        # If a mini-game is active, forward events to it and check for results
        if self.active_game:
            try:
                result = self.active_game.handle_event(event)
                # If the mini-game returns a result dict, deactivate and return it
                if result is not None:
                    self.active_game = None
                    return result
            except Exception as e:
                print(f"Error handling event in active game: {e}")
            return None

        # No active mini-game: handle button interactions
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = self.button_rect.collidepoint(event.pos)
            self.button_hovered_guess = self.button_rect_guess.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.button_hovered:
                # Launch the RPS mini-game if available
                if self.RockPaperScissors:
                    try:
                        self.active_game = self.RockPaperScissors(self.screen, self.event_block)
                        # Do not return a final result yet; the mini-game will run
                        return None
                    except Exception as e:
                        print(f"Error launching RockPaperScissors: {e}")
                        return None
                else:
                    # Fallback behavior: indicate button pressed
                    return True
            # Check guess button click
            if event.button == 1 and self.button_hovered_guess:
                if self.GuessGame:
                    try:
                        self.active_game = self.GuessGame(self.screen, self.event_block)
                        return None
                    except Exception as e:
                        print(f"Error launching GuessGame: {e}")
                        return None
                else:
                    return True
        return False
