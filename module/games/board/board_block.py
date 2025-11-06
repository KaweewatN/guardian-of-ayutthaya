"""
Board Block System
Creates a 6x5 grid (30 blocks on board 1, continuing to board 2)
Manages block positions and character movement between blocks
"""
import importlib.util
import os
import sys
from typing import Optional

import pygame

from block_scenes_config import get_block_scene_sequence
from scene_viewer import SceneViewer

# Add module directory to path for game_state import
_MODULE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _MODULE_BASE not in sys.path:
    sys.path.insert(0, _MODULE_BASE)

from game_state import game_state

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import TEXT_FONT_BOLD


_EVENTS_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'events'))


def _load_event_class(module_name: str, relative_path: str, class_name: str) -> Optional[type]:
    """Safely load an event class without colliding with stdlib modules."""
    if _EVENTS_BASE not in sys.path:
        sys.path.insert(0, _EVENTS_BASE)

    module_path = os.path.join(_EVENTS_BASE, *relative_path.split('/'))
    if not os.path.exists(module_path):
        print(f"Warning: Event module not found at {module_path}")
        return None

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        print(f"Warning: Unable to load spec for {module_name}")
        return None

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    except Exception as exc:  # pragma: no cover - runtime guard
        print(f"Warning: Failed to import {module_name}: {exc}")
        return None

    cls = getattr(module, class_name, None)
    if cls is None:
        print(f"Warning: {class_name} not found in {module_name}")
        return None

    return cls


MathEvent = _load_event_class('events.math.math', 'math/math.py', 'MathEvent')
RockPaperScissors = _load_event_class(
    'events.rock_paper_scissors.rock_paper_scissors',
    'rock_paper_scissors/rock_paper_scissors.py',
    'RockPaperScissors'
)
GuessGame = _load_event_class('events.guess.guess', 'guess/guess.py', 'GuessGame')


class BoardBlock:
    """
    Board block system with 6 columns and 5 rows.
    - Board 1 (board-block-1): Blocks 1-30
    - Board 2 (board-block-2): Blocks 31-60
    - Dimension: 860 × 470
    - Layout: 6 columns × 5 rows per board
    
    Game Events:
    - Math Game: Blocks 3, 11, 20, 28, 37, 43, 49, 54
    - Rock Paper Scissors: Blocks 2, 6, 17, 40, 46, 57
    - Guess Game: Blocks 9, 14, 31, 51
    """
    
    # Board configuration
    BOARD_WIDTH = 910
    BOARD_HEIGHT = 520
    COLS = 6
    ROWS = 5
    BLOCKS_PER_BOARD = COLS * ROWS  # 30 blocks
    
    def __init__(self, screen, start_block=1):
        """
        Initialize the board block system.
        
        Args:
            screen: Pygame display surface
            start_block: Starting block number (default 1)
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Current block position (1-indexed)
        self.current_block = start_block
        
        # Load board images
        self.board_images = {}
        self.load_board_images()
        
        # Block visual settings (must be set before generate_blocks_info)
        self.block_size = self.calculate_block_size()
        
        # Calculate block positions and metadata
        self.blocks_info = self.generate_blocks_info()
        
        # Character position (will be set based on current_block)
        self.character_pos = None
        self.character_image = None
        self.load_character_image()
        self.update_character_position()
        
        # Scene viewer for block scenes
        self.scene_viewer = None
        self.viewing_scenes = False
        self.scene_delay_timer = 0
        self.scene_delay_duration = 2000  # 1 second delay before showing scenes (in milliseconds)
        self.pending_scenes = False
        self.cached_scenes = None
        
        # Game event system
        self.current_game = None
        self.playing_game = False
        
        # Define game event blocks
        self.math_blocks = [3, 11, 20, 28, 37, 43, 49, 54]
        self.rps_blocks = [6, 17, 2, 40, 46, 57]  # Rock Paper Scissors (fixed: removed 25, added 2)
        self.guess_blocks = [9, 14, 31, 51]
        
        # Show scenes for the starting block
        self.show_block_scenes()
        
    def load_board_images(self):
        """Load board-block-1 and board-block-2 from assets/core folder."""
        assets_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 
            'assets', 'core'
        )
        
        for board_num in [1, 2]:
            img_path = os.path.join(assets_path, f'board-block-{board_num}.png')
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path)
                    # Scale to specified dimensions
                    self.board_images[board_num] = pygame.transform.scale(
                        img, 
                        (self.BOARD_WIDTH, self.BOARD_HEIGHT)
                    )
                except Exception as e:
                    print(f"Error loading board-block-{board_num}.png: {e}")
                    self.board_images[board_num] = None
            else:
                print(f"Warning: board-block-{board_num}.png not found at {img_path}")
                self.board_images[board_num] = None
    
    def load_character_image(self):
        """Load selected character image from assets/main-character folder using global game state."""
        assets_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 
            'assets', 'main-character'
        )
        
        # Get selected character image from global game state
        character_image_name = game_state.get_character_image()
        char_path = os.path.join(assets_path, character_image_name)
        
        if os.path.exists(char_path):
            try:
                img = pygame.image.load(char_path).convert_alpha()
                # Scale character to fit block size nicely (about 80% of block size)
                block_width, block_height = self.block_size
                char_size = int(min(block_width, block_height) * 0.8)
                # Use smooth scaling for better quality
                self.character_image = pygame.transform.smoothscale(img, (char_size, char_size))
                print(f"Loaded character: {character_image_name}")
            except Exception as e:
                print(f"Error loading {character_image_name}: {e}")
                self.character_image = None
        else:
            print(f"Warning: {character_image_name} not found at {char_path}")
            self.character_image = None
    
    def reload_character_image(self):
        """Reload character image after character selection. Call this when character changes."""
        print(f"Reloading character image from game state...")
        self.load_character_image()
    
    def calculate_block_size(self):
        """Calculate the size of each block based on board dimensions and grid."""
        block_width = self.BOARD_WIDTH // self.COLS
        block_height = self.BOARD_HEIGHT // self.ROWS
        return (block_width, block_height)
    
    def generate_blocks_info(self):
        """
        Generate position and metadata for all blocks.
        
        Layout pattern (row by row, left to right):
        Row 1: Block 1-6
        Row 2: Block 7-12
        Row 3: Block 13-18
        Row 4: Block 19-24
        Row 5: Block 25-30 (Board 1)
        
        Then continues to Board 2:
        Row 1: Block 31-36
        Row 2: Block 37-42
        ...and so on
        
        Returns:
            dict: {block_number: {board, row, col, x, y, next, prev}}
        """
        blocks = {}
        total_blocks = self.BLOCKS_PER_BOARD * 2  # 60 blocks total (2 boards)
        
        for block_num in range(1, total_blocks + 1):
            # Determine which board (1 or 2)
            if block_num <= self.BLOCKS_PER_BOARD:
                board = 1
                offset = 0
            else:
                board = 2
                offset = self.BLOCKS_PER_BOARD
            
            # Calculate row and column (0-indexed for calculation)
            block_index = (block_num - 1) % self.BLOCKS_PER_BOARD
            row = block_index // self.COLS
            col = block_index % self.COLS
            
            # Calculate position on board (relative to board top-left)
            block_width, block_height = self.block_size
            x = col * block_width + block_width // 2  # Center of block
            y = row * block_height + block_height // 2  # Center of block
            
            # Determine next and previous blocks
            next_block = block_num + 1 if block_num < total_blocks else None
            prev_block = block_num - 1 if block_num > 1 else None
            
            blocks[block_num] = {
                'board': board,
                'row': row + 1,  # 1-indexed for user reference
                'col': col + 1,  # 1-indexed for user reference
                'x': x,
                'y': y,
                'next': next_block,
                'prev': prev_block
            }
        
        return blocks
    
    def get_current_board(self):
        """Get the current board number based on current block."""
        if self.current_block in self.blocks_info:
            return self.blocks_info[self.current_block]['board']
        return 1
    
    def get_board_top_left(self):
        """
        Calculate the top-left position to draw the current board on screen.
        Places the board with 30px left padding and 170px top padding.
        """
        x = 30  # Left padding
        y = 230  # Top padding
        return (x, y)
    
    def update_character_position(self):
        """Update character position based on current_block."""
        if self.current_block in self.blocks_info:
            block_info = self.blocks_info[self.current_block]
            board_x, board_y = self.get_board_top_left()
            
            # Character position = board position + block offset
            self.character_pos = (
                board_x + block_info['x'],
                board_y + block_info['y']
            )
    
    def move_forward(self, show_scenes=True):
        """
        Move character to the next block.
        
        Args:
            show_scenes: Whether to show scenes for the new block (default: True)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.current_block in self.blocks_info:
            next_block = self.blocks_info[self.current_block]['next']
            if next_block:
                self.current_block = next_block
                self.update_character_position()
                # Show scenes for the new block only if requested
                if show_scenes:
                    self.show_block_scenes()
                return True
        return False
    
    def move_backward(self, show_scenes=True):
        """
        Move character to the previous block.
        
        Args:
            show_scenes: Whether to show scenes for the new block (default: True)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.current_block in self.blocks_info:
            prev_block = self.blocks_info[self.current_block]['prev']
            if prev_block:
                self.current_block = prev_block
                self.update_character_position()
                # Show scenes for the new block only if requested
                if show_scenes:
                    self.show_block_scenes()
                return True
        return False
    
    def move_to_block(self, block_number):
        """
        Move character to a specific block number.
        
        Args:
            block_number: Target block (1-60)
            
        Returns:
            bool: True if successful, False if invalid block
        """
        if block_number in self.blocks_info:
            self.current_block = block_number
            self.update_character_position()
            # Show scenes for the new block
            self.show_block_scenes()
            return True
        return False
    
    def show_block_scenes(self):
        """Show the scene sequence for the current block with delay."""
        scenes = get_block_scene_sequence(self.current_block)
        if scenes:
            # Start the delay timer
            self.pending_scenes = True
            self.scene_delay_timer = pygame.time.get_ticks()
            self.cached_scenes = scenes
    
    def start_pending_scenes(self):
        """Actually start showing the scenes after the delay."""
        if self.cached_scenes:
            self.scene_viewer = SceneViewer(self.screen, self.cached_scenes, scene_duration=5000)
            self.viewing_scenes = True
            self.pending_scenes = False
            self.cached_scenes = None
    
    def check_and_start_game_event(self):
        """Check if current block triggers a game event and start it."""
        if self.current_block in self.math_blocks:
            if MathEvent is None:
                print(f"Warning: MathEvent unavailable for block {self.current_block}")
                return
            self.current_game = MathEvent(self.screen, self.current_block)
            self.playing_game = True
            return

        if self.current_block in self.rps_blocks:
            if RockPaperScissors is None:
                print(f"Warning: RockPaperScissors unavailable for block {self.current_block}")
                return
            self.current_game = RockPaperScissors(self.screen, self.current_block)
            self.playing_game = True
            return

        if self.current_block in self.guess_blocks:
            if GuessGame is None:
                print(f"Warning: GuessGame unavailable for block {self.current_block}")
                return
            self.current_game = GuessGame(self.screen, self.current_block)
            self.playing_game = True
    
    def update(self):
        """Update board state. Call this every frame."""
        # Check if we're waiting to show scenes
        if self.pending_scenes:
            current_time = pygame.time.get_ticks()
            if current_time - self.scene_delay_timer >= self.scene_delay_duration:
                # Delay is over, start showing scenes
                self.start_pending_scenes()
        
        # Update scene viewer if active
        if self.viewing_scenes and self.scene_viewer:
            self.scene_viewer.update()
            # Check if scene viewing is finished
            if self.scene_viewer.is_finished:
                self.viewing_scenes = False
                self.scene_viewer = None
                # After scenes finish, check if we should start a game event
                self.check_and_start_game_event()
    
    def get_block_info(self, block_number=None):
        """
        Get information about a specific block.
        
        Args:
            block_number: Block to query (default: current block)
            
        Returns:
            dict: Block information or None if invalid
        """
        if block_number is None:
            block_number = self.current_block
        return self.blocks_info.get(block_number)
    
    def draw(self):
        """Draw the current board and character position."""
        # If playing a game event, let game draw instead
        if self.playing_game and self.current_game:
            self.current_game.draw()
            return
        
        # If viewing scenes, let scene viewer draw instead
        if self.viewing_scenes and self.scene_viewer:
            self.scene_viewer.draw()
            return
        
        # Get current board
        current_board = self.get_current_board()
        board_img = self.board_images.get(current_board)
        
        # Get board position
        board_x, board_y = self.get_board_top_left()
        
        # Draw board background
        if board_img:
            self.screen.blit(board_img, (board_x, board_y))
        else:
            # Fallback: draw a rectangle if image not loaded
            pygame.draw.rect(
                self.screen, 
                (200, 180, 150), 
                (board_x, board_y, self.BOARD_WIDTH, self.BOARD_HEIGHT)
            )
        
        # Draw character (elephant image or fallback to red circle)
        if self.character_pos:
            if self.character_image:
                # Draw elephant image centered on position
                char_rect = self.character_image.get_rect(center=self.character_pos)
                self.screen.blit(self.character_image, char_rect)
            else:
                # Fallback: draw a red circle if image not loaded
                pygame.draw.circle(
                    self.screen,
                    (255, 0, 0),  # Red color
                    self.character_pos,
                    15  # Radius
                )
                # Draw a white outline
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    self.character_pos,
                    15,
                    3  # Outline width
                )
        
        # Optional: Draw block number text
        self.draw_block_info()
    
    def draw_block_info(self):
        """Draw current block number above the board-block."""
        # Use centralized font system
        font = TEXT_FONT_BOLD
        
        # Get board position to place info above it
        board_x, board_y = self.get_board_top_left()
        
        # Only show block number
        info_text = f"Block: {self.current_block}"
        text_surf = font.render(info_text, True, (0, 0, 0))
        
        # Position above the board (20px above board top)
        text_rect = text_surf.get_rect()
        text_rect.left = board_x + 10
        text_rect.bottom = board_y - 10

        self.screen.blit(text_surf, text_rect)
    
    def draw_grid_overlay(self):
        """Draw grid lines for debugging/visualization (optional)."""
        board_x, board_y = self.get_board_top_left()
        block_width, block_height = self.block_size
        
        # Draw vertical lines
        for col in range(self.COLS + 1):
            x = board_x + col * block_width
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (x, board_y),
                (x, board_y + self.BOARD_HEIGHT),
                1
            )
        
        # Draw horizontal lines
        for row in range(self.ROWS + 1):
            y = board_y + row * block_height
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (board_x, y),
                (board_x + self.BOARD_WIDTH, y),
                1
            )
    
    def handle_event(self, event):
        """
        Handle keyboard input for testing movement.
        
        Args:
            event: Pygame event
            
        Returns:
            dict: Movement result or None
        """
        # If playing a game event, forward events to game
        if self.playing_game and self.current_game:
            result = self.current_game.handle_event(event)
            if result is not None:
                # Game finished, return to board
                print(f"Game finished with result: {result}")
                self.playing_game = False
                self.current_game = None
            return None
        
        # If viewing scenes, forward events to scene viewer
        if self.viewing_scenes and self.scene_viewer:
            finished = self.scene_viewer.handle_event(event)
            if finished:
                self.viewing_scenes = False
                self.scene_viewer = None
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                # Move forward
                if self.move_forward():
                    return {'action': 'move_forward', 'block': self.current_block}
            elif event.key == pygame.K_LEFT:
                # Move backward
                if self.move_backward():
                    return {'action': 'move_backward', 'block': self.current_block}
        
        return None
    
    def get_all_blocks_info(self):
        """
        Get information about all blocks.
        Useful for exporting or debugging.
        
        Returns:
            dict: Complete blocks information
        """
        return self.blocks_info.copy()


# Example usage / testing
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Board Block Test")
    clock = pygame.time.Clock()
    
    # Create board block system
    board_block = BoardBlock(screen, start_block=1)
    
    running = True
    show_grid = False
    
    print("=" * 60)
    print("Board Block System - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  RIGHT/SPACE: Move forward")
    print("  LEFT: Move backward")
    print("  G: Toggle grid overlay")
    print("  ESC: Quit")
    print("=" * 60)
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                    print(f"Grid overlay: {'ON' if show_grid else 'OFF'}")
                else:
                    result = board_block.handle_event(event)
                    if result:
                        info = board_block.get_block_info()
                        print(f"Moved to Block {result['block']} - Board {info['board']}, Row {info['row']}, Col {info['col']}")
        
        # Update board state (handles auto-transition of scenes)
        board_block.update()
        
        # Draw
        screen.fill((50, 50, 50))
        board_block.draw()
        
        if show_grid:
            board_block.draw_grid_overlay()
        
        pygame.display.flip()
    
    pygame.quit()
