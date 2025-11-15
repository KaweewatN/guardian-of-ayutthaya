#!/usr/bin/env python3
"""
Interactive Pixel Picker for Photo Hunt
Click on the image to get exact (x, y) coordinates for differences.
"""

import pygame
import sys
import os

def main():
    """Interactive tool to find pixel coordinates on photo hunt images."""
    pygame.init()
    
    # Ask which block to inspect
    print("\n" + "="*60)
    print("PHOTO HUNT - PIXEL COORDINATE PICKER")
    print("="*60)
    print("\nWhich block do you want to inspect?")
    print("  22 = Temple scene")
    print("  34 = Elephant scene")
    
    block = input("\nEnter block number (22 or 34): ").strip()
    if block not in ['22', '34']:
        print("Invalid block number. Using 22.")
        block = '22'
    
    print("\nWhich image?")
    print("  1 = BEFORE image")
    print("  2 = AFTER image")
    which = input("\nEnter 1 or 2: ").strip()
    
    if which == '1':
        img_type = 'before'
    else:
        img_type = 'after'
    
    # Load the image
    assets_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', '..',
        'assets', 'scene', 'event', 'photo-hunt'
    )
    img_path = os.path.join(assets_path, f'{block}-{img_type}.png')
    
    if not os.path.exists(img_path):
        print(f"\nError: Image not found at {img_path}")
        return
    
    print(f"\nLoading: {img_path}")
    image = pygame.image.load(img_path)
    original_size = image.get_size()
    
    # Scale to game size (1280x832)
    screen = pygame.display.set_mode((1280, 832))
    pygame.display.set_caption(f"Pixel Picker - Block {block} ({img_type.upper()})")
    image = pygame.transform.scale(image, (1280, 832))
    
    # Store clicked points
    clicked_points = []
    
    # Colors
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    font = pygame.font.SysFont('Monaco', 16, bold=True)
    title_font = pygame.font.SysFont('Monaco', 20, bold=True)
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("  • LEFT CLICK anywhere on image to mark a difference location")
    print("  • Each click will show a circle and print coordinates")
    print("  • Press 'C' to clear all marks")
    print("  • Press 'ESC' or close window to exit")
    print("="*60 + "\n")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    # Clear all points
                    clicked_points.clear()
                    print("\n[Cleared all marks]")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    clicked_points.append((x, y))
                    print(f"\n✓ Point {len(clicked_points)}: x={x}, y={y}")
                    print(f"   Code: {{'x': {x}, 'y': {y}, 'radius': 60, 'name': 'Description here'}},")
        
        # Draw image
        screen.blit(image, (0, 0))
        
        # Draw all clicked points
        for idx, (x, y) in enumerate(clicked_points):
            # Draw circle with yellow border
            pygame.draw.circle(screen, YELLOW, (x, y), 62, 3)
            pygame.draw.circle(screen, RED, (x, y), 60, 2)
            
            # Draw crosshair
            pygame.draw.line(screen, GREEN, (x-10, y), (x+10, y), 2)
            pygame.draw.line(screen, GREEN, (x, y-10), (x, y+10), 2)
            
            # Draw label
            label = font.render(f"#{idx+1} ({x},{y})", True, WHITE)
            label_bg = pygame.Surface((label.get_width() + 6, label.get_height() + 4))
            label_bg.fill(BLACK)
            label_bg.set_alpha(180)
            screen.blit(label_bg, (x + 15, y - 10))
            screen.blit(label, (x + 18, y - 8))
        
        # Draw instructions at top
        instructions = [
            f"Block {block} - {img_type.upper()} | Click to mark differences | 'C' to clear | ESC to exit",
            f"Marks: {len(clicked_points)} point(s)"
        ]
        
        y_offset = 10
        for text in instructions:
            text_surf = title_font.render(text, True, WHITE)
            text_bg = pygame.Surface((text_surf.get_width() + 20, text_surf.get_height() + 10))
            text_bg.fill(BLACK)
            text_bg.set_alpha(200)
            screen.blit(text_bg, (10, y_offset))
            screen.blit(text_surf, (20, y_offset + 5))
            y_offset += text_surf.get_height() + 15
        
        pygame.display.flip()
        clock.tick(60)
    
    # Print summary before exit
    if clicked_points:
        print("\n" + "="*60)
        print("SUMMARY - Copy this into photo_hunt.py:")
        print("="*60)
        print(f"\nBlock {block} differences:")
        for idx, (x, y) in enumerate(clicked_points):
            print(f"    {{'x': {x}, 'y': {y}, 'radius': 60, 'name': 'Difference {idx+1}'}},")
        print("\n" + "="*60 + "\n")
    
    pygame.quit()


if __name__ == "__main__":
    main()
