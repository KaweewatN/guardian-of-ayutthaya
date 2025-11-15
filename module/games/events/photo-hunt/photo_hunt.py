import pygame
import os
import sys

# Add constant directory to path for font imports
try:
    from constant.fonts import BUTTON_FONT, BUTTON_FONT_LARGE, TEXT_FONT, TEXT_FONT_BOLD, SUBTITLE_FONT
except Exception:
    try:
        const_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'constant'))
        if const_path not in sys.path:
            sys.path.insert(0, const_path)
        from fonts import BUTTON_FONT, BUTTON_FONT_LARGE, TEXT_FONT, TEXT_FONT_BOLD, SUBTITLE_FONT
    except Exception as e:
        print(f"Warning: Fonts import failed ({e}). Using pygame fallback fonts.")
        try:
            pygame_font = pygame.font.SysFont(None, 28)
        except Exception:
            class _DummyFont:
                def render(self, text, aa, color):
                    surf = pygame.Surface((max(200, len(text) * 10), 30))
                    surf.fill((200, 200, 200))
                    return surf
            pygame_font = _DummyFont()

        BUTTON_FONT = pygame_font
        BUTTON_FONT_LARGE = pygame_font
        TEXT_FONT = pygame_font
        TEXT_FONT_BOLD = pygame_font
        SUBTITLE_FONT = pygame_font


class PhotoHuntGame:
    """Photo Hunt mini-game - find the difference between two images.
    
    The player views the 'before' image for 5 seconds, then has 5 seconds
    to click on the difference in the 'after' image.
    """

    # States
    STATE_INTRO = "intro"
    STATE_VIEWING = "viewing"  # Showing before image
    STATE_FINDING = "finding"  # Showing after image, player clicks
    STATE_RESULT = "result"

    # Game configuration
    VIEW_TIME = 5000  # 5 seconds to view before image (in milliseconds)
    FIND_TIME = 3000  # 5 seconds to find difference (in milliseconds)

    def __init__(self, screen, block_number=22):
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 832
        self.block_number = block_number

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BG_COLOR = (245, 235, 220)
        self.TIMER_COLOR = (220, 20, 60)  # Red for timer
        self.SUCCESS_COLOR = (34, 139, 34)  # Green
        self.FAIL_COLOR = (220, 20, 60)  # Red

        # Fonts
        self.title_font = BUTTON_FONT_LARGE
        self.subtitle_font = SUBTITLE_FONT
        self.text_font = TEXT_FONT
        self.timer_font = BUTTON_FONT_LARGE

        # Game state
        self.state = self.STATE_INTRO
        self.result = None  # 'win' or 'lose'
        self.final_result = None

        # Timer
        self.timer_start = 0
        self.time_remaining = 0

        # Images
        self.before_image = None
        self.after_image = None
        self.image_rect = None
        
        # Difference configuration for each block
        # Format: {block_number: [{'x': x, 'y': y, 'radius': radius, 'name': name}, ...]}
        # Player only needs to find ONE difference to win
        self.differences = {
            22: [
                {'x': 356, 'y': 634, 'radius': 60},
                {'x': 1247, 'y': 600, 'radius': 40},
                {'x': 1037, 'y': 550, 'radius': 60},
                {'x': 1039, 'y': 634, 'radius': 60},
                {'x': 1032, 'y': 713, 'radius': 60},
            ],
            34: [
                {'x': 242, 'y': 613, 'radius': 60},
                {'x': 604, 'y': 371, 'radius': 60},
            {'x': 603, 'y': 222, 'radius': 60},
                {'x': 686, 'y': 217, 'radius': 60},
                {'x': 510, 'y': 726, 'radius': 60},
            ]
        }

        
        # Debug mode - show circles on differences
        self.show_debug_circles = False  # Set to False in production
        
        # Load images
        self.load_images()

    def load_images(self):
        """Load before and after images for this block."""
        assets_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', '..', 
            'assets', 'scene', 'event', 'photo-hunt'
        )
        
        before_path = os.path.join(assets_path, f'{self.block_number}-before.png')
        after_path = os.path.join(assets_path, f'{self.block_number}-after.png')
        
        # Load before image
        if os.path.exists(before_path):
            try:
                img = pygame.image.load(before_path)
                self.before_image = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                print(f"Loaded photo hunt before image: {before_path}")
            except Exception as e:
                print(f"Error loading before image {before_path}: {e}")
                self.before_image = None
        else:
            print(f"Warning: before image not found at {before_path}")
            self.before_image = None
        
        # Load after image
        if os.path.exists(after_path):
            try:
                img = pygame.image.load(after_path)
                self.after_image = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                print(f"Loaded photo hunt after image: {after_path}")
            except Exception as e:
                print(f"Error loading after image {after_path}: {e}")
                self.after_image = None
        else:
            print(f"Warning: after image not found at {after_path}")
            self.after_image = None
        
        # Set up image rect for the full screen
        self.image_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)

    def draw_intro(self):
        """Draw intro screen with before-image background + 70% white mask."""
        
        # Draw background as BEFORE image
        if self.before_image:
            self.screen.blit(self.before_image, (0, 0))
        else:
            # fallback background
            self.screen.fill(self.BG_COLOR)

        # White mask with 70% opacity
        white_mask = pygame.Surface((self.screen_width, self.screen_height))
        white_mask.fill((255, 255, 255))
        white_mask.set_alpha(166)  # 70% opacity
        self.screen.blit(white_mask, (0, 0))

        # Title
        title = self.title_font.render("Photo Hunt", True, self.BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(title, title_rect)

        # Instructions
        instructions = [
            "Find ONE difference between two images!",
            "",
            "You will have 5 seconds to memorize the first image.",
            "Then, you have 5 seconds to find and click",
            "ANY difference in the second image.",
            "",
            "Good luck!"
        ]
        
        y_offset = 300
        for line in instructions:
            text_surf = self.text_font.render(line, True, self.BLACK)
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text_surf, text_rect)
            y_offset += 40

        # Start instruction
        start_text = self.text_font.render("Press SPACE or CLICK to start", True, self.BLACK)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(start_text, start_rect)


    def draw_viewing(self):
        """Draw viewing state - show before image with timer."""
        # Draw before image
        if self.before_image:
            self.screen.blit(self.before_image, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)
            error_text = self.subtitle_font.render("Image not found!", True, self.BLACK)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(error_text, error_rect)

        # Calculate time remaining
        elapsed = pygame.time.get_ticks() - self.timer_start
        self.time_remaining = max(0, (self.VIEW_TIME - elapsed) // 1000 + 1)  # Convert to seconds, +1 for display

        # Draw semi-transparent overlay for timer
        overlay = pygame.Surface((400, 150))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(200)
        overlay_rect = overlay.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(overlay, overlay_rect)

        # Draw "Memorize" text
        memo_text = self.subtitle_font.render("Memorize!", True, self.BLACK)
        memo_rect = memo_text.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(memo_text, memo_rect)

        # Draw timer
        timer_text = self.timer_font.render(f"{self.time_remaining}", True, self.TIMER_COLOR)
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(timer_text, timer_rect)

        # Check if viewing time is up
        if elapsed >= self.VIEW_TIME:
            self.state = self.STATE_FINDING
            self.timer_start = pygame.time.get_ticks()

    def draw_finding(self):
        """Draw finding state - show after image with timer."""
        # Draw after image
        if self.after_image:
            self.screen.blit(self.after_image, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)
            error_text = self.subtitle_font.render("Image not found!", True, self.BLACK)
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(error_text, error_rect)

        # Calculate time remaining
        elapsed = pygame.time.get_ticks() - self.timer_start
        self.time_remaining = max(0, (self.FIND_TIME - elapsed) // 1000 + 1)  # Convert to seconds, +1 for display

        # Draw semi-transparent overlay for timer
        overlay = pygame.Surface((600, 150))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(200)
        overlay_rect = overlay.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(overlay, overlay_rect)

        # Draw "Find the difference!" text
        find_text = self.subtitle_font.render("Find the difference!", True, self.BLACK)
        find_rect = find_text.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(find_text, find_rect)

        # Draw timer
        timer_text = self.timer_font.render(f"{self.time_remaining}", True, self.TIMER_COLOR)
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(timer_text, timer_rect)

        # DEBUG: Draw circles around all difference locations (for testing)
        if self.show_debug_circles and self.block_number in self.differences:
            differences_list = self.differences[self.block_number]
            for idx, diff in enumerate(differences_list):
                # Draw semi-transparent yellow circle
                circle_surface = pygame.Surface((diff['radius'] * 2 + 10, diff['radius'] * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (255, 255, 0, 100), 
                                 (diff['radius'] + 5, diff['radius'] + 5), diff['radius'] + 5, 3)
                self.screen.blit(circle_surface, 
                               (diff['x'] - diff['radius'] - 5, diff['y'] - diff['radius'] - 5))
                
                # Draw difference number and name
                debug_font = pygame.font.SysFont('Arial', 16, bold=True)
                debug_text = debug_font.render(f"{idx + 1}: {diff['name']}", True, (255, 255, 0))
                debug_rect = debug_text.get_rect(center=(diff['x'], diff['y'] - diff['radius'] - 15))
                # Add black outline for readability
                outline_text = debug_font.render(f"{idx + 1}: {diff['name']}", True, (0, 0, 0))
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    outline_rect = outline_text.get_rect(center=(diff['x'] + dx, diff['y'] - diff['radius'] - 15 + dy))
                    self.screen.blit(outline_text, outline_rect)
                self.screen.blit(debug_text, debug_rect)

        # Check if time is up
        if elapsed >= self.FIND_TIME:
            self.result = 'lose'
            self.state = self.STATE_RESULT
            
    def draw_result(self):
        """Draw result screen with AFTER image background + 60% white mask."""

        # Draw AFTER image as background
        if self.after_image:
            self.screen.blit(self.after_image, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # White mask (60% opacity = alpha 153)
        white_mask = pygame.Surface((self.screen_width, self.screen_height))
        white_mask.fill((255, 255, 255))
        white_mask.set_alpha(166)
        self.screen.blit(white_mask, (0, 0))

        # Result title
        if self.result == 'win':
            result_title = "You Found It!"
            result_color = self.SUCCESS_COLOR
        else:
            result_title = "Time's Up!"
            result_color = self.FAIL_COLOR

        title_surf = self.title_font.render(result_title, True, result_color)
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 280))
        self.screen.blit(title_surf, title_rect)

        # Additional message
        msg = "Great job spotting the difference!" if self.result == 'win' else "Better luck next time!"
        msg_surf = self.subtitle_font.render(msg, True, self.BLACK)
        msg_rect = msg_surf.get_rect(center=(self.screen_width // 2, 400))
        self.screen.blit(msg_surf, msg_rect)

        # Continue instruction
        continue_text = self.text_font.render("Press SPACE or CLICK to continue", True, self.BLACK)
        continue_rect = continue_text.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(continue_text, continue_rect)


    def draw(self):
        """Main draw method."""
        if self.state == self.STATE_INTRO:
            self.draw_intro()
        elif self.state == self.STATE_VIEWING:
            self.draw_viewing()
        elif self.state == self.STATE_FINDING:
            self.draw_finding()
        elif self.state == self.STATE_RESULT:
            self.draw_result()

    def check_click(self, pos):
        """Check if the player clicked on ANY difference area.
        Returns True if a difference was found (player wins immediately)."""
        if self.block_number not in self.differences:
            print(f"Warning: No difference configured for block {self.block_number}")
            return False
        
        click_x, click_y = pos
        differences_list = self.differences[self.block_number]
        
        # Check each difference - player only needs to find ONE
        for idx, diff in enumerate(differences_list):
            diff_x, diff_y, radius = diff['x'], diff['y'], diff['radius']
            
            # Calculate distance from click to difference center
            distance = ((click_x - diff_x) ** 2 + (click_y - diff_y) ** 2) ** 0.5
            
            if distance <= radius:
                # Found a difference! Player wins immediately
                print(f"Found difference: {diff.get('name', f'Difference {idx + 1}')}")
                self.result = 'win'
                self.state = self.STATE_RESULT
                return True
        
        return False

    def handle_event(self, event):
        """Handle pygame events. Returns result dict when finished, else None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_INTRO:
                    # Start viewing phase
                    self.state = self.STATE_VIEWING
                    self.timer_start = pygame.time.get_ticks()
                    return None
                elif self.state == self.STATE_RESULT:
                    # Finalize and return
                    return self._finalize()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.state == self.STATE_INTRO:
                    # Start viewing phase
                    self.state = self.STATE_VIEWING
                    self.timer_start = pygame.time.get_ticks()
                    return None
                elif self.state == self.STATE_FINDING:
                    # Check if clicked on difference
                    self.check_click(event.pos)
                    # Continue playing until all found or time runs out
                    return None
                elif self.state == self.STATE_RESULT:
                    # Finalize and return
                    return self._finalize()

        return None

    def _finalize(self):
        """Return the result dict to caller after result screen."""
        self.final_result = self.result
        print(f"PhotoHunt returning result: {{'result': '{self.result}'}}")
        return {"result": self.result}

    def update_screen_size(self, screen):
        """Update screen size and recalculate positions."""
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 832
        
        # Reload images at new size
        self.load_images()
