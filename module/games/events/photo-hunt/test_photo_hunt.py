#!/usr/bin/env python3
"""
Test script for Photo Hunt game.
Run this to test the Photo Hunt implementation.
"""

import pygame
import sys
import os

# Add the photo-hunt directory to path so we can import photo_hunt directly
sys.path.insert(0, os.path.dirname(__file__))

from photo_hunt import PhotoHuntGame


def main():
    """Test the Photo Hunt game."""
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Photo Hunt Test - Block 22")
    clock = pygame.time.Clock()
    
    # Test block 22
    game = PhotoHuntGame(screen, block_number=22)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            result = game.handle_event(event)
            if result:
                print(f"Game result: {result}")
                # Test block 34 next
                game = PhotoHuntGame(screen, block_number=34)
        
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
