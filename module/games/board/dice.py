"""
Dice System
Handles dice rolling with animation and integrates with board movement
"""
import pygame
import random
import math
import os
import sys

# Add constant directory to path for fonts import
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import DICE_BUTTON_FONT, TEXT_FONT_BOLD


class Dice:
    """
    Dice rolling system with visual animation.
    Generates random values 1-6 and animates the rolling effect.
    """
    
    def __init__(self, screen, board_block):
        """
        Initialize the dice system.
        
        Args:
            screen: Pygame display surface
            board_block: BoardBlock instance to control character movement
        """
        self.screen = screen
        self.board_block = board_block
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Dice state
        self.current_value = 1
        self.is_rolling = False
        self.roll_result = None
        
        # Animation state
        self.animation_time = 0
        self.animation_duration = 1500  # 1.5 seconds rolling animation in milliseconds
        self.animation_start_time = 0
        
        # Visual settings
        self.dice_size = 120
        self.dice_color = (255, 255, 255)
        self.dot_color = (0, 0, 0)
        self.dice_border_color = (50, 50, 50)
        
        # Button settings
        self.button_rect = None
        self.button_color = (200, 155, 91)  # Gold color
        self.button_hover_color = (230, 185, 121)
        self.button_disabled_color = (150, 150, 150)
        self.button_text_color = (255, 255, 255)
        self.is_button_hovered = False
        
        # Movement state
        self.is_moving = False
        self.steps_remaining = 0
        self.move_delay = 500  # Milliseconds between each step
        self.last_move_time = 0
        
        # Fonts - using centralized font system
        self.button_font = DICE_BUTTON_FONT
        self.result_font = TEXT_FONT_BOLD
        
        # Load dice background image
        self.dice_bg_image = None
        self.load_dice_background()
        
        # Setup UI positions
        self.setup_positions()
    
    def load_dice_background(self):
        """Load dice background image from assets/core folder."""
        bg_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'assets', 'core',
            'dice-bg.png'
        )
        
        if os.path.exists(bg_path):
            try:
                self.dice_bg_image = pygame.image.load(bg_path).convert_alpha()
                print(f"Loaded dice background: dice-bg.png")
            except Exception as e:
                print(f"Error loading dice-bg.png: {e}")
                self.dice_bg_image = None
        else:
            print(f"Warning: dice-bg.png not found at {bg_path}")
            self.dice_bg_image = None
    
    def setup_positions(self):
        """Calculate positions for dice and button on the screen."""
        # Get background dimensions if available
        if self.dice_bg_image:
            bg_width = self.dice_bg_image.get_width()
            bg_height = self.dice_bg_image.get_height()
        else:
            # Default size if no background
            bg_width = 300
            bg_height = 400
        # Position background with 70px padding from right and 520px from top
        self.bg_x = self.screen_width - bg_width - 90  # 70px padding from right
        self.bg_y = 520  # 520px from top
        
        # Center dice within the background (in both x and y)
        self.dice_x = self.bg_x + (bg_width - self.dice_size) // 2
        self.dice_y = self.bg_y + (bg_height - self.dice_size) // 2
        
        # Position button below the background
        button_width = 180
        button_height = 60
        self.button_rect = pygame.Rect(
            self.bg_x + (bg_width - button_width) // 2,  # Center with background
            self.bg_y + bg_height + 20,  # 20px below background
            button_width,
            button_height
        )
    
    def start_roll(self):
        """Start the dice rolling animation."""
        if not self.is_rolling and not self.is_moving:
            self.is_rolling = True
            self.animation_start_time = pygame.time.get_ticks()
            # Pre-determine the final result
            self.roll_result = random.randint(1, 6)
            print(f"Rolling dice... (will land on {self.roll_result})")
    
    def update(self):
        """Update dice animation and movement state."""
        current_time = pygame.time.get_ticks()
        
        # Update rolling animation
        if self.is_rolling:
            elapsed = current_time - self.animation_start_time
            
            if elapsed < self.animation_duration:
                # During rolling: rapidly change displayed value
                # Change value every 100ms for visual effect
                if elapsed % 100 < 50:
                    self.current_value = random.randint(1, 6)
            else:
                # Animation finished: show final result
                self.is_rolling = False
                self.current_value = self.roll_result
                print(f"Dice stopped at: {self.current_value}")
                
                # Start moving the character
                self.start_movement()
        
        # Update character movement
        if self.is_moving and self.steps_remaining > 0:
            if current_time - self.last_move_time >= self.move_delay:
                # Determine if this is the final step
                is_final_step = (self.steps_remaining == 1)
                
                # Move one step (show scenes only on the final step)
                success = self.board_block.move_forward(show_scenes=is_final_step)
                if success:
                    self.steps_remaining -= 1
                    self.last_move_time = current_time
                    print(f"Moved to block {self.board_block.current_block}, steps remaining: {self.steps_remaining}")
                    
                    # Check if movement is complete
                    if self.steps_remaining == 0:
                        self.is_moving = False
                        print(f"Movement complete! Now at block {self.board_block.current_block}")
                else:
                    # Can't move further (reached end of board)
                    self.is_moving = False
                    self.steps_remaining = 0
                    print(f"Reached end of board at block {self.board_block.current_block}")
    
    def start_movement(self):
        """Start moving the character based on dice result."""
        if self.roll_result and self.roll_result > 0:
            self.is_moving = True
            self.steps_remaining = self.roll_result
            self.last_move_time = pygame.time.get_ticks()
            print(f"Starting movement: {self.steps_remaining} steps")
    
    def draw_dice_face(self, value):
        """
        Draw a dice face with dots representing the value.
        
        Args:
            value: Dice value (1-6)
        """
        # Calculate dice rectangle
        dice_rect = pygame.Rect(
            self.dice_x,
            self.dice_y,
            self.dice_size,
            self.dice_size
        )
        
        # Draw dice background
        pygame.draw.rect(self.screen, self.dice_color, dice_rect, border_radius=15)
        
        # Draw dice border
        pygame.draw.rect(self.screen, self.dice_border_color, dice_rect, 3, border_radius=15)
        
        # Draw dots based on value
        center_x = self.dice_x + self.dice_size // 2
        center_y = self.dice_y + self.dice_size // 2
        dot_radius = 10
        offset = 30  # Distance from center
        
        # Dot positions (relative to center)
        dots_config = {
            1: [(0, 0)],  # Center
            2: [(-offset, -offset), (offset, offset)],  # Diagonal
            3: [(-offset, -offset), (0, 0), (offset, offset)],  # Diagonal with center
            4: [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)],  # Corners
            5: [(-offset, -offset), (offset, -offset), (0, 0), (-offset, offset), (offset, offset)],  # Corners + center
            6: [(-offset, -offset), (offset, -offset), (-offset, 0), (offset, 0), (-offset, offset), (offset, offset)]  # 3x2 grid
        }
        
        # Draw dots
        if value in dots_config:
            for dot_x, dot_y in dots_config[value]:
                pygame.draw.circle(
                    self.screen,
                    self.dot_color,
                    (center_x + dot_x, center_y + dot_y),
                    dot_radius
                )
    
    def draw_button(self):
        """Draw the roll dice button."""
        # Determine button state
        can_roll = not self.is_rolling and not self.is_moving
        
        # Choose button color
        if not can_roll:
            color = self.button_disabled_color
        elif self.is_button_hovered and can_roll:
            color = self.button_hover_color
        else:
            color = self.button_color
        
        # Draw button
        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=10)
        
        # Draw button border
        border_color = (255, 255, 255) if can_roll else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, self.button_rect, 3, border_radius=10)
        
        # Draw button text
        if self.is_rolling:
            text = "Rolling..."
        elif self.is_moving:
            text = f"Moving ({self.steps_remaining})"
        else:
            text = "Roll Dice"
        
        text_surface = self.button_font.render(text, True, self.button_text_color)
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_result_text(self):
        """Draw the dice result text above the dice."""
        if not self.is_rolling and self.roll_result is not None:
            if self.is_moving:
                text = f"Moving {self.roll_result} steps"
                color = (100, 200, 100)
            else:
                text = f"Rolled: {self.current_value}"
                color = (50, 50, 50)
            
            text_surface = self.result_font.render(text, True, color)
            text_rect = text_surface.get_rect(
                centerx=self.dice_x + self.dice_size // 2,
                bottom=self.dice_y - 20
            )
            
            # Draw text directly without background
            self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        """Draw the dice and button with background."""
        # Draw background image if available
        if self.dice_bg_image:
            self.screen.blit(self.dice_bg_image, (self.bg_x, self.bg_y))
        
        # Draw dice face (centered within background)
        self.draw_dice_face(self.current_value)
        
        # Draw result text
        self.draw_result_text()
        
        # Draw button
        self.draw_button()
    
    
    def handle_event(self, event):
        """
        Handle mouse events for the dice button.
        
        Args:
            event: Pygame event
            
        Returns:
            dict: Action result or None
        """
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is hovering over button
            self.is_button_hovered = self.button_rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on button
                if self.button_rect.collidepoint(event.pos):
                    # Only allow rolling if not currently rolling or moving
                    if not self.is_rolling and not self.is_moving:
                        self.start_roll()
                        return {'action': 'dice_rolled'}
        
        elif event.type == pygame.KEYDOWN:
            # Allow spacebar to roll dice as well
            if event.key == pygame.K_SPACE:
                if not self.is_rolling and not self.is_moving:
                    self.start_roll()
                    return {'action': 'dice_rolled'}
        
        return None
    
    def reset(self):
        """Reset dice to initial state."""
        self.current_value = 1
        self.is_rolling = False
        self.roll_result = None
        self.is_moving = False
        self.steps_remaining = 0
    
    def get_last_roll(self):
        """Get the result of the last dice roll."""
        return self.roll_result
    
    def is_active(self):
        """Check if dice is currently rolling or character is moving."""
        return self.is_rolling or self.is_moving


# Example usage / testing
if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from board.board_block import BoardBlock
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Dice System Test")
    clock = pygame.time.Clock()
    
    # Create board block system
    board_block = BoardBlock(screen, start_block=1)
    
    # Create dice system
    dice = Dice(screen, board_block)
    
    running = True
    
    print("=" * 60)
    print("Dice System - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  Click 'Roll Dice' button or press SPACE to roll")
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
            
            # Handle dice events
            dice_result = dice.handle_event(event)
            if dice_result:
                print(f"Dice action: {dice_result}")
            
            # Handle board events (when not rolling/moving)
            if not dice.is_active():
                board_block.handle_event(event)
        
        # Update
        board_block.update()
        dice.update()
        
        # Draw
        screen.fill((240, 230, 220))  # Light background
        board_block.draw()
        dice.draw()
        
        pygame.display.flip()
    
    pygame.quit()
