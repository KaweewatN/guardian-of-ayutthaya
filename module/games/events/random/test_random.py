"""
Simple test file for Random Card mini-game
"""
import pygame
import sys
from random_event import RandomCard


def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Random Card Test")
    clock = pygame.time.Clock()
    
    # Create game instance (test with block 4)
    game = RandomCard(screen, block_number=4)
    
    print("=" * 60)
    print("Random Card Game - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  - Click on a card to choose")
    print("  - SPACE or CLICK to continue after reveal")
    print("  - ESC to quit")
    print("=" * 60)
    
    running = True
    while running:
        clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                result = game.handle_event(event)
                if result:
                    print(f"\nGame Result: {result}")
                    print("=" * 60)
                    running = False
        
        # Update game
        game.update()
        
        # Draw game
        game.draw()
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()