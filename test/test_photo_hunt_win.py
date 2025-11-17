"""
Quick test to verify Photo Hunt win leads to alphabet reward
"""
import pygame
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'module', 'games', 'board'))

pygame.init()
screen = pygame.display.set_mode((1280, 832))
pygame.display.set_caption("Photo Hunt → Alphabet Test")
clock = pygame.time.Clock()

from board_block import BoardBlock

# Create board at block 22 (Photo Hunt)
board = BoardBlock(screen, start_block=22)

print("=" * 60)
print("Photo Hunt → Alphabet Reward Test")
print("=" * 60)
print("1. Skip the intro scene (SPACE)")
print("2. Start Photo Hunt (SPACE)")
print("3. Wait 5 seconds (viewing)")
print("4. Click ANY yellow circle to WIN")
print("5. Press SPACE on result screen")
print("6. Should see Alphabet Win screen!")
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
