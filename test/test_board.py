"""
Simple test script for Board with Alphabet Deck
Tests the board interface and alphabet deck expansion feature
"""
import pygame
import sys
import os

# Add module directories to path (we're in test/ folder, go up one level)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'module', 'games'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'module'))

from board.board import Board
from game_state import game_state

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 832
FPS = 60

def main():
    """Test the board with alphabet deck"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Board Test - Alphabet Deck")
    clock = pygame.time.Clock()
    
    # Set up test character
    game_state.set_character('character1', {'name': 'Test Character'})
    
    # Add some test alphabet cards to see in the deck
    # Use draw_alphabet_cards to get random cards from the deck
    drawn_cards = game_state.draw_alphabet_cards(7)
    print(f"Drew {len(drawn_cards)} alphabet cards: {drawn_cards}")
    
    # Create board
    board = Board(screen)
    
    running = True
    print("=" * 60)
    print("Board Test - Alphabet Deck Expansion")
    print("=" * 60)
    print("Controls:")
    print("  - Click 'View Cards' button below alphabet deck to expand")
    print("  - Click red X button to close expanded view")
    print("  - Click 'Roll Dice' to move on board")
    print("  - LEFT/RIGHT arrows to navigate boards")
    print("  - ESC to quit")
    print("=" * 60)
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle board events (includes alphabet deck)
            board.handle_event(event)
        
        # Update board
        board.update()
        
        # Draw everything
        screen.fill((245, 235, 220))  # Fallback background
        board.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
