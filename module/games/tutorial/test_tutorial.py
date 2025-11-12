"""
Test file for Tutorial module
Run this to test the tutorial independently
"""
import pygame
import sys
import os

# Add module directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tutorial import Tutorial

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 832

def main():
    """Test the tutorial system"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tutorial Test - Guardian of Ayutthaya")
    clock = pygame.time.Clock()
    
    # Create tutorial instance
    tutorial = Tutorial(screen)
    
    print("=" * 60)
    print("Tutorial System - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  LEFT/RIGHT arrows: Navigate pages")
    print("  SPACE: Next page")
    print("  ESC: Skip tutorial")
    print("  Mouse: Click buttons")
    print("  Previous/Next/Skip buttons: Click to navigate")
    print("=" * 60)
    
    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle tutorial events
            if tutorial.handle_event(event):
                print("Tutorial finished!")
                print("=" * 60)
                running = False
        
        # Draw tutorial
        tutorial.draw()
    
    pygame.quit()
    print("Test complete!")


if __name__ == "__main__":
    main()
