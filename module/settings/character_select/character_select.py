"""
Character Selection Screen
Allows players to choose their elephant character with animations and effects
"""
import pygame
import os
import math
import json
from constant.fonts import (
    CHARACTER_TITLE_FONT,
    CHARACTER_NAME_FONT,
    CHARACTER_INTRO_FONT,
    CHARACTER_INSTRUCTION_FONT
)


class CharacterSelect:
    """Character selection screen with 4 elephant characters"""
    
    # Character data will be loaded from JSON
    CHARACTERS = []
    
    @staticmethod
    def load_characters():
        """Load character data from characters.json file"""
        json_path = os.path.join(os.path.dirname(__file__), 'characters.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert color arrays to tuples
                characters = data.get('characters', [])
                for char in characters:
                    if 'color' in char and isinstance(char['color'], list):
                        char['color'] = tuple(char['color'])
                return characters
        except Exception as e:
            print(f"Error loading characters.json: {e}")
            # Fallback to default character
            return [{
                'id': 1,
                'name': 'Plai Dum – The Gentle Giant',
                'intro': 'A kind-hearted young elephant who loves nature and believes friendship can overcome any obstacle.',
                'image': 'elephant-1.png',
                'color': (150, 150, 150)
            }]
    
    def __init__(self, screen):
        """
        Initialize character selection screen
        
        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Load character data from JSON
        CharacterSelect.CHARACTERS = CharacterSelect.load_characters()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (200, 155, 91)
        self.DARK_GOLD = (168, 107, 39)
        
        # State
        self.selected_character = None
        self.confirmed = False
        self.hovered_character = None
        
        # Animation state
        self.animation_time = 0
        # Create pulse offsets based on number of characters
        self.pulse_offset = [i * 0.5 for i in range(len(self.CHARACTERS))]
        
        # Load character images
        self.character_images = {}
        self.load_character_images()
        
        # Load background image
        self.background_image = None
        self.load_background()
        
        # Setup fonts from centralized fonts module
        self.title_font = CHARACTER_TITLE_FONT
        self.name_font = CHARACTER_NAME_FONT
        self.intro_font = CHARACTER_INTRO_FONT
        self.instruction_font = CHARACTER_INSTRUCTION_FONT
        
        # Calculate card positions (vertical layout, cards in a row)
        self.card_width = 260
        self.card_height = 600
        self.card_spacing = 30
        self.setup_card_positions()
        
    def load_character_images(self):
        """Load all character images from assets/main-character"""
        assets_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'assets', 'main-character'
        )
        
        for char in self.CHARACTERS:
            img_path = os.path.join(assets_path, char['image'])
            if os.path.exists(img_path):
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    # Scale to fit in card (220x220 for image area)
                    scaled_img = pygame.transform.smoothscale(img, (220, 220))
                    self.character_images[char['id']] = scaled_img
                except Exception as e:
                    print(f"Error loading {char['image']}: {e}")
                    self.character_images[char['id']] = None
            else:
                print(f"Warning: {char['image']} not found at {img_path}")
                self.character_images[char['id']] = None
    
    def load_background(self):
        """Load background image from assets/main-character"""
        bg_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'assets', 'main-character',
            'main_character_bg.png'
        )
        
        if os.path.exists(bg_path):
            try:
                self.background_image = pygame.image.load(bg_path).convert()
                # Scale to fit screen
                self.background_image = pygame.transform.scale(
                    self.background_image,
                    (self.screen_width, self.screen_height)
                )
            except Exception as e:
                print(f"Error loading main_character_bg.png: {e}")
                self.background_image = None
        else:
            print(f"Warning: main_character_bg.png not found at {bg_path}")
            self.background_image = None
    
    def setup_card_positions(self):
        """Calculate positions for character cards"""
        total_width = (self.card_width * 4) + (self.card_spacing * 3)
        start_x = (self.screen_width - total_width) // 2
        card_y = 150  # Fixed y position for all cards
        
        self.card_rects = []
        for i in range(4):
            x = start_x + (i * (self.card_width + self.card_spacing))
            rect = pygame.Rect(x, card_y, self.card_width, self.card_height)
            self.card_rects.append(rect)
    
    def update(self):
        """Update animation state"""
        self.animation_time += 0.05  # Animation speed
        if self.animation_time > math.pi * 2:
            self.animation_time = 0
    
    def get_pulse_scale(self, index):
        """Get pulse scale for animation"""
        offset = self.pulse_offset[index]
        pulse = math.sin(self.animation_time + offset) * 0.03 + 1.0  # Subtle pulse
        return pulse
    
    def get_hover_lift(self, index):
        """Get vertical lift amount for hovered card"""
        if self.hovered_character == index:
            return -10  # Lift up by 10 pixels
        return 0
    
    def draw_card(self, index, char_data, rect):
        """Draw a character card with animations"""
        # Calculate animations
        pulse = self.get_pulse_scale(index)
        lift = self.get_hover_lift(index)
        
        # Adjust rect for lift
        display_rect = rect.copy()
        display_rect.y += lift
        
        # Determine if selected or hovered
        is_selected = (self.selected_character == index)
        is_hovered = (self.hovered_character == index)
        
        # Card background with glow effect
        if is_selected:
            # Draw glow for selected card
            glow_rect = display_rect.inflate(20, 20)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.GOLD, 100), glow_surface.get_rect(), border_radius=20)
            self.screen.blit(glow_surface, glow_rect)
        elif is_hovered:
            # Draw subtle glow for hovered card
            glow_rect = display_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.WHITE, 80), glow_surface.get_rect(), border_radius=20)
            self.screen.blit(glow_surface, glow_rect)
        
        # Main card background
        card_color = (40, 40, 50) if not is_selected else (60, 50, 40)
        pygame.draw.rect(self.screen, card_color, display_rect, border_radius=15)
        
        # Card border
        border_color = self.GOLD if is_selected else self.WHITE
        border_width = 4 if is_selected else 2
        pygame.draw.rect(self.screen, border_color, display_rect, border_width, border_radius=15)
        
        # Character accent color bar at top
        accent_rect = pygame.Rect(display_rect.x + 10, display_rect.y + 10, display_rect.width - 20, 8)
        pygame.draw.rect(self.screen, char_data['color'], accent_rect, border_radius=4)
        
        # Character image (with pulse animation)
        if self.character_images.get(char_data['id']):
            img = self.character_images[char_data['id']]
            img_rect = img.get_rect(centerx=display_rect.centerx, top=display_rect.top + 80)
            
            # Apply pulse scale
            if is_selected or is_hovered:
                scaled_size = (int(220 * pulse), int(220 * pulse))
                pulsed_img = pygame.transform.smoothscale(img, scaled_size)
                img_rect = pulsed_img.get_rect(centerx=display_rect.centerx, top=display_rect.top + 80)
                self.screen.blit(pulsed_img, img_rect)
            else:
                self.screen.blit(img, img_rect)
        else:
            # Fallback: draw placeholder circle
            pygame.draw.circle(
                self.screen,
                char_data['color'],
                (display_rect.centerx, display_rect.top + 190),
                80
            )
        
        # Character name (word wrap)
        name_y = display_rect.top + 320
        self.draw_wrapped_text(
            char_data['name'],
            self.name_font,
            self.WHITE,
            display_rect.x + 10,
            name_y,
            display_rect.width - 20,
            line_spacing=0
        )
        
        # Character intro (word wrap)
        intro_y = display_rect.top + 410
        self.draw_wrapped_text(
            char_data['intro'],
            self.intro_font,
            (200, 200, 200),
            display_rect.x + 10,
            intro_y,
            display_rect.width - 20,
            line_spacing=0
        )
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width, line_spacing=8):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        current_y = y
        for line in lines:
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(centerx=x + max_width // 2, top=current_y)
            self.screen.blit(line_surface, line_rect)
            current_y += line_surface.get_height() + line_spacing
    
    def draw(self):
        """Draw the character selection screen"""
        # Draw background image or fallback to gradient
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Background gradient (fallback)
            for y in range(self.screen_height):
                color_value = int(20 + (y / self.screen_height) * 30)
                pygame.draw.line(
                    self.screen,
                    (color_value, color_value, color_value + 10),
                    (0, y),
                    (self.screen_width, y)
                )
        
        # Title
        title_text = self.title_font.render("Choose Your Guardian", True, self.DARK_GOLD)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 60))
        
        # Title shadow
        shadow_text = self.title_font.render("Choose Your Guardian", True, self.BLACK)
        shadow_rect = shadow_text.get_rect(center=(self.screen_width // 2 + 3, 63))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Draw character cards
        for i, char_data in enumerate(self.CHARACTERS):
            self.draw_card(i, char_data, self.card_rects[i])
        
        # Instructions at bottom
        if self.selected_character is None:
            instruction = "Click on a character to select • ESC to quit"
        else:
            instruction = "Click again to confirm • Click another to change • ESC to cancel"
        
        instruction_text = self.instruction_font.render(instruction, True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        
    
    def handle_event(self, event):
        """
        Handle character selection events
        
        Args:
            event: Pygame event
            
        Returns:
            dict: {'confirmed': True, 'character_id': int, 'character_data': dict} if confirmed,
                  None if still selecting
        """
        if event.type == pygame.MOUSEMOTION:
            # Check which card is hovered
            self.hovered_character = None
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(event.pos):
                    self.hovered_character = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(event.pos):
                        if self.selected_character == i:
                            # Clicked same character again - confirm
                            self.confirmed = True
                            return {
                                'confirmed': True,
                                'character_id': self.CHARACTERS[i]['id'],
                                'character_data': self.CHARACTERS[i].copy()
                            }
                        else:
                            # Select this character
                            self.selected_character = i
                        break
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Cancel selection
                if self.selected_character is not None:
                    self.selected_character = None
                else:
                    # Return to previous screen (handled by main game)
                    return {'cancelled': True}
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Confirm current selection with Enter/Space
                if self.selected_character is not None:
                    i = self.selected_character
                    self.confirmed = True
                    return {
                        'confirmed': True,
                        'character_id': self.CHARACTERS[i]['id'],
                        'character_data': self.CHARACTERS[i].copy()
                    }
        
        return None
    
    def get_selected_character_image_name(self):
        """Get the image filename of selected character"""
        if self.selected_character is not None:
            return self.CHARACTERS[self.selected_character]['image']
        return 'elephant-1.png'  # Default


# Example usage / testing
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Character Selection Test")
    clock = pygame.time.Clock()
    
    character_select = CharacterSelect(screen)
    
    running = True
    print("=" * 60)
    print("Character Selection - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  MOUSE: Hover and click to select")
    print("  ENTER/SPACE: Confirm selection")
    print("  ESC: Cancel selection / Quit")
    print("=" * 60)
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = character_select.handle_event(event)
                if result:
                    if result.get('confirmed'):
                        print(f"\nCharacter selected: {result['character_data']['name']}")
                        print(f"Character ID: {result['character_id']}")
                        print(f"Image file: {result['character_data']['image']}")
                        running = False
                    elif result.get('cancelled'):
                        print("\nSelection cancelled")
                        running = False
        
        character_select.update()
        character_select.draw()
        pygame.display.flip()
    
    pygame.quit()
