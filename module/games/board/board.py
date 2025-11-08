import pygame
import os
import sys

# Import the BoardBlock system
try:
    from board.board_block import BoardBlock
except ImportError:
    try:
        from board_block import BoardBlock
    except ImportError:
        # Fallback: add current directory to path
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from board_block import BoardBlock

# Import the Dice system
try:
    from board.dice import Dice
except ImportError:
    try:
        from dice import Dice
    except ImportError:
        # Fallback: add current directory to path
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from dice import Dice


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
        
        # Load board background image
        self.board_bg = None
        self.load_board_background()
        
        # Initialize the BoardBlock system (the main container)
        self.board_block = BoardBlock(screen, start_block=1)
        
        # Initialize the Dice system
        self.dice = Dice(screen, self.board_block)
        
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

        # Board navigation controls
        self.nav_arrow_size = 68
        self.nav_arrow_spacing = 140
        self.nav_vertical_offset = 45
        self.nav_font = pygame.font.SysFont('Arial', 26, bold=True)
        self.nav_sub_font = pygame.font.SysFont('Arial', 20)
        self.nav_prev_rect = pygame.Rect(0, 0, self.nav_arrow_size, self.nav_arrow_size)
        self.nav_next_rect = pygame.Rect(0, 0, self.nav_arrow_size, self.nav_arrow_size)
        self.nav_label_pos = (0, 0)
        self.nav_prev_hover = False
        self.nav_next_hover = False
        self._update_nav_layout()

        # UI mode: 'board' or 'buttons' (for testing)
        self.ui_mode = 'board'  # Start with board view

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

    def load_board_background(self):
        """Load board-bg.png from assets/core folder."""
        assets_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 
            'assets', 'core'
        )
        
        bg_path = os.path.join(assets_path, 'board-bg.png')
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path)
                # Scale to screen size
                self.board_bg = pygame.transform.scale(
                    img, 
                    (self.screen_width, self.screen_height)
                )
            except Exception as e:
                print(f"Error loading board-bg.png: {e}")
                self.board_bg = None
        else:
            print(f"Warning: board-bg.png not found at {bg_path}")
            self.board_bg = None

    def update(self):
        """Update board-related state each frame."""
        if self.active_game:
            # Mini-game handles its own loop; no board updates required
            return

        self.board_block.update()
        self.dice.update()
    
    def reload_character(self):
        """Reload character image after character selection."""
        self.board_block.reload_character_image()

    def draw(self):
        # If a mini-game is active, let it draw itself
        if self.active_game:
            try:
                self.active_game.draw()
            except Exception as e:
                print(f"Error drawing active game: {e}")
            return

        # Draw board background first
        if self.board_bg:
            self.screen.blit(self.board_bg, (0, 0))
        else:
            # Fallback to a solid color if background not loaded
            self.screen.fill((245, 235, 220))

        # Draw based on UI mode
        if self.ui_mode == 'board':
            # Draw the board block system on top of background
            self.board_block.draw()
            # Draw the dice system on the right side (only if not viewing scenes or playing games)
            if not self.board_block.viewing_scenes and not self.board_block.playing_game:
                self.dice.draw()
            self._draw_board_navigation()
        else:
            # Draw both buttons when in button mode (legacy)
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

        # Handle UI mode toggle (for testing)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.ui_mode = 'buttons' if self.ui_mode == 'board' else 'board'
            return None

        # If in board mode, forward events to board_block and dice
        if self.ui_mode == 'board':
            nav_interactive = not (self.board_block.playing_game or self.board_block.viewing_scenes)

            if not nav_interactive:
                self.nav_prev_hover = False
                self.nav_next_hover = False

            if nav_interactive and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                self._update_nav_layout()

            if nav_interactive and event.type == pygame.MOUSEMOTION:
                self._update_nav_hover(event.pos)

            if nav_interactive and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._handle_nav_click(event.pos):
                    return None

            # Check if board is ready for input
            board_ready = hasattr(self.board_block, 'is_ready_for_input') and self.board_block.is_ready_for_input()

            # Handle dice events first (dice takes priority)
            # Dice will check board state internally
            dice_result = self.dice.handle_event(event)
            if dice_result:
                # Dice action occurred
                pass
            
            # Only handle board events if dice is not active AND board is ready
            # This prevents conflicts during dice rolling/movement
            if not self.dice.is_active() and (board_ready or self.board_block.viewing_scenes or self.board_block.playing_game):
                result = self.board_block.handle_event(event)
                if result:
                    # Handle block movement results if needed
                    pass
            return None

        # No active mini-game and in buttons mode: handle button interactions
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

    def _update_nav_layout(self):
        """Position the navigation arrows below the board."""
        board_x, board_y = self.board_block.get_board_top_left()
        center_x = board_x + self.board_block.BOARD_WIDTH // 2
        nav_y = board_y + self.board_block.BOARD_HEIGHT + self.nav_vertical_offset

        self.nav_prev_rect = pygame.Rect(0, 0, self.nav_arrow_size, self.nav_arrow_size)
        self.nav_next_rect = pygame.Rect(0, 0, self.nav_arrow_size, self.nav_arrow_size)
        self.nav_prev_rect.center = (center_x - self.nav_arrow_spacing, nav_y)
        self.nav_next_rect.center = (center_x + self.nav_arrow_spacing, nav_y)
        self.nav_label_pos = (center_x, nav_y)

    def _update_nav_hover(self, mouse_pos):
        """Update hover states for navigation arrows."""
        prev_enabled = self.board_block.can_view_previous_board()
        next_enabled = self.board_block.can_view_next_board()

        self.nav_prev_hover = prev_enabled and self.nav_prev_rect.collidepoint(mouse_pos)
        self.nav_next_hover = next_enabled and self.nav_next_rect.collidepoint(mouse_pos)

    def _handle_nav_click(self, mouse_pos):
        """Handle clicks on the navigation arrows."""
        handled = False
        if self.nav_prev_rect.collidepoint(mouse_pos):
            handled = self.board_block.view_previous_board()
        elif self.nav_next_rect.collidepoint(mouse_pos):
            handled = self.board_block.view_next_board()

        if handled:
            # Reset hover state to prevent lingering highlights during animation
            self.nav_prev_hover = False
            self.nav_next_hover = False
        return handled

    def _draw_nav_button(self, rect, direction, enabled, hover):
        """Draw a circular navigation arrow button."""
        if rect.width == 0 or rect.height == 0:
            return

        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)

        if enabled:
            fill_color = (255, 255, 255, 255) if hover else (235, 235, 235, 235)
            border_color = (80, 80, 80)
            arrow_color = (40, 40, 40)
        else:
            fill_color = (110, 110, 110, 160)
            border_color = (90, 90, 90)
            arrow_color = (170, 170, 170)

        radius = rect.width // 2
        center = (rect.width // 2, rect.height // 2)
        pygame.draw.circle(button_surface, fill_color, center, radius)
        pygame.draw.circle(button_surface, border_color, center, radius, 2)

        margin = rect.width * 0.28
        top = margin
        bottom = rect.height - margin
        mid_y = rect.height / 2
        if direction == 'left':
            points = [
                (int(margin), int(mid_y)),
                (int(rect.width - margin), int(top)),
                (int(rect.width - margin), int(bottom))
            ]
        else:
            points = [
                (int(rect.width - margin), int(mid_y)),
                (int(margin), int(top)),
                (int(margin), int(bottom))
            ]

        pygame.draw.polygon(button_surface, arrow_color, points)
        self.screen.blit(button_surface, rect.topleft)

    def _draw_board_navigation(self):
        """Render navigation controls for switching between boards."""
        if self.board_block.total_board_count() <= 1:
            return

        if self.board_block.playing_game or self.board_block.viewing_scenes:
            return

        self._update_nav_layout()

        prev_enabled = self.board_block.can_view_previous_board()
        next_enabled = self.board_block.can_view_next_board()

        self._draw_nav_button(self.nav_prev_rect, 'left', prev_enabled, self.nav_prev_hover)
        self._draw_nav_button(self.nav_next_rect, 'right', next_enabled, self.nav_next_hover)

        view_board = self.board_block.get_viewed_board()
        total_boards = self.board_block.total_board_count()
        label_text = f"Board {view_board} / {total_boards}"
        label_surface = self.nav_font.render(label_text, True, (30, 30, 30))

        sub_text = f"Character Block {self.board_block.current_block}"
        sub_surface = self.nav_sub_font.render(sub_text, True, (60, 60, 60))

        label_rect = label_surface.get_rect(center=(self.nav_label_pos[0], self.nav_label_pos[1] - 32))
        sub_rect = sub_surface.get_rect(center=(self.nav_label_pos[0], self.nav_label_pos[1] + 8))

        backdrop_height = (sub_rect.bottom - label_rect.top) + 16
        backdrop_width = max(label_surface.get_width(), sub_surface.get_width()) + 40
        backdrop = pygame.Surface((backdrop_width, backdrop_height), pygame.SRCALPHA)
        pygame.draw.rect(backdrop, (255, 255, 255, 220), backdrop.get_rect(), border_radius=18)
        pygame.draw.rect(backdrop, (210, 210, 210), backdrop.get_rect(), 2, border_radius=18)

        backdrop_rect = backdrop.get_rect()
        backdrop_rect.center = (self.nav_label_pos[0], self.nav_label_pos[1] - 12)
        self.screen.blit(backdrop, backdrop_rect)

        label_rect.center = (self.nav_label_pos[0], label_rect.centery)
        sub_rect.center = (self.nav_label_pos[0], sub_rect.centery)
        self.screen.blit(label_surface, label_rect)
        self.screen.blit(sub_surface, sub_rect)
