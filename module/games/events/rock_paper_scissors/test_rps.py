"""
Simple test script for Rock Paper Scissors mini-game
Run this to test the mini-game without the full board game
"""
import pygame
import sys
import os

# Add module/games to path so we can import the mini-game directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'module', 'games'))

try:
    # Try the package-style import first
    from module.games.rock_paper_scissors import RockPaperScissors
except Exception:
    # Fallback to direct import from module/games folder
    from rock_paper_scissors.rock_paper_scissors import RockPaperScissors



def main():
    """Test the RPS mini-game"""
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Guardian of Ayutthaya - RPS Test")
    clock = pygame.time.Clock()
    
    # Create game instance for block 6
    rps_game = RockPaperScissors(screen, block_number=6)
    
    print("=" * 60)
    print("ROCK PAPER SCISSORS TEST")
    print("=" * 60)
    print("Testing block 6...")
    print("Click to play through the game")
    print("Press ESC to quit")
    print("=" * 60)
    
    running = True
    game_complete = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle game events
            if not game_complete:
                result = rps_game.handle_event(event)
                
                if result is not None:
                    print("\n" + "=" * 60)
                    print("GAME COMPLETE!")
                    print("=" * 60)
                    print(f"Result: {result}")
                    
                    if result["result"] == "win":
                        print(f"✓ Player WINS!")
                    else:
                        print(f"✗ Player LOSES!")
                    
                    print("=" * 60)
                    game_complete = True
                    
                    # Wait a moment before closing
                    pygame.time.wait(3000)
                    running = False
        
        # Draw
        rps_game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest complete!")


if __name__ == "__main__":
    main()
