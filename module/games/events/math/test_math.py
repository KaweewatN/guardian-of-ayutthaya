"""Local development entry point with a simple white screen and number buttons."""
import sys
import pygame

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


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Local Dev")

    clock = pygame.time.Clock()
    buttons = create_buttons(SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_LABELS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        print(f"Button {button['label']} clicked")

        screen.fill(BACKGROUND_COLOR)

        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            rect = button["rect"]
            is_hovered = rect.collidepoint(mouse_pos)
            color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, TEXT_COLOR, rect, width=2, border_radius=12)
            button["text_rect"].center = rect.center
            screen.blit(button["text_surface"], button["text_rect"])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
