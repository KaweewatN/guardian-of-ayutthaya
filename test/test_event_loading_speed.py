"""
Test script to measure event loading speed
Run this to see where the delay is coming from
"""
import time
import pygame
import sys
import os

# Add paths (go up one level from test/ to root)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(root_dir, 'module', 'games', 'board'))
sys.path.insert(0, os.path.join(root_dir, 'module', 'games', 'events'))

print("Testing Event Loading Speed...")
print("=" * 60)

# Initialize pygame
start = time.time()
pygame.init()
screen = pygame.display.set_mode((1280, 832))
print(f"✓ Pygame initialization: {(time.time() - start)*1000:.2f}ms")

# Test importing board_block (this loads all game classes)
start = time.time()
from board_block import BoardBlock
print(f"✓ Import board_block (loads all events): {(time.time() - start)*1000:.2f}ms")

# Test creating board
start = time.time()
board = BoardBlock(screen, start_block=1)
print(f"✓ Create BoardBlock instance: {(time.time() - start)*1000:.2f}ms")

# Test creating individual game instances
print("\n" + "=" * 60)
print("Testing Individual Game Creation:")
print("-" * 60)

# Rock Paper Scissors
from board_block import RockPaperScissors
if RockPaperScissors:
    start = time.time()
    rps = RockPaperScissors(screen, 6)
    print(f"✓ RockPaperScissors (block 6): {(time.time() - start)*1000:.2f}ms")

# Photo Hunt
from board_block import PhotoHuntGame
if PhotoHuntGame:
    start = time.time()
    photo = PhotoHuntGame(screen, 22)
    print(f"✓ PhotoHuntGame (block 22): {(time.time() - start)*1000:.2f}ms")

# Guess Game
from board_block import GuessGame
if GuessGame:
    start = time.time()
    guess = GuessGame(screen, 9)
    print(f"✓ GuessGame (block 9): {(time.time() - start)*1000:.2f}ms")

# Math Event
from board_block import MathEvent
if MathEvent:
    start = time.time()
    math_game = MathEvent(screen, 3)
    print(f"✓ MathEvent (block 3): {(time.time() - start)*1000:.2f}ms")

# Random Card
from board_block import RandomCard
if RandomCard:
    start = time.time()
    random_card = RandomCard(screen, 4)
    print(f"✓ RandomCard (block 4): {(time.time() - start)*1000:.2f}ms")

print("\n" + "=" * 60)
print("Performance Summary:")
print("-" * 60)
print("If any game takes > 100ms, check:")
print("  1. Image file sizes (compress large PNGs)")
print("  2. Number of images being loaded")
print("  3. Font loading (already optimized)")
print("=" * 60)

pygame.quit()
