"""
Test block 53 → 58 jump (should show scenes first)
"""
import pygame
import sys
import os

# Add paths (go up one level from test/ to root, then to module)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'module', 'games', 'board'))

pygame.init()
screen = pygame.display.set_mode((1280, 832))
pygame.display.set_caption("Test Block 53 Jump")
clock = pygame.time.Clock()

from board_block import BoardBlock

# Start at block 53
board = BoardBlock(screen, start_block=22)

print("=" * 60)
print("Block 53 Jump Test")
print("=" * 60)
print("Expected behavior:")
print("1. Shows scenes for block 53")
print("2. After scenes finish → jump to block 58")
print("3. Shows scenes for block 58")
print("=" * 60)
print("Press SPACE to skip scenes quickly")
print("=" * 60)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        else:
            board.handle_event(event)
    
    board.update()
    screen.fill((50, 50, 50))
    board.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nTest completed!")
