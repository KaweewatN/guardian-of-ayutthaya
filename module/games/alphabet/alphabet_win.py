"""Alphabet reward screen shown after winning an event or drawing a good card."""

from __future__ import annotations

import os
from typing import List, Optional

import pygame

# Ensure fonts module can be imported regardless of execution context
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in os.sys.path:
    os.sys.path.insert(0, _CONSTANT_BASE)

try:  # pragma: no cover - runtime dependency
    from fonts import TITLE_FONT, TEXT_FONT, BUTTON_FONT
except Exception:  # pragma: no cover - fallback when fonts fail to load
    TITLE_FONT = pygame.font.SysFont('Arial', 60, bold=True)
    TEXT_FONT = pygame.font.SysFont('Arial', 28)
    BUTTON_FONT = pygame.font.SysFont('Arial', 32, bold=True)

# Import global game state manager
_MODULE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _MODULE_BASE not in os.sys.path:
    os.sys.path.insert(0, _MODULE_BASE)

from game_state import game_state


class AlphabetWin:
    """Display the alphabet reward overlay and grant cards to the player."""

    LETTERS_PER_REWARD = 2

    def __init__(self, screen: pygame.Surface, source: str = 'event') -> None:
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.source = source

        self.background = self._load_image('receive.png')
        self.letter_images = self._load_letter_images()

        # Draw letters immediately so the deck state updates before display
        self.drawn_letters: List[str] = game_state.draw_alphabet_cards(self.LETTERS_PER_REWARD)

        self.title_font = TITLE_FONT
        self.text_font = TEXT_FONT
        self.button_font = BUTTON_FONT

        self._continue_rect: Optional[pygame.Rect] = None
        self.finished = False
        self._result_reported = False

        # Pre-render texts
        source_text = "Congratulations!" if source == 'event' else "Good fortune!"
        self.title_surface = self.title_font.render(source_text, True, (101, 67, 33))  # Darker brown

        if self.drawn_letters:
            letters_str = ', '.join(self.drawn_letters)
            message = f"You received: {letters_str}"
        else:
            message = "The deck is empty. No cards to draw."

        self.message_surface = self.text_font.render(message, True, (0, 0, 0))  # Black
        self.prompt_surface = self.text_font.render("Press SPACE or CLICK to continue", True, (255, 255, 255))

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------
    def _assets_path(self, *paths: str) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base, 'assets', 'alphabet', *paths)

    def _load_image(self, filename: str) -> Optional[pygame.Surface]:
        path = self._assets_path(filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.screen_rect.width, self.screen_rect.height))
            except Exception as exc:  # pragma: no cover - defensive log
                print(f"Warning: failed to load {path}: {exc}")
        else:
            print(f"Warning: alphabet background not found: {path}")
        return None

    def _load_letter_images(self) -> dict[str, pygame.Surface]:
        images: dict[str, pygame.Surface] = {}
        card_width, card_height = 160, 240
        for letter in game_state.get_alphabet_deck_counts().keys():
            filename = os.path.join('letter', f"{letter.lower()}.png")
            path = self._assets_path(filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    images[letter] = pygame.transform.smoothscale(img, (card_width, card_height))
                except Exception as exc:  # pragma: no cover
                    print(f"Warning: unable to load letter card {path}: {exc}")
            else:
                print(f"Warning: letter card missing: {path}")
        return images

    # ------------------------------------------------------------------
    # Pygame interface
    # ------------------------------------------------------------------
    def update(self) -> None:
        """No continuous updates required for static reward screen."""

    def draw(self) -> None:
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((70, 50, 30))

        # Draw title near top
        title_rect = self.title_surface.get_rect(center=(self.screen_rect.centerx, 185))
        self.screen.blit(self.title_surface, title_rect)

        # Draw the cards centered horizontally
        self._draw_letter_cards()

        # Draw message below the cards (cards are at centery-100 with height 240)
        message_y = self.screen_rect.centery - 100 + 240 + 60  # Card bottom + 40px spacing
        message_rect = self.message_surface.get_rect(center=(self.screen_rect.centerx, message_y))
        self.screen.blit(self.message_surface, message_rect)

        prompt_rect = self.prompt_surface.get_rect(center=(self.screen_rect.centerx, self.screen_rect.height - 90))
        self.screen.blit(self.prompt_surface, prompt_rect)
        self._continue_rect = prompt_rect

    def _draw_letter_cards(self) -> None:
        if not self.drawn_letters:
            return

        spacing = 40
        cards = [self.letter_images.get(letter) for letter in self.drawn_letters]
        cards = [card for card in cards if card]

        if not cards:
            return

        total_width = sum(card.get_width() for card in cards) + spacing * (len(cards) - 1)
        start_x = self.screen_rect.centerx - total_width // 2
        y = self.screen_rect.centery - 80  # Moved up from -40

        for card in cards:
            self.screen.blit(card, (start_x, y))
            start_x += card.get_width() + spacing

    def handle_event(self, event: pygame.event.Event) -> Optional[dict]:
        if self.finished:
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return self._finalize()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._finalize()

        return None

    def _finalize(self) -> Optional[dict]:
        if self._result_reported:
            return None
        self._result_reported = True
        self.finished = True
        return {
            'result': 'alphabet-win',
            'letters': self.drawn_letters,
        }
