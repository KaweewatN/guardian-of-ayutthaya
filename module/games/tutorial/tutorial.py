"""
Tutorial System
Teaches players the game mechanics and rules before starting the main game
"""
import pygame
import os
import sys

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

try:
    from fonts import TEXT_FONT, TEXT_FONT_BOLD, SUBTITLE_FONT, TITLE_FONT
except Exception as e:
    print(f"Warning: Fonts import failed ({e}). Using fallback fonts.")
    TEXT_FONT = pygame.font.SysFont('Arial', 24)
    TEXT_FONT_BOLD = pygame.font.SysFont('Arial', 24, bold=True)
    SUBTITLE_FONT = pygame.font.SysFont('Arial', 48)
    TITLE_FONT = pygame.font.SysFont('Arial', 72, bold=True)


class Tutorial:
    """
    Interactive tutorial system that teaches:
    1. Board navigation and dice mechanics
    2. Different event types (Math, Rock-Paper-Scissors, Guess, Random Card)
    3. Special blocks and movement rules
    4. Win/lose conditions
    """
    
    def __init__(self, screen):
        """
        Initialize the tutorial
        
        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Colors (adjusted for dark background)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_TEXT = (240, 240, 240)  # Bright text for dark bg
        self.GRAY = (180, 180, 180)  # Lighter gray for visibility
        self.DARK_GRAY = (100, 100, 100)
        self.GOLD = (255, 215, 0)  # Brighter gold for contrast
        self.DARK_GOLD = (200, 155, 91)
        self.BG_COLOR = (245, 235, 220)
        
        # Tutorial state
        self.current_page = 0
        self.finished = False
        
        # Fonts
        self.title_font = TITLE_FONT
        self.subtitle_font = SUBTITLE_FONT
        self.text_font = TEXT_FONT
        self.text_font_bold = TEXT_FONT_BOLD
        
        # Load background image
        self.background = None
        self.load_background()
        
        # Tutorial pages with content
        self.pages = self.create_tutorial_pages()
        
        # Load page images
        self.page_images = {}
        self.load_page_images()
        
        # Navigation buttons
        self.create_buttons()
        
        # Button hover states
        self.next_hovered = False
        self.prev_hovered = False
        self.skip_hovered = False
        
        # Skip behavior flag
        self.skip_returns_to_game = False
        self._was_skipped = False
    
    def load_background(self):
        """Load tutorial background image"""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        bg_path = os.path.join(base_path, 'assets', 'core', 'tutorial-bg.png')
        
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                print(f"Loaded tutorial background: tutorial-bg.png")
            except Exception as e:
                print(f"Error loading tutorial-bg.png: {e}")
                self.background = None
        else:
            print(f"Warning: tutorial-bg.png not found at {bg_path}")
            self.background = None
    
    def load_page_images(self):
        """Load images for each tutorial page (1.png to 11.png)"""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        tutorial_assets = os.path.join(base_path, 'assets', 'tutorial')
        
        # Try to load images 1.png through 11.png
        for i in range(1, 12):
            img_path = os.path.join(tutorial_assets, f'{i}.png')
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale image bigger (max width 800px, max height 350px)
                    img_rect = img.get_rect()
                    max_width = 800
                    max_height = 350
                    
                    # Calculate scale factor to fit within constraints
                    scale_w = max_width / img_rect.width if img_rect.width > max_width else 1
                    scale_h = max_height / img_rect.height if img_rect.height > max_height else 1
                    scale = min(scale_w, scale_h)
                    
                    if scale < 1:
                        new_width = int(img_rect.width * scale)
                        new_height = int(img_rect.height * scale)
                        img = pygame.transform.smoothscale(img, (new_width, new_height))
                    
                    self.page_images[i - 1] = img  # Store by page index (0-based)
                    print(f"Loaded tutorial image: {i}.png")
                except Exception as e:
                    print(f"Error loading {i}.png: {e}")
            # If image doesn't exist, that's okay - not all pages need images
        
    def create_tutorial_pages(self):
        """Create tutorial page content"""
        pages = [
            {
                "title": "Welcome to Guardian of Ayutthaya!",
                "content": [
                    "You are about to embark on an epic journey through ancient Thailand.",
                    "",
                    "Your mission: Navigate the game board, overcome challenges,",
                    "and reach the final destination to become the Guardian of Ayutthaya!",
                    "",
                    "This tutorial will teach you everything you need to know.",
                ],
                "icon": "welcome"
            },
            {
                "title": "The Game Board",
                "content": [
                    "• The game has 60 blocks across 2 boards (30 blocks each)",
                    "• Start at Block 1 and try to reach Block 60",
                    "• Roll the dice to move forward on the board",
                    "",
                    "Movement:",
                    "• Click 'Roll Dice' button or press SPACE to roll",
                    "• You'll move automatically based on the dice result (1-6)",
                    "• Some blocks have special events that you must complete",
                ],
                "icon": "board"
            },
            {
                "title": "Event Types",
                "content": [
                    "You'll encounter 5 types of events on special blocks:",
                    "",
                    "1. Math Challenge - Solve math problems correctly",
                    "2. Rock-Paper-Scissors - Win the classic game",
                    "3. Guess Game - Answer questions about Brain teasers",
                    "4. Photo Hunt - Find differences between two images",
                    "5. Random Card - Draw a card for random effects",
                    "",
                    "Complete events to continue your journey!",
                ],
                "icon": "events"
            },
            {
                "title": "Math Challenge",
                "content": [
                    "• Solve addition, subtraction, multiplication, or division",
                    "• Type your answer and submit",
                    "• Get it right to continue!",
                    "• You have multiple attempts, but be careful!",
                ],
                "icon": "math"
            },
            {
                "title": "Rock-Paper-Scissors",
                "content": [
                    "• Classic game: Rock beats Scissors, Scissors beats Paper,",
                    "  Paper beats Rock",
                    "• Choose your move wisely",
                    "• Win to proceed on your journey",
                ],
                "icon": "rps"
            },
            {
                "title": "Guess Game",
                "content": [
                    "• Answer questions about Brain teasers",
                    "• Type your answer",
                ],
                "icon": "guess"
            },
            {
                "title": "Photo Hunt",
                "content": [
                    "• Find the differences between two similar images",
                    "• Click on the differences you spot",
                    "• Find all differences to win!",
                    "• Pay close attention to details",
                ],
                "icon": "photo-hunt"
            },
            {
                "title": "Random Card",
                "content": [
                    "• Draw one card from three face-down cards",
                    "  - Good Card: Positive effect",
                    "  - Bad Card: Negative effect", 
                    "  - Warp Card: Teleport to a different block",
                ],
                "icon": "random"
            },
            {
                "title": "Special Features",
                "content": [
                    "Block Scenes:",
                    "• After landing on a block, you may see story scenes",
                    "• Press SPACE or CLICK to skip scenes",
                    "• Wait 5 seconds for scenes to auto-play",
                    "",
                    "Block Jumps:",
                    "• Some blocks automatically jump you to another location",
                    "• These are part of the game's story progression",
                ],
                "icon": "special"
            },
            {
                "title": "Tips for Success",
                "content": [
                    "1. Pay attention to block numbers with events",
                    "2. Read questions carefully in Guess games",
                    "3. Think strategically in Rock-Paper-Scissors",
                    "4. Calculate carefully in Math challenges",
                    "5. Random cards can help or hinder - embrace the chaos!",
                ],
                "icon": "tips"
            },
            {
                "title": "Ready to Begin!",
                "content": [
                    "You now know everything needed to play!",
                    "",
                    "Your quest to become the Guardian of Ayutthaya awaits.",
                    "",
                    "Click 'Start Game' to begin your adventure!",
                    "",
                    "Good luck, brave guardian!",
                ],
                "icon": "ready"
            }
        ]
        return pages
    
    def create_buttons(self):
        """Create navigation buttons"""
        button_width = 180
        button_height = 60
        button_y = self.screen_height - 100
        
        # Next button (right side)
        self.next_button = pygame.Rect(
            self.screen_width - button_width - 50,
            button_y,
            button_width,
            button_height
        )
        
        # Previous button (left side)
        self.prev_button = pygame.Rect(
            50,
            button_y,
            button_width,
            button_height
        )
        
        # Skip button (top right)
        self.skip_button = pygame.Rect(
            self.screen_width - 150,
            30,
            120,
            50
        )
    
    def draw_button(self, rect, text, hovered, enabled=True):
        """Draw a button with hover effect (optimized for dark background)"""
        if not enabled:
            color = self.DARK_GRAY
            text_color = self.GRAY
            border_color = self.DARK_GRAY
        elif hovered:
            color = self.GOLD
            text_color = self.BLACK
            border_color = self.GOLD
        else:
            color = self.DARK_GOLD
            text_color = self.WHITE
            border_color = self.GOLD
        
        # Draw button background
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        # Draw button border
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=10)
        
        # Draw button text
        text_surface = self.text_font_bold.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_page_indicator(self):
        """Draw page number indicator (bright for dark background)"""
        indicator_text = f"Page {self.current_page + 1} / {len(self.pages)}"
        text_surface = self.text_font.render(indicator_text, True, self.LIGHT_TEXT)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(text_surface, text_rect)
    
    def draw_content(self, page):
        """Draw the content of the current page (optimized for dark background)"""
        # Draw title with shadow for better readability
        title_text = page["title"]
        
        # Draw shadow
        shadow_surface = self.subtitle_font.render(title_text, True, self.BLACK)
        shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 2, 102))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw title
        title_surface = self.subtitle_font.render(title_text, True, self.GOLD)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw decorative line under title
        line_y = 150
        line_start = (self.screen_width // 2 - 300, line_y)
        line_end = (self.screen_width // 2 + 300, line_y)
        pygame.draw.line(self.screen, self.GOLD, line_start, line_end, 4)
        
        # Check if we have an image for this page
        has_image = self.current_page in self.page_images
        
        # Draw ALL content lines with shadow for readability (no truncation)
        y_offset = 200
        line_spacing = 35 if has_image else 40
        
        for line in page["content"]:
            if line == "":
                y_offset += line_spacing // 2
                continue
            
            # Check if line starts with bullet point or number
            if line.startswith("•") or line.startswith("1.") or line.startswith("2.") or \
               line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
                font = self.text_font_bold
                text_color = self.WHITE
            else:
                font = self.text_font
                text_color = self.LIGHT_TEXT
            
            # Draw text shadow
            shadow_surface = font.render(line, True, self.BLACK)
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 1, y_offset + 1))
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Draw text
            text_surface = font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += line_spacing
        
        # Draw image if available (centered horizontally, below text with 5px vertical margin)
        if has_image:
            image = self.page_images[self.current_page]
            img_rect = image.get_rect()
            img_x = (self.screen_width - img_rect.width) // 2
            img_y = y_offset + 5  # 5px vertical margin below text
            
            # Draw darker yellow/gold border around image (6px thick) for pages 1-8
            # Pages 9 and 10 don't have border
            if self.current_page < 8:
                border_thickness = 6
                border_color = self.GOLD  # Darker gold color (255, 215, 0)
                border_rect = pygame.Rect(
                    img_x - border_thickness,
                    img_y - border_thickness,
                    img_rect.width + (border_thickness * 2),
                    img_rect.height + (border_thickness * 2)
                )
                pygame.draw.rect(self.screen, border_color, border_rect, border_thickness)
            
            # Draw the image
            self.screen.blit(image, (img_x, img_y))
    
    def draw(self):
        """Draw the current tutorial page"""
        # Draw background image or fill with color
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Fallback dark background if image not found
            self.screen.fill((20, 20, 30))
        
        # Draw current page content
        if self.current_page < len(self.pages):
            self.draw_content(self.pages[self.current_page])
        
        # Draw navigation buttons
        # Previous button (disabled on first page)
        self.draw_button(
            self.prev_button, 
            "Previous", 
            self.prev_hovered,
            enabled=(self.current_page > 0)
        )
        
        # Next/Start button
        is_last_page = (self.current_page >= len(self.pages) - 1)
        next_text = "Start Game" if is_last_page else "Next"
        self.draw_button(self.next_button, next_text, self.next_hovered)
        
        # Skip button
        self.draw_button(self.skip_button, "Skip", self.skip_hovered)
        
        # Page indicator
        self.draw_page_indicator()
    
    def handle_event(self, event):
        """
        Handle tutorial events
        
        Args:
            event: Pygame event
            
        Returns:
            bool: True if tutorial is finished, False otherwise
        """
        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            self.next_hovered = self.next_button.collidepoint(event.pos)
            self.prev_hovered = self.prev_button.collidepoint(event.pos) and self.current_page > 0
            self.skip_hovered = self.skip_button.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Next button
                if self.next_button.collidepoint(event.pos):
                    if self.current_page >= len(self.pages) - 1:
                        # Last page - finish tutorial
                        self.finished = True
                        return True
                    else:
                        # Go to next page
                        self.current_page += 1
                
                # Previous button
                elif self.prev_button.collidepoint(event.pos) and self.current_page > 0:
                    self.current_page -= 1
                
                # Skip button
                elif self.skip_button.collidepoint(event.pos):
                    self.finished = True
                    self._was_skipped = True
                    return True
        
        elif event.type == pygame.KEYDOWN:
            # Right arrow or Space - next page
            if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                if self.current_page >= len(self.pages) - 1:
                    self.finished = True
                    return True
                else:
                    self.current_page += 1
            
            # Left arrow - previous page
            elif event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
            
            # Escape - skip tutorial
            elif event.key == pygame.K_ESCAPE:
                self.finished = True
                self._was_skipped = True
                return True
        
        return False
    
    def reset(self):
        """Reset tutorial to first page"""
        self.current_page = 0
        self.finished = False
    
    def set_skip_returns_to_game(self, returns_to_game=True):
        """
        Set whether skipping tutorial returns to game or not
        
        Args:
            returns_to_game: If True, skip button returns to game instead of finishing tutorial
        """
        self.skip_returns_to_game = returns_to_game
    
    def is_skipped(self):
        """Check if tutorial was skipped (vs completed)"""
        return hasattr(self, '_was_skipped') and self._was_skipped


# Test the tutorial system
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Tutorial Test")
    clock = pygame.time.Clock()
    
    tutorial = Tutorial(screen)
    
    print("=" * 60)
    print("Tutorial System - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  LEFT/RIGHT arrows: Navigate pages")
    print("  SPACE: Next page")
    print("  ESC: Skip tutorial")
    print("  Mouse: Click buttons")
    print("=" * 60)
    
    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if tutorial.handle_event(event):
                print("Tutorial finished!")
                running = False
        
        tutorial.draw()
        pygame.display.flip()
    
    pygame.quit()
