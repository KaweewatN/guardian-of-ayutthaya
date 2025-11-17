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

# Import the Dice system and alphabet deck widget
try:
    from board.dice import Dice
    from board.alphabet_deck import AlphabetDeck
except ImportError:
    try:
        from dice import Dice
        from alphabet_deck import AlphabetDeck
    except ImportError:
        # Fallback: add current directory to path
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from dice import Dice
        from alphabet_deck import AlphabetDeck


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

        # Alphabet deck HUD
        try:
            self.alphabet_deck = AlphabetDeck(screen, self.dice)
        except Exception as exc:
            print(f"Warning: AlphabetDeck failed to initialize: {exc}")
            self.alphabet_deck = None
        
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
        self.nav_arrow_size = 48
        self.nav_arrow_spacing = 110
        self.nav_vertical_offset = 35
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
        if self.alphabet_deck:
            self.alphabet_deck.update()
    
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
                if self.alphabet_deck:
                    self.alphabet_deck.draw()
                self.dice.draw()
            self._draw_board_navigation()
            
            # Draw alphabet deck on top of everything if expanded
            if self.alphabet_deck and self.alphabet_deck.is_expanded:
                self.alphabet_deck.draw()
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

        # Handle alphabet deck events first (if expanded, it should capture all events)
        if self.alphabet_deck:
            if self.alphabet_deck.is_expanded:
                # When expanded, alphabet deck handles all events
                handled = self.alphabet_deck.handle_event(event)
                if handled:
                    return None
                # Even if not handled, don't pass events to other components when deck is expanded
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    return None
            else:
                # When not expanded, only handle events on the deck area
                self.alphabet_deck.handle_event(event)

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
                    return result
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

        radius = rect.width // 2
        center = (rect.width // 2, rect.height // 2)

        if enabled:
            base_color = (214, 189, 146)
            base_hover_color = (233, 206, 166)
            rim_color = (124, 94, 62)
            arrow_color = (122, 96, 60) if hover else (108, 82, 52)
            arrow_outline = (70, 50, 32)
            highlight_alpha = 85 if hover else 60
            shadow_alpha = 90
        else:
            base_color = (140, 126, 111)
            base_hover_color = base_color
            rim_color = (110, 98, 85)
            arrow_color = (184, 170, 154)
            arrow_outline = (150, 140, 126)
            highlight_alpha = 0
            shadow_alpha = 60

        fill_color = base_hover_color if hover else base_color

        pygame.draw.circle(button_surface, fill_color, center, radius - 1)
        pygame.draw.circle(button_surface, rim_color, center, radius - 1, 2)

        if highlight_alpha:
            highlight_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            highlight_radius = max(radius - 8, 4)
            highlight_center = (center[0], center[1] - radius // 3)
            pygame.draw.circle(
                highlight_surface,
                (255, 255, 255, highlight_alpha),
                highlight_center,
                highlight_radius
            )
            button_surface.blit(highlight_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        arrow_radius = radius * 0.86
        sign = -1 if direction == 'left' else 1
        points = [
            (int(center[0] - sign * arrow_radius * 0.42), int(center[1] - arrow_radius * 0.45)),
            (int(center[0] + sign * arrow_radius * 0.10), int(center[1] - arrow_radius * 0.45)),
            (int(center[0] + sign * arrow_radius * 0.60), int(center[1])),
            (int(center[0] + sign * arrow_radius * 0.10), int(center[1] + arrow_radius * 0.45)),
            (int(center[0] - sign * arrow_radius * 0.42), int(center[1] + arrow_radius * 0.45)),
        ]

        pygame.draw.polygon(button_surface, arrow_color, points)
        pygame.draw.lines(button_surface, arrow_outline, True, points, 2)

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

        # Intentionally omit descriptive text and backdrops so the navigation
        # arrows stand on their own and better blend with the board view.
