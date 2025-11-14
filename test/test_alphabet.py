"""
Simple test script for AlphabetWin and AlphabetLose screens
Press 1 for Win screen, 2 for Lose screen
"""
import pygame
import sys
import os

# Add module directories to path (we're in test/ folder, go up one level)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'module', 'games'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'module'))

from alphabet.alphabet_win import AlphabetWin
from alphabet.alphabet_lose import AlphabetLose
from game_state import game_state

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 832
FPS = 60

def main():
    """Test alphabet win and lose screens"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Alphabet Screens Test")
    clock = pygame.time.Clock()
    
    # Set up test character
    game_state.set_character('character1', {'name': 'Test Character'})
    
    # Add some initial alphabet cards for lose screen testing
    game_state.draw_alphabet_cards(5)
    
    # Start with menu
    current_screen = None
    screen_type = None
    
    running = True
    print("=" * 60)
    print("Alphabet Screens Test")
    print("=" * 60)
    print("Controls:")
    print("  1 - Show Alphabet WIN screen (gain 2 cards)")
    print("  2 - Show Alphabet LOSE screen (return 1 card)")
    print("  SPACE/CLICK - Continue (after viewing a screen)")
    print("  ESC - Quit")
    print("=" * 60)
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    # Show win screen
                    current_screen = AlphabetWin(screen, source='event')
                    screen_type = 'win'
                    print("\n[Test] Showing AlphabetWin screen")
                elif event.key == pygame.K_2:
                    # Show lose screen
                    current_screen = AlphabetLose(screen)
                    screen_type = 'lose'
                    print("\n[Test] Showing AlphabetLose screen")
            
            # Handle screen events
            if current_screen:
                result = current_screen.handle_event(event)
                if result:
                    print(f"[Test] Screen returned result: {result}")
                    current_screen = None
                    screen_type = None
                    
                    # Show current card inventory
                    cards = game_state.list_player_alphabet_cards()
                    counts = game_state.get_player_alphabet_counts()
                    print(f"[Test] Current cards: {sorted(cards)}")
                    print(f"[Test] Card counts: {counts}")
        
        # Update and draw
        screen.fill((50, 35, 25))  # Dark brown background
        
        if current_screen:
            current_screen.update()
            current_screen.draw()
        else:
            # Show menu
            font = pygame.font.SysFont('Arial', 40, bold=True)
            title = font.render("Alphabet Screens Test", True, (255, 230, 180))
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))
            
            font_small = pygame.font.SysFont('Arial', 28)
            inst1 = font_small.render("Press 1 for WIN screen", True, (255, 255, 255))
            inst2 = font_small.render("Press 2 for LOSE screen", True, (255, 255, 255))
            inst3 = font_small.render("Press ESC to quit", True, (200, 200, 200))
            
            screen.blit(inst1, inst1.get_rect(center=(SCREEN_WIDTH // 2, 350)))
            screen.blit(inst2, inst2.get_rect(center=(SCREEN_WIDTH // 2, 400)))
            screen.blit(inst3, inst3.get_rect(center=(SCREEN_WIDTH // 2, 500)))
            
            # Show current inventory
            cards = game_state.list_player_alphabet_cards()
            counts = game_state.get_player_alphabet_counts()
            inventory_text = f"Current cards: {counts}"
            inventory = font_small.render(inventory_text, True, (200, 255, 200))
            screen.blit(inventory, inventory.get_rect(center=(SCREEN_WIDTH // 2, 600)))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
