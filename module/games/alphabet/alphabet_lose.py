"""Alphabet return screen shown when a bad card is drawn."""

from __future__ import annotations

import math
import os
from typing import List, Optional, Tuple

import pygame

# Ensure fonts module import works when running as script
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in os.sys.path:
    os.sys.path.insert(0, _CONSTANT_BASE)

try:  # pragma: no cover - runtime dependency
    from fonts import TEXT_FONT, BUTTON_FONT
except Exception:  # pragma: no cover - fallback when fonts fail
    TEXT_FONT = pygame.font.SysFont('Arial', 28)
    BUTTON_FONT = pygame.font.SysFont('Arial', 32, bold=True)

# Import global game state manager
_MODULE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _MODULE_BASE not in os.sys.path:
    os.sys.path.insert(0, _MODULE_BASE)

from game_state import game_state


class AlphabetLose:
    """Display alphabet return overlay and force the player to give back a card."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.cards: List[str] = sorted(game_state.list_player_alphabet_cards())
        self.has_cards = bool(self.cards)

        self.card_size = (140, 210)
        self.background = self._load_background('return.png' if self.has_cards else 'return-empty.png')
        self.letter_images = self._load_letter_images()
        self.card_rects: List[Tuple[pygame.Rect, str]] = []
        self.hovered_index: Optional[int] = None

        self.text_font = TEXT_FONT
        self.button_font = BUTTON_FONT

        if self.has_cards:
            self.instruction_surface = self.text_font.render(
                "Select one card to return to the deck", True, (255, 230, 180)
            )
        else:
            self.instruction_surface = self.text_font.render(
                "You do not have any alphabet cards yet.", True, (255, 230, 180)
            )

        self.prompt_surface = self.button_font.render(
            "Click or press SPACE to continue", True, (255, 214, 153)
        )

        self._result_reported = False

        if self.has_cards:
            self._layout_cards()

    # ------------------------------------------------------------------
    # Asset helpers
    # ------------------------------------------------------------------
    def _assets_path(self, *paths: str) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base, 'assets', 'alphabet', *paths)

    def _load_background(self, filename: str) -> Optional[pygame.Surface]:
        path = self._assets_path(filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.screen_rect.width, self.screen_rect.height))
            except Exception as exc:  # pragma: no cover
                print(f"Warning: failed to load {path}: {exc}")
        else:
            print(f"Warning: alphabet background not found: {path}")
        return None

    def _load_letter_images(self) -> dict[str, pygame.Surface]:
        images: dict[str, pygame.Surface] = {}
        width, height = self.card_size
        for letter in game_state.get_alphabet_deck_counts().keys():
            path = self._assets_path('letter', f"{letter.lower()}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    images[letter] = pygame.transform.smoothscale(img, (width, height))
                except Exception as exc:  # pragma: no cover
                    print(f"Warning: unable to load letter card {path}: {exc}")
            else:
                print(f"Warning: letter card missing: {path}")
        return images

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _layout_cards(self) -> None:
        columns = 5
        spacing_x = 24
        spacing_y = 24
        width, height = self.card_size

        rows = max(1, math.ceil(len(self.cards) / columns))
        displayed_columns = min(columns, len(self.cards))
        total_width = displayed_columns * width + (displayed_columns - 1) * spacing_x
        total_height = rows * height + (rows - 1) * spacing_y

        start_x = self.screen_rect.centerx - total_width // 2
        start_y = self.screen_rect.centery - total_height // 2 + 40

        self.card_rects.clear()
        for index, letter in enumerate(self.cards):
            row = index // columns
            col = index % columns
            x = start_x + col * (width + spacing_x)
            y = start_y + row * (height + spacing_y)
            rect = pygame.Rect(x, y, width, height)
            self.card_rects.append((rect, letter))

    # ------------------------------------------------------------------
    # Pygame interface
    # ------------------------------------------------------------------
    def update(self) -> None:
        """No dynamic updates required."""

    def draw(self) -> None:
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((60, 40, 25))

        instruction_rect = self.instruction_surface.get_rect(center=(self.screen_rect.centerx, 160))
        self.screen.blit(self.instruction_surface, instruction_rect)

        prompt_rect = self.prompt_surface.get_rect(center=(self.screen_rect.centerx, self.screen_rect.height - 90))
        self.screen.blit(self.prompt_surface, prompt_rect)

        if not self.has_cards:
            return

        mouse_pos = pygame.mouse.get_pos()
        hovered_index: Optional[int] = None
        for idx, (rect, letter) in enumerate(self.card_rects):
            image = self.letter_images.get(letter)
            if not image:
                continue

            self.screen.blit(image, rect)

            if rect.collidepoint(mouse_pos):
                hovered_index = idx

        if hovered_index is not None:
            rect, _ = self.card_rects[hovered_index]
            border_rect = rect.inflate(12, 12)
            pygame.draw.rect(self.screen, (255, 225, 120), border_rect, width=4, border_radius=8)

    def handle_event(self, event: pygame.event.Event) -> Optional[dict]:
        if self._result_reported:
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.has_cards:
                return self._finalize(None)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.has_cards:
                return self._finalize(None)

            for rect, letter in self.card_rects:
                if rect.collidepoint(event.pos):
                    success = game_state.return_alphabet_card(letter)
                    if success:
                        return self._finalize(letter)
                    break

        return None

    def _finalize(self, letter: Optional[str]) -> Optional[dict]:
        if self._result_reported:
            return None
        self._result_reported = True
        return {
            'result': 'alphabet-lose',
            'returned': letter,
        }
