"""Interactive test harness for alphabet win/lose overlays.

This script launches a simple Pygame window with two buttons:
* "Gain" shows the :class:`AlphabetWin` overlay and draws two cards.
* "Return" shows the :class:`AlphabetLose` overlay with the current hand.

Before triggering either overlay you can type a number (0-22) to simulate how
many alphabet cards the player currently owns. The harness resets the global
``game_state`` and draws the requested number of cards so the overlays display
realistic data.

Run directly with ``python module/games/alphabet/alphabet_test_page.py``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Callable, Optional

import pygame

pygame.init()

# Allow running this file directly regardless of CWD
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from module.game_state import game_state
from module.games.alphabet.alphabet_win import AlphabetWin
from module.games.alphabet.alphabet_lose import AlphabetLose


WINDOW_SIZE = (1280, 720)
BG_COLOR = (35, 24, 16)
TEXT_COLOR = (240, 230, 220)
INPUT_BG = (60, 45, 32)
BUTTON_COLOR = (90, 65, 45)
BUTTON_HOVER = (120, 90, 65)
BUTTON_TEXT = (255, 240, 200)

pygame.display.set_caption("Alphabet Overlay Tester")
DEFAULT_FONT = pygame.font.SysFont("Arial", 28)
BUTTON_FONT = pygame.font.SysFont("Arial", 30, bold=True)
TITLE_FONT = pygame.font.SysFont("Arial", 40, bold=True)


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    on_click: Callable[[], None]

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = BUTTON_FONT.render(self.label, True, BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False


def reset_decks_with_cards(card_count: int) -> None:
    """Reset deck and draw ``card_count`` letters into the player's hand."""
    card_count = max(0, min(card_count, 22))
    game_state.reset_alphabet_inventory()
    if card_count:
        game_state.draw_alphabet_cards(card_count)


class AlphabetTester:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()

        self.overlay: Optional[object] = None
        self.last_result: Optional[str] = None

        self.input_active = False
        self.input_text = "0"

        self.buttons = [
            Button(pygame.Rect(360, 500, 220, 72), "Gain (Win)", self._show_gain),
            Button(pygame.Rect(700, 500, 220, 72), "Return (Lose)", self._show_return),
        ]

    # ------------------------------------------------------------------
    # Overlay helpers
    # ------------------------------------------------------------------
    def _show_gain(self) -> None:
        count = self._current_card_count()
        reset_decks_with_cards(count)
        self.overlay = AlphabetWin(self.screen)
        self.last_result = None

    def _show_return(self) -> None:
        count = self._current_card_count()
        reset_decks_with_cards(count)
        self.overlay = AlphabetLose(self.screen)
        self.last_result = None

    def _current_card_count(self) -> int:
        try:
            return int(self.input_text)
        except ValueError:
            return 0

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.overlay is not None:
                    if hasattr(self.overlay, "handle_event"):
                        result = self.overlay.handle_event(event)
                    else:
                        result = None
                    if result:
                        self.last_result = repr(result)
                        self.overlay = None
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.input_active = self._input_rect().collidepoint(event.pos)

                if self.input_active and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isdigit():
                        if self.input_text == "0":
                            self.input_text = ""

                        if len(self.input_text) < 2 or (len(self.input_text) == 2 and self.input_text == "2"):
                            self.input_text += event.unicode
                            if int(self.input_text) > 22:
                                self.input_text = "22"
                    elif event.unicode.strip() == "" and not self.input_text:
                        # Allow leading spaces to be ignored
                        pass

                if not self.input_text:
                    self.input_text = "0"

                for button in self.buttons:
                    if button.handle_event(event):
                        break

            self._draw()
            self.clock.tick(60)

        pygame.quit()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw(self) -> None:
        self.screen.fill(BG_COLOR)

        if self.overlay is not None:
            if hasattr(self.overlay, "update"):
                self.overlay.update()
            if hasattr(self.overlay, "draw"):
                self.overlay.draw()
            pygame.display.flip()
            return

        mouse_pos = pygame.mouse.get_pos()

        title = TITLE_FONT.render("Alphabet Overlay Tester", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_SIZE[0] // 2, 120))
        self.screen.blit(title, title_rect)

        instructions = [
            "Type how many alphabet cards the player owns (0-22).",
            "Click a button to show the matching overlay.",
            "When the overlay finishes, the result will appear below.",
        ]
        for index, line in enumerate(instructions):
            text = DEFAULT_FONT.render(line, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, 220 + index * 36))
            self.screen.blit(text, rect)

        # Input box
        label = DEFAULT_FONT.render("Card Count:", True, TEXT_COLOR)
        label_rect = label.get_rect(midright=(WINDOW_SIZE[0] // 2 - 20, 360))
        self.screen.blit(label, label_rect)

        input_rect = self._input_rect()
        pygame.draw.rect(
            self.screen,
            INPUT_BG,
            input_rect,
            border_radius=6,
        )
        border_color = (255, 215, 120) if self.input_active else (120, 90, 65)
        pygame.draw.rect(self.screen, border_color, input_rect, width=2, border_radius=6)

        display_text = self.input_text or "0"
        text_surface = BUTTON_FONT.render(display_text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=input_rect.center)
        self.screen.blit(text_surface, text_rect)

        for button in self.buttons:
            button.draw(self.screen, mouse_pos)

        if self.last_result:
            result_surface = DEFAULT_FONT.render(f"Last Result: {self.last_result}", True, TEXT_COLOR)
            result_rect = result_surface.get_rect(center=(WINDOW_SIZE[0] // 2, 620))
            self.screen.blit(result_surface, result_rect)

        pygame.display.flip()

    def _input_rect(self) -> pygame.Rect:
        return pygame.Rect(WINDOW_SIZE[0] // 2 + 20, 330, 120, 60)


if __name__ == "__main__":
    AlphabetTester().run()
