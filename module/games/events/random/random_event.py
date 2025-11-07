
"""
Random Card Mini-Game
Occurs at blocks: 4, 8, 12, 16, 19, 23, 26, 29, 33, 36, 39, 43, 45, 48, 52, 56
Players draw one random card from three face-down cards.
"""
import pygame
import os
import sys

# Import random module from stdlib before any path manipulation
from random import shuffle as random_shuffle


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


class RandomCard:
    """Random Card mini-game for special event spaces"""
    
    # Game states
    STATE_CHOOSING = "choosing"  # Player chooses a card
    STATE_REVEALING = "revealing"  # Card flips and reveals
    STATE_RESULT = "result"  # Show result and effect
    
    # Card configuration for each block
    BLOCK_CARDS = {
        4: ["bad", "warp-10", "warp-6"],
        8: ["good", "warp-20", "warp-14"],
        12: ["warp-6", "good", "warp-14"],
        16: ["warp-2", "bad", "warp-20"],
        19: ["warp-2", "warp-27", "good"],
        23: ["good", "warp-20", "warp-14"],
        26: ["warp-2", "good", "warp-27"],
        29: ["bad", "good", "warp-6"],
        33: ["warp-6", "bad", "warp-10"],
        36: ["bad", "warp-2", "warp-20"],
        39: ["good", "warp-14", "warp-6"],
        43: ["good", "warp-20", "warp-14"],
        45: ["bad", "good", "warp-27"],
        48: ["warp-2", "bad", "warp-20"],
        52: ["warp-2", "good", "warp-27"],
        56: ["bad", "warp-14", "warp-20"],
    }
    
    def __init__(self, screen, block_number):
        """
        Initialize the Random Card game
        
        Args:
            screen: Pygame display surface
            block_number: The block number where this event occurs
        """
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 832
        self.block_number = block_number
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        
        # Game state
        self.state = self.STATE_CHOOSING
        self.chosen_card_index = None
        self.revealed_card = None
        self.card_pool = []
        
        # Setup card pool for this block
        self.setup_card_pool()
        
        # Fonts
        self.title_font = SUBTITLE_FONT  # 48pt regular
        self.text_font = TEXT_FONT
        
        # Load images
        self.load_images()
        
        # Create card buttons (3 face-down cards)
        self.create_card_buttons()
        
        # Hover states
        self.hovered_card = None
        
        # Animation state
        self.reveal_timer = 0
        self.reveal_duration = 1200  # 1.2 second flip animation (slightly longer for smoother feel)
    
    def ease_in_out_cubic(self, t):
        """Smooth easing function for animations (cubic ease-in-out)"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
        
    def setup_card_pool(self):
        """Setup the card pool for this block and shuffle"""
        if self.block_number in self.BLOCK_CARDS:
            self.card_pool = self.BLOCK_CARDS[self.block_number].copy()
            random_shuffle(self.card_pool)
        else:
            # Default fallback
            self.card_pool = ["good", "bad", "warp-6"]
            random_shuffle(self.card_pool)
    
    def load_images(self):
        """Load background and card images"""
        # Get absolute path to assets folder
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        
        # Load background from assets/scene/empty/{block_number}.png
        empty_path = os.path.join(base_path, 'assets', 'scene', 'empty', f'{self.block_number}.png')
        if os.path.exists(empty_path):
            img = pygame.image.load(empty_path)
            self.background = pygame.transform.scale(img, (self.screen_width, self.screen_height))
            # Create semi-transparent overlay
            self.background_overlay = self.background.copy()
            self.background_overlay.set_alpha(153)  # 60% opacity (255 * 0.6)
        else:
            print(f"Warning: {empty_path} not found")
            self.background = None
            self.background_overlay = None
        
        # Load card back image with better scaling
        card_back_path = os.path.join(base_path, 'assets', 'random-card', 'random-back.png')
        if os.path.exists(card_back_path):
            img = pygame.image.load(card_back_path)
            # Scale card to match the choosing size (276x429)
            self.card_back = pygame.transform.smoothscale(img, (276, 429))
        else:
            print(f"Warning: {card_back_path} not found")
            self.card_back = None
        
        # Load all possible card face images
        self.card_faces = {}
        card_types = ["good", "bad", "warp-2", "warp-6", "warp-10", "warp-14", "warp-20", "warp-27"]
        
        for card_type in card_types:
            card_path = os.path.join(base_path, 'assets', 'random-card', f'{card_type}.png')
            if os.path.exists(card_path):
                img = pygame.image.load(card_path)
                # Scale card faces to same size as card back (276x429)
                self.card_faces[card_type] = pygame.transform.smoothscale(img, (276, 429))
                print(f"Loaded card: {card_type}")
            else:
                print(f"Warning: {card_path} not found")
                self.card_faces[card_type] = None
        
        # Create white opacity mask
        self.white_mask = pygame.Surface((self.screen_width, self.screen_height))
        self.white_mask.fill((255, 255, 255))
        self.white_mask.set_alpha(128)  # 50% opacity white overlay
    
    def create_card_buttons(self):
        """Create interactive buttons for 3 cards"""
        self.card_buttons = []
        
        card_width = 276
        card_height = 429
        card_spacing = 80
        total_width = (card_width * 3) + (card_spacing * 2)
        start_x = (self.screen_width - total_width) // 2
        center_y = self.screen_height // 2 + 30
        
        for i in range(3):
            x = start_x + (i * (card_width + card_spacing))
            
            card_rect = pygame.Rect(x, center_y - card_height // 2, card_width, card_height)
            
            self.card_buttons.append({
                'rect': card_rect,
                'index': i,
                'card_type': self.card_pool[i] if i < len(self.card_pool) else "good"
            })
    
    def draw_choosing(self):
        """Draw the choosing screen with 3 face-down cards"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((245, 235, 220))
        
        # Draw white opacity mask
        self.screen.blit(self.white_mask, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("Draw one random card", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Draw 3 face-down cards
        for card_data in self.card_buttons:
            rect = card_data['rect']
            is_hovered = self.hovered_card == card_data['index']
            
            if self.card_back:
                if is_hovered:
                    # Scale up slightly when hovered (10% bigger)
                    scaled_card = pygame.transform.smoothscale(self.card_back, (304, 472))
                    card_rect = scaled_card.get_rect(center=rect.center)
                    self.screen.blit(scaled_card, card_rect)
                else:
                    self.screen.blit(self.card_back, rect)
            else:
                # Fallback: draw colored rectangle
                color = (220, 180, 130) if is_hovered else (200, 160, 110)
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                pygame.draw.rect(self.screen, self.BLACK, rect, 3, border_radius=10)
    
    def draw_revealing(self):
        """Draw the revealing animation (card flip)"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((245, 235, 220))
        
        # Draw white opacity mask
        self.screen.blit(self.white_mask, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("Draw one random card", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Calculate flip progress (0.0 to 1.0)
        elapsed = pygame.time.get_ticks() - self.reveal_timer
        raw_progress = min(elapsed / self.reveal_duration, 1.0)
        
        # Apply easing for smoother animation
        progress = self.ease_in_out_cubic(raw_progress)
        
        # Draw all cards
        for i, card_data in enumerate(self.card_buttons):
            rect = card_data['rect']
            
            if i == self.chosen_card_index:
                # Animate the chosen card flipping with smooth easing
                if progress < 0.5:
                    # First half: shrink horizontally (showing back)
                    scale_x = 1.0 - (progress * 2)
                    if self.card_back:
                        scaled_w = int(276 * scale_x)
                        if scaled_w > 0:
                            scaled_card = pygame.transform.smoothscale(self.card_back, (scaled_w, 429))
                            card_rect = scaled_card.get_rect(center=rect.center)
                            self.screen.blit(scaled_card, card_rect)
                else:
                    # Second half: expand horizontally (showing face)
                    scale_x = (progress - 0.5) * 2
                    card_face = self.card_faces.get(card_data['card_type'])
                    if card_face:
                        scaled_w = int(276 * scale_x)
                        if scaled_w > 0:
                            # Card face has same size as card back (276x429)
                            scaled_card = pygame.transform.smoothscale(card_face, (scaled_w, 429))
                            card_rect = scaled_card.get_rect(center=rect.center)
                            self.screen.blit(scaled_card, card_rect)
            else:
                # Draw other cards face-down and slightly dimmed
                if self.card_back:
                    dimmed_card = self.card_back.copy()
                    dimmed_card.set_alpha(100)  # More dimmed (about 40% opacity)
                    self.screen.blit(dimmed_card, rect)
    
    def draw_result(self):
        """Draw the result screen showing the revealed card"""
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((245, 235, 220))
        
        # Draw white opacity mask
        self.screen.blit(self.white_mask, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("Your Card", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title_text, title_rect)
        
        # Draw the revealed card in the center with larger size (345x536)
        chosen_card = self.card_buttons[self.chosen_card_index]
        card_face = self.card_faces.get(chosen_card['card_type'])
        
        if card_face:
            # Scale up the card for result display
            large_card = pygame.transform.smoothscale(card_face, (345, 536))
            # Center the card on screen
            card_rect = large_card.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
            self.screen.blit(large_card, card_rect)
        
        # Add instruction text at bottom
        instruction_text = self.text_font.render("Press SPACE or CLICK to continue", True, self.BLACK)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw(self):
        """Main draw method"""
        if self.state == self.STATE_CHOOSING:
            self.draw_choosing()
        elif self.state == self.STATE_REVEALING:
            self.draw_revealing()
        elif self.state == self.STATE_RESULT:
            self.draw_result()
    
    def parse_card_effect(self, card_type):
        """
        Parse card type and return effect
        
        Args:
            card_type: Card type (e.g., "good", "bad", "warp-10")
            
        Returns:
            dict: {"type": "good"/"bad"/"warp", "value": block_number or None}
        """
        if card_type == "good":
            return {"type": "good", "value": None}
        elif card_type == "bad":
            return {"type": "bad", "value": None}
        elif card_type.startswith("warp-"):
            # Extract block number from card name (e.g., "warp-10" -> 10)
            block_number = int(card_type.split("-")[1])
            print(f"Random Card: {card_type} -> Warp to block {block_number}")
            return {"type": "warp", "value": block_number}
        else:
            return {"type": "unknown", "value": None}
    
    def update(self):
        """Update game state"""
        if self.state == self.STATE_REVEALING:
            # Check if reveal animation is complete
            elapsed = pygame.time.get_ticks() - self.reveal_timer
            if elapsed >= self.reveal_duration:
                self.state = self.STATE_RESULT
    
    def handle_event(self, event):
        """
        Handle game events
        
        Args:
            event: Pygame event
            
        Returns:
            dict or None: Game result if complete, None otherwise
                         {"effect": {"type": "good"/"bad"/"warp", "value": warp_amount}}
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered_card = None
            
            if self.state == self.STATE_CHOOSING:
                for card_data in self.card_buttons:
                    if card_data['rect'].collidepoint(event.pos):
                        self.hovered_card = card_data['index']
                        break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Choosing state - select a card
                if self.state == self.STATE_CHOOSING:
                    for card_data in self.card_buttons:
                        if card_data['rect'].collidepoint(event.pos):
                            self.chosen_card_index = card_data['index']
                            self.revealed_card = card_data['card_type']
                            self.state = self.STATE_REVEALING
                            self.reveal_timer = pygame.time.get_ticks()
                            return None
                
                # Result state - click to continue
                elif self.state == self.STATE_RESULT:
                    effect = self.parse_card_effect(self.revealed_card)
                    return {
                        "effect": effect
                    }
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Result state - press SPACE to continue
                if self.state == self.STATE_RESULT:
                    effect = self.parse_card_effect(self.revealed_card)
                    return {
                        "effect": effect
                    }
        
        return None


