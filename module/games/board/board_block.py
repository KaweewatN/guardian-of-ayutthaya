"""
Board Block System
Creates a 6x5 grid (30 blocks on board 1, continuing to board 2)
Manages block positions and character movement between blocks
"""
import importlib.util
import json
import math
import os
import sys

import pygame

from block_scenes_config import get_block_scene_sequence, get_block_jump_destination
from scene_viewer import SceneViewer
from event_image_preloader import EventImagePreloader

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
if _EVENTS_BASE not in sys.path:
    sys.path.append(_EVENTS_BASE)

_ALPHABET_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alphabet'))
if _ALPHABET_BASE not in sys.path:
    sys.path.insert(0, _ALPHABET_BASE)

# Load alphabet screens
try:  # pragma: no cover - runtime dependency
    from alphabet_win import AlphabetWin
    from alphabet_lose import AlphabetLose
except Exception as exc:  # pragma: no cover - fallback when unavailable
    print(f"Warning: alphabet screens unavailable: {exc}")
    AlphabetWin = None  # type: ignore
    AlphabetLose = None  # type: ignore

# Load game outcome screen
try:
    from game_outcome import GameOutcomeScreen
except Exception as exc:  # pragma: no cover
    print(f"Warning: GameOutcomeScreen unavailable: {exc}")
    GameOutcomeScreen = None  # type: ignore

# Load event classes using direct imports (faster than importlib)
# Add each event subdirectory to sys.path to avoid name conflicts with stdlib
# Cache loaded modules to avoid reloading
_EVENT_CLASS_CACHE = {}

def _load_event_module_once(module_name, file_path):
    """Load a module from file path, with caching to prevent reloads."""
    if module_name in _EVENT_CLASS_CACHE:
        return _EVENT_CLASS_CACHE[module_name]
    
    if not os.path.exists(file_path):
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        _EVENT_CLASS_CACHE[module_name] = module
        return module
    except Exception as exc:
        print(f"Warning: Failed to load {module_name}: {exc}")
        return None

MathEvent = None
RockPaperScissors = None
GuessGame = None
PhotoHuntGame = None
RandomCard = None

# Math Event
math_module = _load_event_module_once('math_event', os.path.join(_EVENTS_BASE, 'math', 'math.py'))
if math_module:
    MathEvent = getattr(math_module, 'MathEvent', None)

# Rock Paper Scissors
rps_module = _load_event_module_once('rps_event', os.path.join(_EVENTS_BASE, 'rock_paper_scissors', 'rock_paper_scissors.py'))
if rps_module:
    RockPaperScissors = getattr(rps_module, 'RockPaperScissors', None)

# Guess Game
guess_module = _load_event_module_once('guess_event', os.path.join(_EVENTS_BASE, 'guess', 'guess.py'))
if guess_module:
    GuessGame = getattr(guess_module, 'GuessGame', None)

# Photo Hunt
photo_module = _load_event_module_once('photo_hunt_event', os.path.join(_EVENTS_BASE, 'photo-hunt', 'photo_hunt.py'))
if photo_module:
    PhotoHuntGame = getattr(photo_module, 'PhotoHuntGame', None)

# Random Card
random_module = _load_event_module_once('random_card_event', os.path.join(_EVENTS_BASE, 'random', 'random_event.py'))
if random_module:
    RandomCard = getattr(random_module, 'RandomCard', None)


class BoardBlock:
    """
    Board block system with 6 columns and 5 rows.
    - Board 1 (board-block-1): Blocks 1-30
    - Board 2 (board-block-2): Blocks 31-60
    - Dimension: 860 × 470
    - Layout: 6 columns × 5 rows per board
    
    Game Events:
    - Math Game: Blocks 3, 11, 20, 28, 37, 43, 49, 54
    - Rock Paper Scissors: Blocks 6, 17, 40, 46, 57
    - Guess Game: Blocks 9, 14, 31, 51
    - Photo Hunt: Blocks 22, 34
    """
    
    # Board configuration
    BOARD_WIDTH = 910
    BOARD_HEIGHT = 520
    COLS = 6
    ROWS = 5
    BLOCKS_PER_BOARD = COLS * ROWS  # 30 blocks
    
    # Shared image preloader (class variable, loaded once for all instances)
    _image_preloader = None
    
    @classmethod
    def get_image_preloader(cls):
        """Get the shared image preloader instance."""
        return cls._image_preloader
    
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
        
        # Loading state - prevent interactions before everything is ready
        self.is_fully_loaded = False
        self.is_transitioning = False  # Prevents actions during state transitions
        
        # Current block position (1-indexed)
        self.current_block = start_block
        
        # Load place names from place.json
        self.place_names = self.load_place_names()
        
        # Load board images
        self.board_images = {}
        self.load_board_images()

        # Block visual settings (must be set before generate_blocks_info)
        self.block_size = self.calculate_block_size()

        # Calculate block positions and metadata
        self.blocks_info = self.generate_blocks_info()

        # Determine how many boards exist and set viewing state
        self.total_boards = max((info['board'] for info in self.blocks_info.values()), default=1)
        self.viewed_board = self.blocks_info.get(self.current_block, {}).get('board', 1)
        self.board_transition = None
        self.board_transition_duration = 420  # milliseconds for sliding transitions
        self._current_board_offsets = {}
        self._last_drawn_character_pos = None

        # Character position (will be set based on current_block)
        self.character_pos = None
        self.character_image = None
        self.load_character_image()
        self.update_character_position()
        self.character_board = self.blocks_info.get(self.current_block, {}).get('board', 1)
        
        # Scene viewer for block scenes
        self.scene_viewer = None
        self.viewing_scenes = False
        self.scene_delay_timer = 0
        self.scene_delay_duration = 1000 
        self.pending_scenes = False
        self.cached_scenes = None

        # Game event system
        self.current_game = None
        self.playing_game = False
        self.game_completed = False
        self.final_outcome = None

        # Define game event blocks
        self.math_blocks = [3, 11, 20, 28, 37, 43, 49, 54]
        self.rps_blocks = [6, 17, 25, 40, 46, 57]
        self.guess_blocks = [9, 14, 31, 51]
        self.photo_hunt_blocks = [22, 34]
        self.random_blocks = [4, 8, 12, 16, 19, 23, 26, 33, 36, 39, 42, 45, 48, 52, 56]

        # Movement animation state
        self.active_animation = None
        self.animation_duration = 260  # milliseconds per tile when animating
        self.floating_text = None
        self.wrap_effect = None

        # Initialize image preloader (once per class, shared across all instances)
        if BoardBlock._image_preloader is None:
            BoardBlock._image_preloader = EventImagePreloader(screen)
            BoardBlock._image_preloader.preload_all_events()

        # Show scenes for the starting block
        self.show_block_scenes()

        # Mark as fully loaded after initialization
        self.is_fully_loaded = True
    
    def load_place_names(self):
        """Load place names from place.json file."""
        place_file = os.path.join(os.path.dirname(__file__), 'place.json')
        try:
            with open(place_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load place.json: {e}")
            return {}
        
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

            previous_board = getattr(self, 'character_board', None)
            new_board = block_info['board']

            # Character position = board position + block offset
            self.character_pos = (
                board_x + block_info['x'],
                board_y + block_info['y']
            )

            self.character_board = new_board

            # Automatically slide the view when the character changes boards
            if previous_board is not None and new_board != previous_board:
                direction = 'forward' if new_board > previous_board else 'backward'
                self._begin_board_transition(new_board, direction=direction, auto=True)

    def get_block_world_position(self, block_number):
        """Return the on-screen position for a block centre."""
        block_info = self.blocks_info.get(block_number)
        if not block_info:
            return None

        board_x, board_y = self.get_board_top_left()
        return (
            board_x + block_info['x'],
            board_y + block_info['y']
        )

    def build_path_for_steps(self, steps):
        """Construct a sequential list of blocks for a given number of steps."""
        path = []
        current = self.current_block
        for _ in range(max(0, steps)):
            info = self.blocks_info.get(current)
            if not info:
                break
            next_block = info.get('next')
            if not next_block:
                break
            path.append(next_block)
            current = next_block
        return path

    def start_path_movement(self, block_sequence, movement_type='dice', show_scenes=True, allow_jump=True):
        """Animate movement across a list of block numbers."""
        if not block_sequence:
            return False

        if not self.is_ready_for_input():
            return False

        # Ensure all blocks exist
        positions = [self.get_block_world_position(block) for block in block_sequence]
        if not all(positions):
            return False

        start_pos = self.get_block_world_position(self.current_block)
        if start_pos is None:
            return False

        self.active_animation = {
            'blocks': block_sequence,
            'segment_index': 0,
            'start_pos': start_pos,
            'end_pos': positions[0],
            'start_time': pygame.time.get_ticks(),
            'duration': self.animation_duration,
            'type': movement_type,
            'show_scenes': show_scenes,
            'allow_jump': allow_jump
        }
        self.active_animation['target_block'] = block_sequence[0]
        self.floating_text = None
        self.is_transitioning = True
        return True

    def start_jump_animation(self, from_block, to_block, label_text=None):
        """Animate a jump (ladder/trunk) between two blocks."""
        start_pos = self.get_block_world_position(from_block)
        end_pos = self.get_block_world_position(to_block)
        if not start_pos or not end_pos:
            self.current_block = to_block
            self.update_character_position()
            self.show_block_scenes()
            return

        jump_type = 'jump_forward' if to_block > from_block else 'jump_backward'
        self.active_animation = {
            'blocks': [to_block],
            'segment_index': 0,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'start_time': pygame.time.get_ticks(),
            'duration': int(self.animation_duration * 1.1),
            'type': jump_type,
            'show_scenes': True,
            'allow_jump': False
        }
        self.active_animation['target_block'] = to_block
        self.is_transitioning = True

        if label_text:
            color = (54, 104, 214) if to_block > from_block else (176, 41, 53)
            self._spawn_floating_text(label_text, color)

    def _begin_board_transition(self, target_board, direction=None, auto=False):
        """Start sliding the board view towards the requested board."""
        if target_board is None:
            return False

        # Clamp to available boards
        if target_board < 1 or target_board > self.total_boards:
            return False

        # Avoid starting multiple transitions simultaneously
        if self.board_transition:
            if self.board_transition.get('target_board') == target_board:
                return False
            return False

        start_board = self.viewed_board
        if target_board == start_board:
            return False

        if direction is None:
            direction = 'forward' if target_board > start_board else 'backward'

        self.board_transition = {
            'start_board': start_board,
            'target_board': target_board,
            'start_time': pygame.time.get_ticks(),
            'duration': self.board_transition_duration,
            'direction': direction,
            'auto': auto
        }
        return True

    def trigger_wrap_effect(self):
        """Trigger a short flash effect for instant warps."""
        self.wrap_effect = {
            'start_time': pygame.time.get_ticks(),
            'duration': 500,
            'max_radius': 70
        }

    def is_animating_movement(self):
        """Return True while a movement animation is active."""
        return self.active_animation is not None

    def move_forward(self, show_scenes=True):
        """
        Move character to the next block.

        Args:
            show_scenes: Whether to show scenes for the new block (default: True)

        Returns:
            bool: True if successful, False otherwise
        """
        if self.game_completed:
            return False

        # Safety check: prevent movement if not fully loaded or transitioning
        if not self.is_fully_loaded or self.is_transitioning:
            return False
        
        # Prevent movement if viewing scenes or playing game
        if self.viewing_scenes or self.playing_game or self.pending_scenes:
            return False
        
        if self.current_block in self.blocks_info:
            next_block = self.blocks_info[self.current_block]['next']
            if next_block:
                # Lock state during transition
                self.is_transitioning = True
                
                self.current_block = next_block
                self.update_character_position()
                
                # Show scenes for the new block
                # Jumps will be checked AFTER scenes finish in _check_post_scene_actions()
                if show_scenes:
                    self.show_block_scenes()

                # Unlock state after transition when no jump animation started
                self.is_transitioning = False
                return True
        
        self.is_transitioning = False
        return False
    
    def move_backward(self, show_scenes=True):
        """
        Move character to the previous block.

        Args:
            show_scenes: Whether to show scenes for the new block (default: True)

        Returns:
            bool: True if successful, False otherwise
        """
        if self.game_completed:
            return False

        # Safety check: prevent movement if not fully loaded or transitioning
        if not self.is_fully_loaded or self.is_transitioning:
            return False
        
        # Prevent movement if viewing scenes or playing game
        if self.viewing_scenes or self.playing_game or self.pending_scenes:
            return False
        
        if self.current_block in self.blocks_info:
            prev_block = self.blocks_info[self.current_block]['prev']
            if prev_block:
                # Lock state during transition
                self.is_transitioning = True
                
                self.current_block = prev_block
                self.update_character_position()
                
                # Show scenes for the new block
                # Jumps will be checked AFTER scenes finish in _check_post_scene_actions()
                if show_scenes:
                    self.show_block_scenes()

                # Unlock state after transition when no jump animation started
                self.is_transitioning = False
                return True
        
        self.is_transitioning = False
        return False
    
    def move_to_block(self, block_number):
        """
        Move character to a specific block number.

        Args:
            block_number: Target block (1-60)

        Returns:
            bool: True if successful, False if invalid block
        """
        if self.game_completed:
            return False

        # Safety check: prevent movement if not fully loaded or transitioning
        if not self.is_fully_loaded or self.is_transitioning:
            return False
        
        # Prevent movement if viewing scenes or playing game
        if self.viewing_scenes or self.playing_game or self.pending_scenes:
            return False
        
        if block_number in self.blocks_info:
            # Lock state during transition
            self.is_transitioning = True
            
            self.current_block = block_number
            self.update_character_position()
            
            # Check for special block jumps (from_jump=False because this is normal movement)
            jump_destination = get_block_jump_destination(self.current_block, from_jump=False)
            if jump_destination:
                label = "Ladder!" if jump_destination > self.current_block else "Trunk!"
                self.start_jump_animation(self.current_block, jump_destination, label)
                return True

            # Show scenes for the new block
            self.show_block_scenes()

            # Unlock state after transition
            self.is_transitioning = False
            return True
        
        self.is_transitioning = False
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
            self.scene_viewer = SceneViewer(self.screen, self.cached_scenes, block_number=self.current_block, scene_duration=5000)
            self.viewing_scenes = True
            self.pending_scenes = False
            self.cached_scenes = None
    
    def _check_post_scene_actions(self):
        """
        Check what to do after scenes finish.
        Priority: 1) Jumps, 2) Game events, 3) End game check
        """
        # First check for jumps
        jump_destination = get_block_jump_destination(self.current_block, from_jump=False)
        if jump_destination:
            label = "Ladder!" if jump_destination > self.current_block else "Trunk!"
            self.start_jump_animation(self.current_block, jump_destination, label)
            return
        
        # No jump, so check for game events
        self.check_and_start_game_event()
    
    def check_and_start_game_event(self):
        """
        Check if current block triggers a game event and start it.

        This method is idempotent and safe to call multiple times.
        It includes safety checks to prevent:
        - Starting multiple games simultaneously
        - Starting games during scene viewing or transitions
        
        Called from:
        1. _check_post_scene_actions() - After scenes finish
        2. handle_event() - When scenes are skipped by user input
        """
        if self.game_completed:
            return

        # Safety checks: Don't start a new game if one is already active or system is busy
        if self.playing_game or self.current_game is not None:
            return
        
        # Don't start game during transitions or if viewing scenes
        if self.is_transitioning or self.viewing_scenes or self.pending_scenes:
            return
        
        # Random Card has priority - check first
        if self.current_block in self.random_blocks:
            if RandomCard is None:
                print(f"Warning: RandomCard unavailable for block {self.current_block}")
                return
            print(f"Starting Random Card event at block {self.current_block}")
            self.current_game = RandomCard(self.screen, self.current_block)
            self.playing_game = True
            return
        
        if self.current_block in self.math_blocks:
            if MathEvent is None:
                print(f"Warning: MathEvent unavailable for block {self.current_block}")
                return
            print(f"Starting Math game at block {self.current_block}")
            self.current_game = MathEvent(self.screen, self.current_block)
            self.playing_game = True
            return

        if self.current_block in self.rps_blocks:
            if RockPaperScissors is None:
                print(f"Warning: RockPaperScissors unavailable for block {self.current_block}")
                return
            print(f"Starting Rock-Paper-Scissors game at block {self.current_block}")
            self.current_game = RockPaperScissors(self.screen, self.current_block)
            self.playing_game = True
            return

        if self.current_block in self.guess_blocks:
            if GuessGame is None:
                print(f"Warning: GuessGame unavailable for block {self.current_block}")
                return
            print(f"Starting Guess game at block {self.current_block}")
            self.current_game = GuessGame(self.screen, self.current_block)
            self.playing_game = True
            return

        if self.current_block in self.photo_hunt_blocks:
            if PhotoHuntGame is None:
                print(f"Warning: PhotoHuntGame unavailable for block {self.current_block}")
                return
            print(f"Starting Photo Hunt game at block {self.current_block}")
            self.current_game = PhotoHuntGame(self.screen, self.current_block)
            self.playing_game = True

    def _start_alphabet_reward(self, source='event'):
        if AlphabetWin is None:
            print("Warning: AlphabetWin unavailable")
            return False
        self.current_game = AlphabetWin(self.screen, source=source)
        self.playing_game = True
        return True

    def _start_alphabet_return(self):
        if AlphabetLose is None:
            print("Warning: AlphabetLose unavailable")
            return False
        self.current_game = AlphabetLose(self.screen)
        self.playing_game = True
        return True

    def _handle_mini_game_result(self, result, finished_game=None):
        follow_up_started = False
        
        print(f"DEBUG: _handle_mini_game_result called with result={result}, finished_game={type(finished_game).__name__ if finished_game else None}")

        effect = result.get('effect') if isinstance(result, dict) else None
        if effect:
            effect_type = effect.get('type')
            if effect_type == 'warp':
                movement = effect.get('value')
                if movement is not None:
                    # Calculate new block position with bounds checking (1-60)
                    new_block = self.current_block + movement
                    new_block = max(1, min(60, new_block))  # Clamp between 1 and 60
                    
                    if new_block != self.current_block:
                        direction = "forward" if movement > 0 else "backward"
                        print(f"Random Card: Moving {direction} {abs(movement)} spaces from {self.current_block} to {new_block}")
                        self.current_block = new_block
                        self.update_character_position()
                        self.trigger_wrap_effect()
                        self.show_block_scenes()
                        if new_block == 60:
                            self._check_for_alphabet_completion()
                    else:
                        print(f"Random Card: Already at boundary, staying at block {self.current_block}")
                return False
            if effect_type == 'good':
                print("Random Card: Good card - gain letters")
                follow_up_started = self._start_alphabet_reward(source='random')
                return follow_up_started
            if effect_type == 'bad':
                print("Random Card: Bad card - return a letter")
                follow_up_started = self._start_alphabet_return()
                return follow_up_started
            return False

        if finished_game and AlphabetWin and isinstance(finished_game, AlphabetWin):
            self._check_for_alphabet_completion()
            return False
        if finished_game and AlphabetLose and isinstance(finished_game, AlphabetLose):
            self._check_for_alphabet_completion()
            return False
        if finished_game and GameOutcomeScreen and isinstance(finished_game, GameOutcomeScreen):
            return False

        result_flag = result.get('result') if isinstance(result, dict) else None
        success_flag = result.get('success') if isinstance(result, dict) else None
        
        print(f"DEBUG: result_flag={result_flag}, success_flag={success_flag}")

        if result_flag in ('win',) or success_flag is True:
            print(f"DEBUG: Calling _start_alphabet_reward for win/success")
            follow_up_started = self._start_alphabet_reward(source='event')
            return follow_up_started

        if result_flag in ('alphabet-win', 'alphabet-lose'):
            self._check_for_alphabet_completion()
            return False

        if result_flag == 'game-finished':
            self.final_outcome = result.get('outcome')
            self.game_completed = True
            return False

        return False

    def _check_for_alphabet_completion(self):
        if self.game_completed:
            return
        if self.current_block == 60:
            outcome = 'win' if game_state.has_ayutthaya_letters() else 'lose'
            self._show_game_outcome(outcome)

    def _show_game_outcome(self, outcome):
        if GameOutcomeScreen is None:
            print(f"Game ended with {outcome.upper()}, but GameOutcomeScreen unavailable")
            self.game_completed = True
            self.final_outcome = outcome
            return
        self.current_game = GameOutcomeScreen(self.screen, outcome)
        self.playing_game = True
        self.game_completed = True
        self.final_outcome = outcome

    def update(self):
        """Update board state. Call this every frame."""
        if self.active_animation:
            self._update_movement_animation()

        # Update floating text fade/movement
        if self.floating_text:
            self._update_floating_text()

        # Update wrap effect lifetime
        if self.wrap_effect:
            now = pygame.time.get_ticks()
            if now - self.wrap_effect['start_time'] >= self.wrap_effect['duration']:
                self.wrap_effect = None

        # Check if we're waiting to show scenes
        if self.pending_scenes:
            current_time = pygame.time.get_ticks()
            if current_time - self.scene_delay_timer >= self.scene_delay_duration:
                # Delay is over, start showing scenes
                self.start_pending_scenes()
        
        # Update scene viewer if active
        if self.viewing_scenes and self.scene_viewer:
            self.scene_viewer.update()
            # Check if scene viewing is finished (auto-advance by timer)
            if self.scene_viewer.is_finished:
                self.viewing_scenes = False
                self.scene_viewer = None
                # After scenes finish, check for jumps first, then game events
                self._check_post_scene_actions()
        
        # Update game if playing
        if self.playing_game and self.current_game:
            if hasattr(self.current_game, 'update'):
                self.current_game.update()

    def _update_movement_animation(self):
        """Progress the active movement animation."""
        animation = self.active_animation
        if not animation:
            return

        now = pygame.time.get_ticks()
        duration = max(1, animation.get('duration', self.animation_duration))
        progress = (now - animation['start_time']) / duration
        progress = max(0.0, min(1.0, progress))

        start_pos = animation.get('start_pos')
        end_pos = animation.get('end_pos')
        if start_pos and end_pos:
            eased = self._ease_in_out(progress)
            self.character_pos = (
                start_pos[0] + (end_pos[0] - start_pos[0]) * eased,
                start_pos[1] + (end_pos[1] - start_pos[1]) * eased
            )

        if progress >= 1.0:
            # Snap to target block at the end of the segment
            self.current_block = animation['target_block']
            self.update_character_position()

            # Advance to the next segment if available
            segment_index = animation['segment_index']
            if segment_index + 1 < len(animation['blocks']):
                animation['segment_index'] += 1
                next_block = animation['blocks'][animation['segment_index']]
                animation['start_pos'] = self.get_block_world_position(self.current_block)
                animation['end_pos'] = self.get_block_world_position(next_block)
                animation['start_time'] = now
                animation['target_block'] = next_block

                # If we're about to move onto a different board, start sliding the view
                current_board = self.blocks_info.get(self.current_block, {}).get('board')
                next_board = self.blocks_info.get(next_block, {}).get('board')
                if next_board and current_board and next_board != current_board:
                    direction = 'forward' if next_board > current_board else 'backward'
                    self._begin_board_transition(next_board, direction=direction, auto=True)
            else:
                final_block = self.current_block
                show_scenes = animation.get('show_scenes', True)
                allow_jump = animation.get('allow_jump', True)

                self.active_animation = None
                self.is_transitioning = False

                if allow_jump:
                    self._resolve_post_movement(final_block, show_scenes)
                else:
                    # Jump animation completed - show scenes and check for game completion
                    if show_scenes:
                        self.show_block_scenes()
                        self._check_for_alphabet_completion()
                    else:
                        self._check_for_alphabet_completion()

    def _resolve_post_movement(self, final_block, show_scenes):
        """Handle ladders/snakes or scene triggers after movement completes."""
        jump_destination = get_block_jump_destination(final_block, from_jump=False)
        if jump_destination:
            label = "Ladder!" if jump_destination > final_block else "Trunk!"
            self.start_jump_animation(final_block, jump_destination, label)
            return

        if show_scenes:
            self.show_block_scenes()
            self._check_for_alphabet_completion()
        else:
            self._check_for_alphabet_completion()

    def _ease_in_out(self, t):
        """Smooth step interpolation."""
        return 0.5 - 0.5 * math.cos(math.pi * t)

    def _spawn_floating_text(self, text, color):
        """Create a floating text label above the board."""
        if not text:
            return

        font = TEXT_FONT_BOLD
        surface = font.render(text, True, color)
        if surface:
            surface = surface.convert_alpha()

        board_x, board_y = self.get_board_top_left()
        self.floating_text = {
            'surface': surface,
            'start_time': pygame.time.get_ticks(),
            'duration': 1200,
            'base_pos': (
                board_x + self.BOARD_WIDTH // 2,
                board_y - 40
            ),
            'offset_y': 0,
            'alpha': 255,
            'board': self.character_board
        }

    def _update_floating_text(self):
        """Fade and move the floating label upwards."""
        if not self.floating_text:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.floating_text['start_time']
        duration = self.floating_text.get('duration', 1)
        if elapsed >= duration:
            self.floating_text = None
            return

        progress = elapsed / duration
        self.floating_text['offset_y'] = -40 * progress
        self.floating_text['alpha'] = max(0, min(255, int(255 * (1 - progress))))

    def _draw_wrap_effect(self):
        """Render the flash effect used for instant warps."""
        if not self.wrap_effect or not self._last_drawn_character_pos:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.wrap_effect['start_time']
        duration = self.wrap_effect.get('duration', 1)
        if elapsed >= duration:
            self.wrap_effect = None
            return

        progress = max(0.0, min(1.0, elapsed / duration))
        radius = int(self.wrap_effect.get('max_radius', 60) * progress)
        if radius <= 0:
            return

        alpha = int(200 * (1 - progress))
        overlay_size = radius * 2
        overlay = pygame.Surface((overlay_size, overlay_size), pygame.SRCALPHA)
        center = (radius, radius)
        pygame.draw.circle(overlay, (255, 255, 255, alpha), center, radius)
        pygame.draw.circle(overlay, (255, 215, 0, max(0, alpha - 40)), center, max(1, radius // 2), 4)

        center_x, center_y = self._last_drawn_character_pos
        self.screen.blit(
            overlay,
            (center_x - radius, center_y - radius)
        )

    def _draw_floating_text(self):
        """Draw the floating feedback text (e.g., "Ladder!", "Trunk!")."""
        if not self.floating_text:
            return

        surface = self.floating_text.get('surface')
        if not surface:
            return

        alpha = self.floating_text.get('alpha', 255)
        text_surface = surface.copy()
        text_surface.set_alpha(alpha)

        base_x, base_y = self.floating_text.get('base_pos', (0, 0))
        offset_y = self.floating_text.get('offset_y', 0)
        board = self.floating_text.get('board')
        offset_x = 0
        if board is not None:
            offset_x = self._current_board_offsets.get(board)
            if offset_x is None:
                return
        else:
            offset_x = self._current_board_offsets.get(self.get_viewed_board(), 0)

        pos = (
            int(base_x + offset_x - text_surface.get_width() / 2),
            int(base_y + offset_y)
        )
        board_x, board_y = self.get_board_top_left()
        min_x = board_x
        max_x = board_x + self.BOARD_WIDTH - text_surface.get_width()
        if max_x < min_x:
            clamped_x = min_x
        else:
            clamped_x = max(min_x, min(pos[0], max_x))
        self.screen.blit(text_surface, (clamped_x, pos[1]))

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

        board_x, board_y = self.get_board_top_left()
        self._current_board_offsets = {}
        self._last_drawn_character_pos = None

        board_surface = pygame.Surface((self.BOARD_WIDTH, self.BOARD_HEIGHT), pygame.SRCALPHA)
        board_surface.fill((0, 0, 0, 0))

        def draw_board_surface(board_number, offset_x):
            if board_number is None:
                return

            clamped_offset = max(-self.BOARD_WIDTH, min(self.BOARD_WIDTH, offset_x))
            self._current_board_offsets[board_number] = clamped_offset
            dest_x = offset_x
            board_img_local = self.board_images.get(board_number)

            if board_img_local:
                board_surface.blit(board_img_local, (dest_x, 0))
            else:
                pygame.draw.rect(
                    board_surface,
                    (200, 180, 150),
                    (dest_x, 0, self.BOARD_WIDTH, self.BOARD_HEIGHT)
                )

            if self.character_pos and self.character_board == board_number:
                local_center = (
                    int((self.character_pos[0] - board_x) + offset_x),
                    int(self.character_pos[1] - board_y)
                )
                draw_center = (board_x + local_center[0], board_y + local_center[1])
                if self.character_image:
                    char_rect = self.character_image.get_rect(center=local_center)
                    board_surface.blit(self.character_image, char_rect)
                else:
                    pygame.draw.circle(
                        board_surface,
                        (255, 0, 0),
                        local_center,
                        15
                    )
                    pygame.draw.circle(
                        board_surface,
                        (255, 255, 255),
                        local_center,
                        15,
                        3
                    )
                self._last_drawn_character_pos = draw_center

        if self.board_transition:
            transition = self.board_transition
            duration = max(1, transition.get('duration', self.board_transition_duration))
            elapsed = pygame.time.get_ticks() - transition.get('start_time', 0)
            progress = max(0.0, min(1.0, elapsed / duration))
            eased = self._ease_in_out(progress)
            distance = self.BOARD_WIDTH
            travel = int(distance * eased)
            remaining = distance - travel

            if transition.get('direction') == 'forward':
                start_offset = -travel
                target_offset = remaining
            else:
                start_offset = travel
                target_offset = -remaining

            draw_board_surface(transition.get('start_board'), start_offset)
            draw_board_surface(transition.get('target_board'), target_offset)

            if progress >= 1.0:
                self.viewed_board = transition.get('target_board', self.viewed_board)
                self.board_transition = None
        else:
            draw_board_surface(self.viewed_board, 0)

        self.screen.blit(board_surface, (board_x, board_y))

        if self._last_drawn_character_pos:
            self._draw_wrap_effect()

        self._draw_floating_text()

        # Optional: Draw block number text
        self.draw_block_info()
    
    def draw_block_info(self):
        """Draw current block number and place name above the board-block."""
        # Use centralized font system
        font = TEXT_FONT_BOLD

        # Determine which board the label should attach to (target during transitions)
        reference_board = self.board_transition['target_board'] if self.board_transition else self.viewed_board
        board_x, board_y = self.get_board_top_left()
        offset_x = self._current_board_offsets.get(reference_board, 0)

        # Get place name for current block
        place_name = self.place_names.get(str(self.current_block), "Unknown Place")
        
        info_text = f"Board {self.get_viewed_board()} of {self.total_boards}"
        info_text += f"  •  Block {self.current_block}: {place_name}"
        text_surf = font.render(info_text, True, (0, 0, 0))

        text_rect = text_surf.get_rect()
        text_rect.bottom = board_y - 10
        text_rect.left = board_x

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

    def get_viewed_board(self):
        """Return the board currently targeted by the camera."""
        if self.board_transition:
            return self.board_transition.get('target_board', self.viewed_board)
        return self.viewed_board

    def get_character_board(self):
        """Return the board on which the character currently stands."""
        return self.character_board

    def total_board_count(self):
        return self.total_boards

    def can_view_previous_board(self):
        return not self.board_transition and self.viewed_board > 1

    def can_view_next_board(self):
        return not self.board_transition and self.viewed_board < self.total_boards

    def view_previous_board(self):
        if not self.can_view_previous_board():
            return False
        return self._begin_board_transition(self.viewed_board - 1, direction='backward', auto=False)

    def view_next_board(self):
        if not self.can_view_next_board():
            return False
        return self._begin_board_transition(self.viewed_board + 1, direction='forward', auto=False)

    def is_view_transition_active(self):
        return self.board_transition is not None
    
    def handle_event(self, event):
        """
        Handle keyboard input for testing movement.
        
        Args:
            event: Pygame event
            
        Returns:
            dict: Movement result or None
        """
        # Safety check: prevent any input handling if not fully loaded
        if not self.is_fully_loaded:
            return None
        
        # If playing a game event, forward events to game
        if self.playing_game and self.current_game:
            result = self.current_game.handle_event(event)
            if result is not None:
                finished_game = self.current_game
                print(f"Game finished with result: {result}")

                self.playing_game = False
                self.current_game = None

                self._handle_mini_game_result(result, finished_game)
            return None
        
        # If viewing scenes, forward events to scene viewer
        if self.viewing_scenes and self.scene_viewer:
            finished = self.scene_viewer.handle_event(event)
            if finished:
                self.viewing_scenes = False
                self.scene_viewer = None
                # After scenes finish (skipped by user), check for jumps then game events
                self._check_post_scene_actions()
            return None
        
        # Block input during transitions or pending scenes
        if self.is_transitioning or self.pending_scenes:
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
    
    def is_ready_for_input(self):
        """
        Check if the board is ready to accept user input.
        
        Returns:
            bool: True if board can accept input, False otherwise
        """
        return (
            self.is_fully_loaded and
            not self.is_transitioning and
            not self.viewing_scenes and
            not self.playing_game and
            not self.pending_scenes and
            not self.game_completed
        )


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
