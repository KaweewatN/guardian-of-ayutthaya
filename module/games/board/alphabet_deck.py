"""HUD widget that displays collected alphabet cards."""

from __future__ import annotations

import os
from typing import List, Tuple, Optional

import pygame

# Import fonts via constant module irrespective of execution context
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in os.sys.path:
    os.sys.path.insert(0, _CONSTANT_BASE)

try:  # pragma: no cover - runtime dependency
    from fonts import TEXT_FONT, TEXT_FONT_BOLD
except Exception:  # pragma: no cover - fallback when fonts unavailable
    TEXT_FONT = pygame.font.SysFont('Arial', 22)
    TEXT_FONT_BOLD = pygame.font.SysFont('Arial', 24, bold=True)

# Import global game state manager
_MODULE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _MODULE_BASE not in os.sys.path:
    os.sys.path.insert(0, _MODULE_BASE)

from game_state import game_state


class AlphabetDeck:
    """Render the alphabet deck status on the board screen."""

    WORD = "AYUTTHAYA"

    def __init__(self, screen: pygame.Surface, dice=None) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.dice = dice

        self.bg_image = self._load_background()
        self.bg_rect = self.bg_image.get_rect() if self.bg_image else pygame.Rect(0, 0, 360, 240)

        self.card_size = (42, 64)
        self.top_slots: List[Tuple[int, int]] = []
        self.extra_slots: List[Tuple[int, int]] = []
        self.letter_images = self._load_letter_images()

        self.text_font = TEXT_FONT
        self.text_font_bold = TEXT_FONT_BOLD

        self._compute_layout()

    # ------------------------------------------------------------------
    # Asset loading helpers
    # ------------------------------------------------------------------
    def _assets_path(self, *paths: str) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base, 'assets', *paths)

    def _load_background(self) -> pygame.Surface:
        path = self._assets_path('core', 'alphabet-deck.png')
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return img
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Warning: failed to load alphabet deck background {path}: {exc}")
        else:
            print(f"Warning: alphabet deck background not found: {path}")
        # fallback blank surface
        surface = pygame.Surface((360, 240), pygame.SRCALPHA)
        surface.fill((40, 24, 12, 210))
        pygame.draw.rect(surface, (255, 220, 150), surface.get_rect(), width=3, border_radius=12)
        return surface

    def _load_letter_images(self) -> dict[str, pygame.Surface]:
        images: dict[str, pygame.Surface] = {}
        width, height = self.card_size
        for letter in ['A', 'Y', 'U', 'T', 'H']:
            path = self._assets_path('alphabet', 'letter', f"{letter.lower()}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    images[letter] = pygame.transform.smoothscale(img, (width, height))
                except Exception as exc:  # pragma: no cover
                    print(f"Warning: unable to load letter {path}: {exc}")
            else:
                print(f"Warning: letter card missing: {path}")
        return images

    # ------------------------------------------------------------------
    # Layout calculation
    # ------------------------------------------------------------------
    def _compute_layout(self) -> None:
        bg_width = self.bg_rect.width
        bg_height = self.bg_rect.height

        if self.dice and hasattr(self.dice, 'bg_x') and hasattr(self.dice, 'bg_y'):
            x = self.dice.bg_x
            y = max(140, self.dice.bg_y - bg_height - 36)
        else:
            x = self.screen_rect.width - bg_width - 90
            y = 180

        self.bg_position = (int(x), int(y))

        slot_width, slot_height = self.card_size

        top_margin_x = 18
        top_margin_y = 58
        if len(self.WORD) > 1:
            slot_spacing = (bg_width - 2 * top_margin_x - len(self.WORD) * slot_width) / (len(self.WORD) - 1)
        else:
            slot_spacing = 0
        slot_spacing = max(6, slot_spacing)

        self.top_slots = []
        for index in range(len(self.WORD)):
            slot_x = self.bg_position[0] + top_margin_x + int(index * (slot_width + slot_spacing))
            slot_y = self.bg_position[1] + top_margin_y
            self.top_slots.append((slot_x, slot_y))

        # Extra slots arranged in two rows
        extra_rows = 2
        extra_columns = 8
        extra_margin_x = 18
        extra_margin_y = top_margin_y + slot_height + 52
        if extra_columns > 1:
            extra_spacing_x = (bg_width - 2 * extra_margin_x - extra_columns * slot_width) / (extra_columns - 1)
        else:
            extra_spacing_x = 0
        extra_spacing_x = max(6, extra_spacing_x)
        extra_spacing_y = slot_height + 16

        self.extra_slots = []
        for row in range(extra_rows):
            for col in range(extra_columns):
                slot_x = self.bg_position[0] + extra_margin_x + int(col * (slot_width + extra_spacing_x))
                slot_y = self.bg_position[1] + extra_margin_y + int(row * extra_spacing_y)
                self.extra_slots.append((slot_x, slot_y))

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def update(self) -> None:
        """Currently static but kept for consistency."""

    def draw(self) -> None:
        self.screen.blit(self.bg_image, self.bg_position)

        counts = game_state.get_player_alphabet_counts()

        used_for_word = {letter: 0 for letter in counts}
        top_letters: List[Optional[str]] = []
        for letter in self.WORD:
            collected = counts.get(letter, 0)
            used = used_for_word.get(letter, 0)
            if collected > used:
                top_letters.append(letter)
                used_for_word[letter] = used + 1
            else:
                top_letters.append(None)

        extras: List[str] = []
        for letter, collected in counts.items():
            remaining = collected - used_for_word.get(letter, 0)
            if remaining > 0:
                extras.extend([letter] * remaining)

        # Draw top row frames and letters
        slot_width, slot_height = self.card_size
        frame_color = (255, 221, 142)
        empty_color = (120, 80, 40)

        for (x, y), letter in zip(self.top_slots, top_letters):
            rect = pygame.Rect(x, y, slot_width, slot_height)
            pygame.draw.rect(self.screen, frame_color, rect.inflate(8, 8), border_radius=6, width=3)
            if letter and letter in self.letter_images:
                self.screen.blit(self.letter_images[letter], rect)
            else:
                pygame.draw.rect(self.screen, empty_color, rect, border_radius=4)

        # Draw extra letters
        for (x, y), letter in zip(self.extra_slots, extras):
            rect = pygame.Rect(x, y, slot_width, slot_height)
            pygame.draw.rect(self.screen, (90, 58, 32), rect.inflate(6, 6), border_radius=4)
            if letter in self.letter_images:
                self.screen.blit(self.letter_images[letter], rect)

        # Text summary at bottom-left of widget
        summary_lines = []
        for letter in ['A', 'Y', 'U', 'T', 'H']:
            summary_lines.append(f"{letter}: {counts.get(letter, 0)}")

        summary_surface = self._render_summary(summary_lines)
        summary_pos = (
            self.bg_position[0] + 18,
            self.bg_position[1] + self.bg_rect.height - summary_surface.get_height() - 18,
        )
        self.screen.blit(summary_surface, summary_pos)

    def _render_summary(self, lines: List[str]) -> pygame.Surface:
        padding = 6
        text_surfaces = [self.text_font.render(line, True, (255, 240, 200)) for line in lines]
        width = max(surface.get_width() for surface in text_surfaces) + padding * 2
        height = sum(surface.get_height() for surface in text_surfaces) + padding * (len(text_surfaces) + 1)

        summary_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        summary_surface.fill((24, 16, 8, 160))

        y = padding
        for surface in text_surfaces:
            summary_surface.blit(surface, (padding, y))
            y += surface.get_height() + padding

        return summary_surface
