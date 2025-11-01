import pygame
import sys
import os

"""
Interactive test script for the Guess mini-game.

This mirrors the style of the Rock-Paper-Scissors test: it opens a window,
instantiates `GuessGame` for a given block (default 9) and lets you play the
mini-game manually. When the mini-game returns a result dict it will be printed
and the test exits.
"""

# Make imports robust: try package-style import first, then fall back to local
# module import. Also add module/games to sys.path (like main.py does).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'games'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

GuessGame = None
try:
    # Try importing using the same package path as main.py (events package)
    from events.guess.guess import GuessGame
except Exception:
    try:
        # Fallback: import directly from this folder
        from guess import GuessGame
    except Exception as e:
        print(f"Failed to import GuessGame: {e}")
        raise


def main():
    pygame.init()
    # Open fullscreen using the current display resolution so the test
    # matches the game's usual fullscreen environment.
    pygame.display.set_caption("Guardian of Ayutthaya - Guess Test (Fullscreen)")
    # Query current display size, then set fullscreen mode
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Choose the block to test (9 matches quiz assets)
    block_number = 51
    game = GuessGame(screen, block_number=block_number)

    print("=" * 60)
    print("GUESS GAME TEST")
    print("=" * 60)
    print(f"Testing block {block_number}...")
    print("Instructions: press SPACE or click to start, type answer, press ENTER to submit.")
    print("Press ESC to quit.")
    print("=" * 60)

    running = True
    game_complete = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            # Forward events to the mini-game while it is active
            if not game_complete:
                try:
                    result = game.handle_event(event)
                except Exception as e:
                    print(f"Error in game.handle_event: {e}")
                    result = None

                if isinstance(result, dict) and result.get("result") in ("win", "lose"):
                    print("\n" + "=" * 60)
                    print("GAME COMPLETE!")
                    print("=" * 60)
                    print(f"Result: {result}")
                    print("=" * 60)
                    game_complete = True
                    # small pause to allow user to see result
                    pygame.time.wait(1500)
                    running = False

        # Draw game
        game.draw()
        # Optionally draw other UI here
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("\nTest complete!")


if __name__ == '__main__':
    main()
