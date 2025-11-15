"""
Event Image Preloader
Preloads all event game images at startup to make events start instantly.
"""
import os
import pygame


class EventImagePreloader:
    """Preload all event game images to improve runtime performance."""
    
    def __init__(self, screen):
        """
        Initialize the preloader.
        
        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Cache for all preloaded images
        self.image_cache = {}
        
        # Track loading progress
        self.total_images = 0
        self.loaded_images = 0
    
    def preload_all_events(self):
        """Preload images for all event games."""
        print("Preloading event images...")
        start_time = pygame.time.get_ticks()
        
        # Preload each event type
        self.preload_rock_paper_scissors()
        self.preload_photo_hunt()
        self.preload_math_event()
        self.preload_random_cards()
        
        elapsed = pygame.time.get_ticks() - start_time
        print(f"✓ Preloaded {self.loaded_images} event images in {elapsed}ms")
    
    def preload_rock_paper_scissors(self):
        """Preload Rock Paper Scissors images for all blocks."""
        blocks = [6, 17, 25, 40, 46, 57]
        base_path = "assets/scene/event/rock-paper-scissors"
        
        for block in blocks:
            # Intro background
            self._load_image(f"rps_{block}_intro", 
                           os.path.join(base_path, "blocks", f"{block}-intro.png"),
                           scale=(self.screen_width, self.screen_height))
            
            # Playing background
            self._load_image(f"rps_{block}_bg",
                           os.path.join(base_path, "blocks", f"{block}-bg.png"),
                           scale=(self.screen_width, self.screen_height))
            
            # Result images
            for result in ["win", "lose", "draw"]:
                self._load_image(f"rps_{block}_{result}",
                               os.path.join(base_path, "blocks", f"{block}-{result}.png"),
                               scale=(self.screen_width, self.screen_height))
        
        # Component images (shared across all blocks)
        for component in ["rock", "paper", "scissor"]:
            self._load_image(f"rps_component_{component}",
                           os.path.join(base_path, "components", f"{component}.png"),
                           scale=(120, 120))
        
        # VS image
        self._load_image("rps_vs",
                       os.path.join(base_path, "components", "vs.png"))
    
    def preload_photo_hunt(self):
        """Preload Photo Hunt images for all blocks."""
        blocks = [22, 34]
        base_path = "assets/scene/event/photo-hunt"
        
        for block in blocks:
            # Before image
            self._load_image(f"photo_hunt_{block}_before",
                           os.path.join(base_path, f"{block}-before.png"),
                           scale=(self.screen_width, self.screen_height))
            
            # After image
            self._load_image(f"photo_hunt_{block}_after",
                           os.path.join(base_path, f"{block}-after.png"),
                           scale=(self.screen_width, self.screen_height))
    
    def preload_math_event(self):
        """Preload Math Event images for all blocks."""
        blocks = [3, 11, 20, 28, 37, 43, 49, 54]
        
        for block in blocks:
            # Intro image
            self._load_image(f"math_{block}_intro",
                           f"assets/scene/event/math/intro/{block}-intro.png",
                           scale=(self.screen_width, self.screen_height))
            
            # Win image
            self._load_image(f"math_{block}_win",
                           f"assets/scene/event/math/win/{block}-win.png",
                           scale=(self.screen_width, self.screen_height))
            
            # Lose image
            self._load_image(f"math_{block}_lose",
                           f"assets/scene/event/math/lose/{block}-lose.png",
                           scale=(self.screen_width, self.screen_height))
        
        # Component images (shared)
        base_path = "assets/scene/event/math/component"
        for i in range(10):  # Numbers 0-9
            self._load_image(f"math_number_{i}",
                           os.path.join(base_path, f"{i}.png"),
                           scale=(80, 80))
        
        # Operators
        for op in ["+", "-", "x"]:
            filename = "plus.png" if op == "+" else "minus.png" if op == "-" else "multiply.png"
            self._load_image(f"math_op_{op}",
                           os.path.join(base_path, filename),
                           scale=(60, 60))
        
        # Equals sign
        self._load_image("math_equals",
                       os.path.join(base_path, "equals.png"),
                       scale=(60, 60))
    
    def preload_random_cards(self):
        """Preload Random Card event images."""
        base_path = "assets/random-card"
        
        # Card types
        cards = [
            "good", "bad",
            "forward-1", "forward-3", "forward-5", "forward-7",
            "backward-2", "backward-4", "backward-6", "backward-8", "backward-12"
        ]
        
        for card in cards:
            self._load_image(f"random_card_{card}",
                           os.path.join(base_path, f"{card}.png"),
                           scale=(self.screen_width, self.screen_height))
    
    def _load_image(self, cache_key, file_path, scale=None):
        """
        Load and cache an image.
        
        Args:
            cache_key: Unique key for caching
            file_path: Path to image file
            scale: Optional (width, height) tuple for scaling
        """
        self.total_images += 1
        
        if not os.path.exists(file_path):
            # Don't warn - some images may not exist for all blocks
            return
        
        try:
            img = pygame.image.load(file_path)
            if scale:
                img = pygame.transform.scale(img, scale)
            else:
                img = img.convert_alpha()
            
            self.image_cache[cache_key] = img
            self.loaded_images += 1
        except Exception as e:
            # Silently skip failed loads
            pass
    
    def get_image(self, cache_key):
        """
        Retrieve a preloaded image.
        
        Args:
            cache_key: The key used when loading the image
            
        Returns:
            pygame.Surface or None
        """
        return self.image_cache.get(cache_key)
    
    def get_cache_stats(self):
        """Get statistics about the preloaded cache."""
        return {
            'total_attempted': self.total_images,
            'successfully_loaded': self.loaded_images,
            'cache_size_mb': sum(img.get_size()[0] * img.get_size()[1] * 4 / (1024 * 1024) 
                                for img in self.image_cache.values())
        }
