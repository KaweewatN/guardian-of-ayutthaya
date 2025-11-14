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
    
    # All random card block numbers
    block_numbers = [4, 8, 12, 16, 19, 23, 26, 29, 33, 36, 39, 42, 45, 48, 52, 56]
    current_index = 0
    
    # Print all block configurations
    print("=" * 80)
    print("RANDOM CARD CONFIGURATIONS FOR ALL BLOCKS")
    print("=" * 80)
    for block_num in block_numbers:
        cards = RandomCard.BLOCK_CARDS.get(block_num, [])
        print(f"\nBlock {block_num}:")
        for i, card in enumerate(cards, 1):
            if card == "good":
                effect = "Divine Blessing - Gain letter(s)"
            elif card == "bad":
                effect = "Careless Mistake - Return a letter"
            elif card.startswith("forward-"):
                spaces = card.replace("forward-", "")
                effect = f"Move forward {spaces} spaces"
            elif card.startswith("backward-"):
                spaces = card.replace("backward-", "")
                effect = f"Move backward {spaces} spaces"
            else:
                effect = "Unknown"
            print(f"  Card {i}: {card:15s} -> {effect}")
    print("=" * 80)
    print()
    
    # Create game instance
    game = RandomCard(screen, block_number=block_numbers[current_index])
    
    print("=" * 60)
    print("Random Card Game - Test Mode")
    print("=" * 60)
    print("Controls:")
    print("  - Click on a card to choose")
    print("  - SPACE or CLICK to continue after reveal")
    print("  - N = Next block space")
    print("  - P = Previous block space")
    print("  - R = Restart current block")
    print("  - ESC = Quit")
    print("=" * 60)
    print(f"Current Block: {block_numbers[current_index]}")
    print("=" * 60)
    
    running = True
    while running:
        clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    # Next block
                    current_index = (current_index + 1) % len(block_numbers)
                    game = RandomCard(screen, block_number=block_numbers[current_index])
                    print(f"\n[Switched to Block {block_numbers[current_index]}]")
                    print("=" * 60)
                elif event.key == pygame.K_p:
                    # Previous block
                    current_index = (current_index - 1) % len(block_numbers)
                    game = RandomCard(screen, block_number=block_numbers[current_index])
                    print(f"\n[Switched to Block {block_numbers[current_index]}]")
                    print("=" * 60)
                elif event.key == pygame.K_r:
                    # Restart current block
                    game = RandomCard(screen, block_number=block_numbers[current_index])
                    print(f"\n[Restarted Block {block_numbers[current_index]}]")
                    print("=" * 60)
                else:
                    result = game.handle_event(event)
                    if result:
                        print(f"\nGame Result: {result}")
                        effect = result.get('effect', {})
                        effect_type = effect.get('type')
                        if effect_type == 'warp':
                            movement = effect.get('value', 0)
                            direction = "forward" if movement > 0 else "backward"
                            print(f"Effect: Move {direction} {abs(movement)} spaces")
                        elif effect_type == 'good':
                            print("Effect: Gain letter(s)")
                        elif effect_type == 'bad':
                            print("Effect: Return a letter")
                        print("=" * 60)
                        print("Press N for next block, P for previous, or R to restart")
                        print("=" * 60)
            else:
                result = game.handle_event(event)
                if result:
                    print(f"\nGame Result: {result}")
                    effect = result.get('effect', {})
                    effect_type = effect.get('type')
                    if effect_type == 'warp':
                        movement = effect.get('value', 0)
                        direction = "forward" if movement > 0 else "backward"
                        print(f"Effect: Move {direction} {abs(movement)} spaces")
                    elif effect_type == 'good':
                        print("Effect: Gain letter(s)")
                    elif effect_type == 'bad':
                        print("Effect: Return a letter")
                    print("=" * 60)
                    print("Press N for next block, P for previous, or R to restart")
                    print("=" * 60)
        
        # Update game
        game.update()
        
        # Draw game
        game.draw()
        
        # Draw block info at top
        font = pygame.font.SysFont('Arial', 24, bold=True)
        block_text = font.render(f"Block {block_numbers[current_index]} ({current_index + 1}/{len(block_numbers)})", True, (255, 255, 255))
        text_rect = block_text.get_rect(topleft=(10, 10))
        # Draw shadow
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        shadow_text = font.render(f"Block {block_numbers[current_index]} ({current_index + 1}/{len(block_numbers)})", True, (0, 0, 0))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(block_text, text_rect)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()