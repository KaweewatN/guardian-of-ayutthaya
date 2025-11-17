"""
Scene Viewer
Displays a sequence of scene images with navigation
Used when player lands on a block to show story scenes
"""
import pygame
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from constant.fonts import BUTTON_FONT_SMALL, TEXT_FONT


class SceneViewer:
    """
    Displays a sequence of scene images.
    Automatically transitions between scenes with a timer.
    """
    
    def __init__(self, screen, scenes_list, block_number=1, scene_duration=5000):
        """
        Initialize scene viewer.
        
        Args:
            screen: Pygame display surface
            scenes_list: List of scene dictionaries from block_scenes_config
                        Each dict has: {'folder': str, 'filename': str, 'type': str}
            block_number: Current block number for displaying place name
            scene_duration: Duration in milliseconds to show each scene (default: 5000 = 5 seconds)
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Block and place info
        self.block_number = block_number
        self.place_names = self.load_place_names()
        
        # Scene data
        self.scenes_list = scenes_list
        self.current_scene_index = 0
        self.total_scenes = len(scenes_list)
        
        # Load all scene images
        self.scene_images = []
        self.load_scenes()
        
        # Navigation state
        self.is_finished = False
        
        # Auto-transition timer
        self.scene_duration = scene_duration
        self.scene_start_time = pygame.time.get_ticks()
        
        # Debouncing - prevent rapid input
        self.last_input_time = 0
        self.input_cooldown = 300  # 300ms cooldown between inputs
        
        # Smaller font for UI text
        self.small_font = TEXT_FONT
    
    def load_place_names(self):
        """Load place names from place.json file."""
        place_file = os.path.join(os.path.dirname(__file__), 'place.json')
        try:
            with open(place_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load place.json: {e}")
            return {}
    
    def load_scenes(self):
        """Load all scene images from assets/scene folder."""
        assets_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'assets', 'scene'
        )
        
        for scene_info in self.scenes_list:
            folder = scene_info['folder']
            filename = scene_info['filename']
            scene_path = os.path.join(assets_path, folder, filename)
            
            if os.path.exists(scene_path):
                try:
                    img = pygame.image.load(scene_path)
                    # Scale to fit screen while maintaining aspect ratio
                    img = self.scale_image_to_fit(img)
                    self.scene_images.append(img)
                except Exception as e:
                    print(f"Error loading scene {scene_path}: {e}")
                    # Create a placeholder surface
                    self.scene_images.append(self.create_placeholder(scene_info))
            else:
                print(f"Warning: Scene not found: {scene_path}")
                self.scene_images.append(self.create_placeholder(scene_info))
    
    def scale_image_to_fit(self, image):
        """Scale image to fit screen while maintaining aspect ratio."""
        img_width, img_height = image.get_size()
        
        # Calculate scaling to fit within screen
        scale_x = self.screen_width / img_width
        scale_y = self.screen_height / img_height
        scale = min(scale_x, scale_y)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        return pygame.transform.scale(image, (new_width, new_height))
    
    def create_placeholder(self, scene_info):
        """Create a placeholder surface when image is missing."""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        surface.fill((50, 50, 50))
        
        # Draw text
        font = pygame.font.SysFont('Arial', 36)
        text = font.render(f"Scene not found:", True, (255, 255, 255))
        text2 = font.render(f"{scene_info['folder']}/{scene_info['filename']}", True, (200, 200, 200))
        
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 30))
        text_rect2 = text2.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
        
        surface.blit(text, text_rect)
        surface.blit(text2, text_rect2)
        
        return surface
    
    def next_scene(self):
        """Move to next scene or finish if at the end."""
        if self.current_scene_index < self.total_scenes - 1:
            self.current_scene_index += 1
            self.scene_start_time = pygame.time.get_ticks()  # Reset timer for new scene
        else:
            self.is_finished = True
    
    def update(self):
        """Update scene viewer state. Call this every frame."""
        # Check if it's time to advance to next scene
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.scene_start_time
        
        if time_elapsed >= self.scene_duration and not self.is_finished:
            self.next_scene()
    
    def draw(self):
        """Draw the current scene."""
        # Fill background
        self.screen.fill((0, 0, 0))
        
        # Draw current scene image (centered)
        if self.current_scene_index < len(self.scene_images):
            img = self.scene_images[self.current_scene_index]
            img_rect = img.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(img, img_rect)
        
        # Draw UI overlay
        self.draw_ui()
    
    def draw_ui(self):
        """Draw navigation UI elements."""
        # Place name (top right with margin)
        place_name = self.place_names.get(str(self.block_number), "Unknown Place")
        place_text = f"Block {self.block_number}: {place_name}"
        place_surf = self.small_font.render(place_text, True, (255, 255, 255))
        place_rect = place_surf.get_rect()
        place_rect.topright = (self.screen_width - 30, 20)  # 30px margin from top and right
        
        self.screen.blit(place_surf, place_rect)
        
        # Keystroke instructions (center bottom) - smaller text, no background
        instructions = "Press SPACE or ENTER to continue"
        inst_surf = self.small_font.render(instructions, True, (255, 255, 255))
        inst_rect = inst_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(inst_surf, inst_rect)
    
    def handle_event(self, event):
        """
        Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            bool: True if scene viewing is finished, False otherwise
        """
        # Debouncing: check if enough time has passed since last input
        current_time = pygame.time.get_ticks()
        if current_time - self.last_input_time < self.input_cooldown:
            return False  # Ignore input if within cooldown period
        
        if event.type == pygame.KEYDOWN:
            # Next scene or finish with SPACE or ENTER
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.last_input_time = current_time
                self.next_scene()
                return self.is_finished
            # Skip all scenes with ESC
            elif event.key == pygame.K_ESCAPE:
                self.last_input_time = current_time
                self.is_finished = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click anywhere on screen
                self.last_input_time = current_time
                self.next_scene()
                return self.is_finished
        
        return False
    
    def reset(self):
        """Reset viewer to first scene."""
        self.current_scene_index = 0
        self.is_finished = False
        self.scene_start_time = pygame.time.get_ticks()


# Example usage / testing
if __name__ == "__main__":
    import sys
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from block_scenes_config import get_block_scene_sequence
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Scene Viewer Test")
    clock = pygame.time.Clock()
    
    # Test with block 1 scenes
    test_block = 25
    scenes = get_block_scene_sequence(test_block)
    
    print(f"Testing Scene Viewer with Block {test_block}")
    print(f"Scenes to display: {len(scenes)}")
    for scene in scenes:
        print(f"  - {scene['folder']}/{scene['filename']}")
    
    scene_viewer = SceneViewer(screen, scenes)
    
    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                finished = scene_viewer.handle_event(event)
                if finished:
                    print("Scene viewing finished!")
                    running = False
        
        # Update scene viewer (handles auto-transition)
        scene_viewer.update()
        
        # Check if finished after update
        if scene_viewer.is_finished:
            print("Scene viewing finished!")
            running = False
        
        scene_viewer.draw()
        pygame.display.flip()
    
    pygame.quit()
