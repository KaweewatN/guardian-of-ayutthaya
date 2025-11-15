"""
Quick test for Victory / Outcome page
Tests the win/lose screen independently
"""

import pygame
import sys
import os

# Add module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module.games.board.game_outcome import GameOutcomeScreen

def test_victory_page():
    """Test victory page display"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Test Victory Page - Press SPACE to close")
    clock = pygame.time.Clock()
    
    # Create victory screen
    outcome_screen = GameOutcomeScreen(screen, 'win')
    
    print("=" * 60)
    print("Displaying Victory Page")
    print("=" * 60)
    print("Press SPACE or click to close")
    print("Press ESC to exit")
    print("=" * 60)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Let outcome screen handle events
            result = outcome_screen.handle_event(event)
            if result:
                print(f"Victory screen closed with result: {result}")
                running = False
        
        # Update and draw
        outcome_screen.update()
        outcome_screen.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Victory page test completed!")

def test_defeat_page():
    """Test defeat page display"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption("Test Defeat Page - Press SPACE to close")
    clock = pygame.time.Clock()
    
    # Create defeat screen
    outcome_screen = GameOutcomeScreen(screen, 'lose')
    
    print("=" * 60)
    print("Displaying Defeat Page")
    print("=" * 60)
    print("Press SPACE or click to close")
    print("Press ESC to exit")
    print("=" * 60)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Let outcome screen handle events
            result = outcome_screen.handle_event(event)
            if result:
                print(f"Defeat screen closed with result: {result}")
                running = False
        
        # Update and draw
        outcome_screen.update()
        outcome_screen.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Defeat page test completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'lose':
        test_defeat_page()
    else:
        test_victory_page()
    
    print("\n" + "=" * 60)
    print("Usage:")
    print("  python3 test/test_victory_page.py       - Test victory page")
    print("  python3 test/test_victory_page.py lose  - Test defeat page")
    print("=" * 60)
