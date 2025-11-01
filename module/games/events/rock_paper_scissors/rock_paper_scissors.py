"""
Rock Paper Scissors Mini-Game
Occurs at blocks: 6, 17, 25, 40, 46, 57
"""
import pygame
import os
import sys
import random

# Import fonts robustly: prefer package-style `constant.fonts`, then fall back
# to adding the top-level `constant` directory and importing `fonts`. If both
# fail, provide simple pygame SysFont fallbacks to avoid import errors in tests.
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


class RockPaperScissors:
    """Rock Paper Scissors mini-game for event spaces"""
    
    # Game states
    STATE_INTRO = "intro"
    STATE_PLAYING = "playing"
    STATE_RESULT = "result"  # VS screen showing both choices
    STATE_ROUND_RESULT = "round_result"  # Win/Lose/Draw result screen
    
    # Choices
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissor"
    
    def __init__(self, screen, block_number):
        """
        Initialize the Rock Paper Scissors game
        
        Args:
            screen: Pygame display surface
            block_number: The block number where this event occurs (6, 17, 25, 40, 46, 57)
        """
        
        
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.block_number = block_number
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BUTTON_COLOR = (200, 155, 91)  # #C89B5B
        self.BUTTON_HOVER_COLOR = (220, 175, 111)  # Lighter version for hover
        self.BUTTON_TEXT_COLOR = (75, 42, 12)  # #4B2A0C
        self.BUTTON_BORDER_COLOR = (168, 107, 39)  # #A86B27
        # Default background color used when no bg image is available
        self.BG_COLOR = (245, 235, 220)
        
        
        # Game state
        self.state = self.STATE_INTRO
        self.player_choice = None
        self.opponent_choice = None
        self.result = None  # "win" or "lose" (draw triggers replay)
        self.final_result = None  # Store final result: "win" or "lose"
        
        # Fonts - use centralized font system
        self.title_font = BUTTON_FONT_LARGE
        self.button_font = BUTTON_FONT
        self.text_font = TEXT_FONT
        self.subtitle_font = SUBTITLE_FONT  # 48pt regular (non-bold)
        self.small_font = TEXT_FONT
        
        # Load images
        self.load_images()
        
        # Create buttons for player choices
        self.create_choice_buttons()
        
        # Continue button (for result screen)
        self.continue_button = None
        self.create_continue_button()
        
        # Hover states
        self.hovered_button = None
        
    def load_images(self):
        """Load background images, component images, and result images"""
        # Load intro background (e.g., 6-intro.png)
        intro_path = f"assets/scene/event/rock-paper-scissors/blocks/{self.block_number}-intro.png"
        if os.path.exists(intro_path):
            img = pygame.image.load(intro_path)
            self.intro_background = pygame.transform.scale(img, (self.screen_width, self.screen_height))
        else:
            print(f"Warning: {intro_path} not found")
            self.intro_background = None
        
        # Load playing background (e.g., 6-bg.png) - used during gameplay with NPC
        bg_path = f"assets/scene/event/rock-paper-scissors/blocks/{self.block_number}-bg.png"
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(img, (self.screen_width, self.screen_height))
        else:
            print(f"Warning: {bg_path} not found - using solid color")
            self.background = None
        

        
        # Load component images (player choices - rock, paper, scissors)
        self.images = {
            self.ROCK: None,
            self.PAPER: None,
            self.SCISSORS: None
        }
        
        components_path = "assets/scene/event/rock-paper-scissors/components"
        for choice in [self.ROCK, self.PAPER, self.SCISSORS]:
            img_path = os.path.join(components_path, f"{choice}.png")
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                # Scale to reasonable size (120x120)
                self.images[choice] = pygame.transform.scale(img, (120, 120))
            else:
                print(f"Warning: {img_path} not found - game needs component images!")
                self.images[choice] = None
        
        # Load result images (e.g., 6-win.png, 6-lose.png, 6-draw.png)
        self.result_images = {
            "win": None,
            "lose": None,
            "draw": None
        }
        
        for result in ["win", "lose", "draw"]:
            img_path = f"assets/scene/event/rock-paper-scissors/blocks/{self.block_number}-{result}.png"
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                # Scale to fill screen
                self.result_images[result] = pygame.transform.scale(img, (self.screen_width, self.screen_height))
            else:
                print(f"Warning: {img_path} not found")
                
    def create_choice_buttons(self):
        """Create interactive buttons for rock, paper, scissors"""
        self.choice_buttons = {}
        
        button_spacing = 220
        total_width = button_spacing * 2
        start_x = (self.screen_width - total_width) // 2
        center_y = self.screen_height // 2 + 100
        
        choices = [self.ROCK, self.PAPER, self.SCISSORS]
        for i, choice in enumerate(choices):
            x = start_x + (i * button_spacing)
            
            # Button rect for collision detection (circular hitbox)
            button_rect = pygame.Rect(0, 0, 140, 140)
            button_rect.centerx = x
            button_rect.centery = center_y
            
            self.choice_buttons[choice] = {
                'rect': button_rect,
                'image': self.images[choice],
                'label': choice.upper()
            }
    
    def create_continue_button(self):
        """Create continue button for result screen"""
        button_width = 250
        button_height = 70
        self.continue_button = pygame.Rect(0, 0, button_width, button_height)
        self.continue_button.center = (self.screen_width // 2, self.screen_height - 100)
    
    def draw_intro(self):
        """Draw the introduction screen with intro background"""
        # Draw intro background image if available
        if self.intro_background:
            self.screen.blit(self.intro_background, (0, 0))
        elif self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((245, 235, 220))
        
        # Add instruction text at bottom
        instruction_text = self.small_font.render("Press SPACE or CLICK to continue", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_playing(self):
        """Draw the game playing screen with background and choice buttons"""
        # Draw background image
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)
        
        # Draw "Choose your hand wisely" text at the top
        title_text = self.subtitle_font.render("Choose your hand wisely", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw choice buttons
        for choice, button_data in self.choice_buttons.items():
            rect = button_data['rect']
            image = button_data['image']
            
            # Highlight if hovered
            is_hovered = self.hovered_button == choice
            
            # Draw the component image
            if image:
                if is_hovered:
                    # Scale up slightly when hovered
                    scaled_img = pygame.transform.scale(image, (140, 140))
                    image_rect = scaled_img.get_rect(center=rect.center)
                    self.screen.blit(scaled_img, image_rect)
                else:
                    image_rect = image.get_rect(center=rect.center)
                    self.screen.blit(image, image_rect)
    
    def draw_result(self):
        """Draw the VS screen with both choices"""
        # Show the VS screen (background with both choices)
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)
        
        # Draw "Choose your hand wisely" text at the top
        title_text = self.subtitle_font.render("Choose your hand wisely", True, self.BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Display choices side by side with VS in the middle
        player_x = self.screen_width // 3
        opponent_x = 2 * self.screen_width // 3
        choice_y = self.screen_height // 2 + 50
        
        # Player choice (left)
        if self.images[self.player_choice]:
            player_img_rect = self.images[self.player_choice].get_rect(center=(player_x, choice_y))
            self.screen.blit(self.images[self.player_choice], player_img_rect)
        
        # VS text/image in the middle
        vs_image_path = "assets/scene/event/rock-paper-scissors/components/vs.png"
        if os.path.exists(vs_image_path):
            vs_img = pygame.image.load(vs_image_path)
            vs_rect = vs_img.get_rect(center=(self.screen_width // 2, choice_y))
            self.screen.blit(vs_img, vs_rect)
        else:
            # Fallback to text VS
            vs_text = self.title_font.render("VS", True, self.BLACK)
            vs_rect = vs_text.get_rect(center=(self.screen_width // 2, choice_y))
            self.screen.blit(vs_text, vs_rect)
        
        # Opponent choice (right)
        if self.images[self.opponent_choice]:
            opponent_img_rect = self.images[self.opponent_choice].get_rect(center=(opponent_x, choice_y))
            self.screen.blit(self.images[self.opponent_choice], opponent_img_rect)
        
        # Add instruction text at bottom
        instruction_text = self.small_font.render("Press SPACE or CLICK to continue", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_round_result(self):
        """Draw the round result screen with win/lose/draw image"""
        # Display full-screen result image (e.g., 6-win.png, 6-lose.png, 6-draw.png)
        if self.result_images[self.result]:
            self.screen.blit(self.result_images[self.result], (0, 0))
        else:
            # Fallback if image not found
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.BG_COLOR)
            
            # Show text result
            result_text = self.title_font.render(f"{self.result.upper()}!", True, self.BLACK)
            result_rect = result_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(result_text, result_rect)
        
        # Add instruction text at bottom only for win/lose (not draw since it auto-replays)
        if self.result != "draw":
            instruction_text = self.small_font.render("Press SPACE or CLICK to continue", True, self.WHITE)
            instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
            self.screen.blit(instruction_text, instruction_rect)
    

    
    def draw(self):
        """Main draw method"""
        if self.state == self.STATE_INTRO:
            self.draw_intro()
        elif self.state == self.STATE_PLAYING:
            self.draw_playing()
        elif self.state == self.STATE_RESULT:
            self.draw_result()  # VS screen
        elif self.state == self.STATE_ROUND_RESULT:
            self.draw_round_result()  # Win/Lose/Draw screen
    
    def determine_winner(self, player, opponent):
        """
        Determine the winner of a round
        
        Args:
            player: Player's choice (rock/paper/scissors)
            opponent: Opponent's choice (rock/paper/scissors)
            
        Returns:
            str: "win", "lose", or "draw"
        """
        if player == opponent:
            return "draw"
        
        winning_combinations = {
            self.ROCK: self.SCISSORS,
            self.PAPER: self.ROCK,
            self.SCISSORS: self.PAPER
        }
        
        if winning_combinations[player] == opponent:
            return "win"
        else:
            return "lose"
    
    def play_round(self, player_choice):
        """
        Play a round with the given player choice
        
        Args:
            player_choice: Player's choice (rock/paper/scissors)
        """
        self.player_choice = player_choice
        self.opponent_choice = random.choice([self.ROCK, self.PAPER, self.SCISSORS])
        self.result = self.determine_winner(self.player_choice, self.opponent_choice)
        
        # Go to VS screen first
        self.state = self.STATE_RESULT
    
    def handle_event(self, event):
        """
        Handle game events
        
        Args:
            event: Pygame event
            
        Returns:
            dict or None: Game result if complete, None otherwise
                         {"result": "win"/"lose", "rewards": {...}}
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered_button = None
            
            if self.state == self.STATE_PLAYING:
                for choice, button_data in self.choice_buttons.items():
                    if button_data['rect'].collidepoint(event.pos):
                        self.hovered_button = choice
                        break
            
            elif self.state in [self.STATE_RESULT, self.STATE_ROUND_RESULT]:
                if self.continue_button.collidepoint(event.pos):
                    self.hovered_button = "continue"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Intro screen - press SPACE to start
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    return None
                
                # VS Result screen - press SPACE to continue
                elif self.state == self.STATE_RESULT:
                    self.state = self.STATE_ROUND_RESULT
                    return None
                
                # Round result screen - handle win/lose/draw
                elif self.state == self.STATE_ROUND_RESULT:
                    if self.result == "draw":
                        # Draw: press SPACE to replay
                        self.state = self.STATE_PLAYING
                        return None
                    else:
                        # Win or Lose: press SPACE to return result
                        self.final_result = self.result
                        
                        return {
                            "result": self.result  # "win" or "lose"
                        }
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                
                # Intro screen - click anywhere to start
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    return None
                
                # Playing screen - choose rock/paper/scissors
                elif self.state == self.STATE_PLAYING:
                    for choice, button_data in self.choice_buttons.items():
                        if button_data['rect'].collidepoint(event.pos):
                            self.play_round(choice)
                            return None
                
                # VS Result screen - click anywhere to continue
                elif self.state == self.STATE_RESULT:
                    self.state = self.STATE_ROUND_RESULT
                    return None
                
                # Round result screen - handle win/lose/draw
                elif self.state == self.STATE_ROUND_RESULT:
                    if self.result == "draw":
                        # Draw: click anywhere to replay
                        self.state = self.STATE_PLAYING
                        return None
                    else:
                        # Win or Lose: click anywhere to return result
                        self.final_result = self.result
                        
                        return {
                            "result": self.result  # "win" or "lose"
                        }
        
        return None
    
    def update_screen_size(self, screen):
        """Update game for new screen size"""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.create_choice_buttons()
        self.create_continue_button()
