"""Interactive harness to preview the animated endgame sequence."""

import os
import sys
import pygame

# Ensure the project root is on the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from module.games.stories.endgame import EndGameSequence


class EndgameHarness:
    """Simple menu with Win/Lose buttons that launches the endgame sequence."""

    SCREEN_SIZE = (1280, 832)
    BUTTON_SIZE = (280, 96)
    BUTTON_GAP = 40

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption("Endgame Sequence Harness")
        self.clock = pygame.time.Clock()
        self.running = True

        self.background_color = (18, 12, 6)
        self.button_color = (215, 181, 125)
        self.button_hover = (231, 198, 148)
        self.text_color = (60, 36, 12)
        self.message_color = (240, 230, 220)

        self.title_font = pygame.font.SysFont('Times New Roman', 54, bold=True)
        self.button_font = pygame.font.SysFont('Times New Roman', 36, bold=True)
        self.message_font = pygame.font.SysFont('Times New Roman', 24)

        center_x = self.SCREEN_SIZE[0] // 2
        center_y = self.SCREEN_SIZE[1] // 2

        self.win_button = pygame.Rect(0, 0, *self.BUTTON_SIZE)
        self.win_button.center = (center_x, center_y - self.BUTTON_SIZE[1] // 2 - self.BUTTON_GAP // 2)

        self.lose_button = pygame.Rect(0, 0, *self.BUTTON_SIZE)
        self.lose_button.center = (center_x, center_y + self.BUTTON_SIZE[1] // 2 + self.BUTTON_GAP // 2)

        self.sequence: EndGameSequence | None = None
        self.last_result_message = ""

    def run(self) -> None:
        print("=== Endgame Sequence Harness ===")
        print("Click WIN or LOSE to mock reaching block 60.")
        print("Once the popup appears choose Restart or Quit to return here.")
        print("Press ESC or close the window to exit.")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self._handle_event(event)

            self._update()
            self._draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    # ------------------------------------------------------------------
    # Event, update, draw helpers
    # ------------------------------------------------------------------
    def _handle_event(self, event: pygame.event.Event) -> None:
        if self.sequence:
            result = self.sequence.handle_event(event)
            if result:
                choice = result.get('choice')
                outcome = result.get('outcome')
                self.last_result_message = (
                    f"Sequence completed: outcome={outcome}, player chose {choice}."
                )
                self.sequence = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.win_button.collidepoint(event.pos):
                self._start_sequence('win')
            elif self.lose_button.collidepoint(event.pos):
                self._start_sequence('lose')

    def _start_sequence(self, outcome: str) -> None:
        try:
            self.sequence = EndGameSequence(self.screen, outcome)
            self.last_result_message = ""
        except Exception as exc:  # pragma: no cover - runtime surface failures
            print(f"Failed to start EndGameSequence: {exc}")
            self.sequence = None

    def _update(self) -> None:
        if self.sequence:
            self.sequence.update()

    def _draw(self) -> None:
        if self.sequence:
            self.sequence.draw()
            return

        self.screen.fill(self.background_color)

        title = self.title_font.render("Mock Block 60 Outcome", True, self.message_color)
        title_rect = title.get_rect(center=(self.SCREEN_SIZE[0] // 2, 140))
        self.screen.blit(title, title_rect)

        self._draw_button(self.win_button, "Win")
        self._draw_button(self.lose_button, "Lose")

        if self.last_result_message:
            message = self.message_font.render(self.last_result_message, True, self.message_color)
            message_rect = message.get_rect(center=(self.SCREEN_SIZE[0] // 2, self.SCREEN_SIZE[1] - 80))
            self.screen.blit(message, message_rect)

    def _draw_button(self, rect: pygame.Rect, label: str) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        color = self.button_hover if hovered else self.button_color

        pygame.draw.rect(self.screen, color, rect, border_radius=24)
        pygame.draw.rect(self.screen, (115, 73, 26), rect, width=4, border_radius=24)

        text_surface = self.button_font.render(label, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    EndgameHarness().run()
