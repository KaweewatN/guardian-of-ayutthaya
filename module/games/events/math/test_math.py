"""Local development test harness for the math event intro."""
import os
import sys
import importlib.util

import pygame

# Attempt to import MathEvent similarly to other event test harnesses.
MODULE_DIR = os.path.dirname(__file__)
SYS_GAMES_DIR = os.path.join(MODULE_DIR, "..", "..", "..")
SYS_EVENTS_DIR = os.path.join(MODULE_DIR, "..", "..", "..", "games")

if SYS_GAMES_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(SYS_GAMES_DIR))
if SYS_EVENTS_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(SYS_EVENTS_DIR))

try:
    from events.math.math import MathEvent  # type: ignore
except Exception:
    math_path = os.path.join(MODULE_DIR, "math.py")
    spec = importlib.util.spec_from_file_location("math_event_module", math_path)
    if not spec or not spec.loader:  # pragma: no cover - sanity check
        raise ImportError("Unable to load MathEvent implementation")
    math_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(math_module)
    MathEvent = math_module.MathEvent


# Initialize pygame
pygame.init()

# Screen configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_COLOR = (220, 220, 220)
BUTTON_HOVER_COLOR = (180, 180, 180)
TEXT_COLOR = (0, 0, 0)
FONT_NAME = "Arial"
FONT_SIZE = 36
FPS = 60

# Numbers to display on buttons
BUTTON_LABELS = [3, 11, 20, 28, 37, 43, 49, 53]
RESULT_DISPLAY_MS = 1200


def create_buttons(screen_width, screen_height, button_labels, columns=4, rows=2, padding=40):
    """Create button rects and texts arranged in a grid."""
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold=True)
    button_width = int((screen_width - (columns + 1) * padding) / columns)
    button_height = int((screen_height - (rows + 1) * padding) / rows)

    buttons = []
    for index, label in enumerate(button_labels):
        row = index // columns
        col = index % columns
        x = int(padding + col * (button_width + padding))
        y = int(padding + row * (button_height + padding))
        rect = pygame.Rect(x, y, button_width, button_height)
        text_surface = font.render(str(label), True, TEXT_COLOR)
        buttons.append({
            "rect": rect,
            "label": str(label),
            "text_surface": text_surface,
            "text_rect": text_surface.get_rect(center=rect.center),
        })
    return buttons


def draw_selection_screen(screen, buttons):
    screen.fill(BACKGROUND_COLOR)

    for button in buttons:
        rect = button["rect"]
        is_hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, TEXT_COLOR, rect, width=2, border_radius=12)
        button["text_rect"].center = rect.center
        screen.blit(button["text_surface"], button["text_rect"])


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Local Dev - Math Event")

    clock = pygame.time.Clock()
    buttons = create_buttons(SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_LABELS)

    running = True
    math_event = None
    math_event_result = None
    math_event_end_time = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if math_event is None:
                    running = False
                    continue

            if math_event is not None:
                result = math_event.handle_event(event)
                if isinstance(result, dict):
                    print(f"Math event result: {result}")
                    math_event_result = result
                    math_event_end_time = pygame.time.get_ticks()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            label = button["label"]
                            print(f"Button {label} clicked")
                            if label == "3":
                                math_event = MathEvent(screen, block_number=3)
                                math_event_result = None
                                math_event_end_time = 0
                            break

        if math_event is not None:
            math_event.draw()
            if math_event_result and pygame.time.get_ticks() - math_event_end_time > RESULT_DISPLAY_MS:
                math_event = None
                math_event_result = None
                math_event_end_time = 0
        else:
            draw_selection_screen(screen, buttons)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
