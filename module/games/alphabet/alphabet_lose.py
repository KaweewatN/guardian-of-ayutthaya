"""Alphabet return screen shown when a bad card is drawn."""

from __future__ import annotations

import math
import os
from collections import Counter
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

    WORD = "AYUTTHAYA"

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.cards: List[str] = sorted(game_state.list_player_alphabet_cards())
        self.has_cards = bool(self.cards)

        self.background = self._load_background('tutorial-bg.png')
        self.card_size: Tuple[int, int] = (80, 120)
        self.deck_surface: Optional[pygame.Surface] = None
        self.deck_rect = pygame.Rect(0, 0, 0, 0)
        self.slot_frames: List[Tuple[pygame.Rect, Optional[str], str]] = []
        self.card_rects: List[Tuple[pygame.Rect, str]] = []
        self.hovered_index: Optional[int] = None
        self.selected_index: Optional[int] = None
        self.selected_letter: Optional[str] = None
        self.state: str = 'selecting' if self.has_cards else 'no-cards'

        self._compute_layout()
        self.text_font = TEXT_FONT
        self.button_font = BUTTON_FONT

        info_color = (210, 180, 120)
        confirm_color = (245, 230, 190)

        self.base_letter_images: dict[str, pygame.Surface] = {}
        self.letter_images: dict[str, pygame.Surface] = self._load_letter_images()

        if self.has_cards:
            message = "Select one card to return to the deck"
        else:
            message = "You do not have any alphabet cards yet."
        self.primary_instruction_surface = self.button_font.render(message, True, info_color)

        self.selected_instruction_surface = self.text_font.render(
            "Press SPACE or CLICK to confirm your choice", True, confirm_color
        )

        self.prompt_surface = self.text_font.render(
            "Press SPACE or CLICK to continue", True, (255, 255, 255)
        )

        self.confirm_instruction_surface = self.text_font.render(
            "to the deck", True, confirm_color
        )

        self.confirm_text_color = (255, 240, 210)

        self._result_reported = False

    # ------------------------------------------------------------------
    # Asset helpers
    # ------------------------------------------------------------------
    def _assets_path(self, *paths: str) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base, 'assets', 'alphabet', *paths)

    def _load_background(self, filename: str) -> Optional[pygame.Surface]:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        path = os.path.join(base, 'assets', 'core', filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.screen_rect.width, self.screen_rect.height))
            except Exception as exc:  # pragma: no cover
                print(f"Warning: failed to load {path}: {exc}")
        else:
            print(f"Warning: background not found: {path}")
        return None

    def _load_letter_images(self) -> dict[str, pygame.Surface]:
        images: dict[str, pygame.Surface] = {}
        width, height = self.card_size
        for letter in sorted(game_state.get_alphabet_deck_counts().keys()):
            path = self._assets_path('letter', f"{letter.lower()}.png")
            original: Optional[pygame.Surface] = None
            if os.path.exists(path):
                try:
                    original = pygame.image.load(path).convert_alpha()
                except Exception as exc:  # pragma: no cover
                    print(f"Warning: unable to load letter card {path}: {exc}")
            else:
                print(f"Warning: letter card missing: {path}")

            if original is None:
                original = pygame.Surface((width, height), pygame.SRCALPHA)
                original.fill((90, 58, 32, 255))
                pygame.draw.rect(original, (255, 221, 142), original.get_rect(), width=4, border_radius=8)

            self.base_letter_images[letter] = original
            images[letter] = pygame.transform.smoothscale(original, (width, height))

        return images

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _compute_layout(self) -> None:
        """Compute card slot positions mirroring the board deck layout."""

        word_length = len(self.WORD)
        max_width = min(860, max(520, self.screen_rect.width - 80))
        margin_x = max(36, int(max_width * 0.06))
        spacing_x = max(12, int(max_width * 0.035))

        available_width = max_width - 2 * margin_x - (word_length - 1) * spacing_x
        card_width = max(54, min(int(available_width / word_length), 120))
        deck_width = 2 * margin_x + word_length * card_width + (word_length - 1) * spacing_x

        if deck_width > max_width:
            card_width = max(48, int((max_width - 2 * margin_x - (word_length - 1) * spacing_x) / word_length))
            deck_width = 2 * margin_x + word_length * card_width + (word_length - 1) * spacing_x

        card_height = int(card_width * 1.45)
        upper_margin = max(40, int(card_height * 0.55))
        bottom_margin = max(40, int(card_height * 0.55))
        top_to_extra_gap = max(32, int(card_height * 0.45))
        extra_spacing_y = max(12, int(card_height * 0.2))

        counts = Counter(self.cards)
        top_letters: List[Optional[str]] = []
        for letter in self.WORD:
            if counts.get(letter, 0) > 0:
                top_letters.append(letter)
                counts[letter] -= 1
            else:
                top_letters.append(None)

        extras: List[str] = []
        for letter in sorted(counts.elements()):
            extras.append(letter)

        extra_columns = word_length
        extra_rows = math.ceil(len(extras) / extra_columns) if extras else 0

        deck_height = upper_margin + card_height + bottom_margin
        if extra_rows > 0:
            deck_height = (
                upper_margin
                + card_height
                + top_to_extra_gap
                + extra_rows * card_height
                + max(0, extra_rows - 1) * extra_spacing_y
                + bottom_margin
            )

        self.card_size = (card_width, card_height)

        self.deck_surface = pygame.Surface((deck_width, deck_height), pygame.SRCALPHA)
        self.deck_surface.fill((40, 24, 12, 235))
        pygame.draw.rect(self.deck_surface, (255, 221, 142), self.deck_surface.get_rect(), width=4, border_radius=16)
        inner_rect = self.deck_surface.get_rect().inflate(-12, -12)
        pygame.draw.rect(self.deck_surface, (70, 50, 35), inner_rect, border_radius=12)

        self.deck_rect = self.deck_surface.get_rect()
        base_center_y = self.screen_rect.centery + (40 if self.has_cards else 0)
        min_center_y = 220
        max_center_y = self.screen_rect.height - self.deck_rect.height // 2 - 80
        if max_center_y < min_center_y:
            deck_center_y = (min_center_y + max_center_y) / 2
        else:
            deck_center_y = min(max_center_y, max(min_center_y, base_center_y))
        self.deck_rect.center = (self.screen_rect.centerx, int(deck_center_y))

        self.slot_frames.clear()
        self.card_rects.clear()

        top_start_x = self.deck_rect.left + margin_x
        top_start_y = self.deck_rect.top + upper_margin

        for index in range(word_length):
            slot_x = top_start_x + index * (card_width + spacing_x)
            slot_rect = pygame.Rect(slot_x, top_start_y, card_width, card_height)
            letter = top_letters[index]
            self.slot_frames.append((slot_rect, letter, 'top'))
            if letter:
                self.card_rects.append((slot_rect, letter))

        if extra_rows > 0:
            extra_start_y = top_start_y + card_height + top_to_extra_gap
            for row in range(extra_rows):
                for col in range(extra_columns):
                    slot_index = row * extra_columns + col
                    slot_x = top_start_x + col * (card_width + spacing_x)
                    slot_y = extra_start_y + row * (card_height + extra_spacing_y)
                    slot_rect = pygame.Rect(slot_x, slot_y, card_width, card_height)
                    letter = extras[slot_index] if slot_index < len(extras) else None
                    self.slot_frames.append((slot_rect, letter, 'extra'))
                    if letter:
                        self.card_rects.append((slot_rect, letter))

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

        if self.state == 'confirm' and self.selected_letter:
            self._draw_confirm_view()
        else:
            self._draw_selection_view()

        prompt_rect = self.prompt_surface.get_rect(center=(self.screen_rect.centerx, self.screen_rect.height - 90))
        self.screen.blit(self.prompt_surface, prompt_rect)

    def handle_event(self, event: pygame.event.Event) -> Optional[dict]:
        if self._result_reported:
            return None

        if self.state == 'no-cards':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return self._finalize(None)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self._finalize(None)
            return None

        if not self.has_cards:
            return None

        if self.state in ('selecting', 'selected'):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.selected_letter:
                    self.state = 'confirm'
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_index: Optional[int] = None
                for idx, (rect, _) in enumerate(self.card_rects):
                    if rect.collidepoint(event.pos):
                        clicked_index = idx
                        break

                if clicked_index is not None:
                    self.selected_index = clicked_index
                    self.selected_letter = self.card_rects[clicked_index][1]
                    self.state = 'selected'
                elif self.selected_letter:
                    self.state = 'confirm'
                return None

        if self.state == 'confirm':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return self._return_selected_card()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self._return_selected_card()

        return None

    def _finalize(self, letter: Optional[str]) -> Optional[dict]:
        if self._result_reported:
            return None
        self._result_reported = True
        self.state = 'finished'
        return {
            'result': 'alphabet-lose',
            'returned': letter,
        }

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _draw_selection_view(self) -> None:
        instruction_rect = self.primary_instruction_surface.get_rect(center=(self.screen_rect.centerx, 150))
        self.screen.blit(self.primary_instruction_surface, instruction_rect)

        show_confirm_hint = self.has_cards and self.selected_letter and self.state == 'selected'
        if show_confirm_hint:
            hint_rect = self.selected_instruction_surface.get_rect(
                center=(self.screen_rect.centerx, instruction_rect.bottom + 36)
            )
            self.screen.blit(self.selected_instruction_surface, hint_rect)

        hovered_index: Optional[int] = None
        if self.card_rects and self.state in ('selecting', 'selected'):
            mouse_pos = pygame.mouse.get_pos()
            for idx, (rect, _) in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    hovered_index = idx
                    break

        self.hovered_index = hovered_index
        self._draw_slots(hovered_index)

    def _draw_slots(self, hovered_index: Optional[int]) -> None:
        if not self.deck_surface:
            return

        self.screen.blit(self.deck_surface, self.deck_rect.topleft)

        top_frame_color = (255, 221, 142)
        empty_slot_color = (120, 80, 40)
        extra_slot_color = (90, 58, 32)

        for rect, letter, slot_type in self.slot_frames:
            if slot_type == 'top':
                pygame.draw.rect(self.screen, top_frame_color, rect.inflate(10, 10), width=3, border_radius=10)
                if letter and letter in self.letter_images:
                    self.screen.blit(self.letter_images[letter], rect)
                else:
                    pygame.draw.rect(self.screen, empty_slot_color, rect, border_radius=8)
            else:
                pygame.draw.rect(self.screen, extra_slot_color, rect.inflate(6, 6), border_radius=6)
                if letter and letter in self.letter_images:
                    self.screen.blit(self.letter_images[letter], rect)

        highlight_color = (255, 230, 140)
        selected_color = (255, 215, 80)

        if hovered_index is not None and hovered_index != self.selected_index and self.state in ('selecting', 'selected'):
            rect = self.card_rects[hovered_index][0]
            pygame.draw.rect(self.screen, highlight_color, rect.inflate(12, 12), width=4, border_radius=10)

        if self.selected_index is not None and self.selected_index < len(self.card_rects):
            rect = self.card_rects[self.selected_index][0]
            pygame.draw.rect(self.screen, selected_color, rect.inflate(16, 16), width=5, border_radius=12)

    def _draw_confirm_view(self) -> None:
        letter = (self.selected_letter or "?").upper()
        message = f"Return {letter}"
        message_surface = self.button_font.render(message, True, self.confirm_text_color)

        frame_width = max(260, min(self.screen_rect.width - 140, int(self.screen_rect.width * 0.7)))
        frame_height = max(220, min(self.screen_rect.height - 200, int(self.screen_rect.height * 0.55)))
        confirm_rect = pygame.Rect(0, 0, frame_width, frame_height)
        confirm_rect.center = (self.screen_rect.centerx, self.screen_rect.centery + 20)

        frame_surface = pygame.Surface(confirm_rect.size, pygame.SRCALPHA)
        frame_surface.fill((40, 24, 12, 235))
        pygame.draw.rect(frame_surface, (255, 221, 142), frame_surface.get_rect(), width=4, border_radius=18)
        inner_rect = frame_surface.get_rect().inflate(-24, -24)
        pygame.draw.rect(frame_surface, (70, 50, 35), inner_rect, border_radius=14)

        self.screen.blit(frame_surface, confirm_rect.topleft)

        message_rect = message_surface.get_rect(center=(self.screen_rect.centerx, confirm_rect.top + 45))
        self.screen.blit(message_surface, message_rect)

        confirm_hint_rect = self.confirm_instruction_surface.get_rect(
            center=(self.screen_rect.centerx, confirm_rect.bottom - 40)
        )
        self.screen.blit(self.confirm_instruction_surface, confirm_hint_rect)

        if self.selected_letter:
            max_width = max(1, int(inner_rect.width * 0.4))
            max_height = max(1, int(inner_rect.height * 0.6))
            card_image = self._get_scaled_letter_image(self.selected_letter, max_width, max_height)
            if card_image:
                card_rect = card_image.get_rect()
                inner_rect_global = inner_rect.move(confirm_rect.topleft)
                card_rect.center = inner_rect_global.center
                self.screen.blit(card_image, card_rect)

    def _get_scaled_letter_image(self, letter: str, max_width: int, max_height: int) -> Optional[pygame.Surface]:
        base_image = self.base_letter_images.get(letter)
        if not base_image:
            return self.letter_images.get(letter)

        width, height = base_image.get_size()
        if width == 0 or height == 0:
            return None

        scale = min(max_width / width, max_height / height)
        scale = min(scale, 2.5)
        if scale <= 0:
            return None

        scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        return pygame.transform.smoothscale(base_image, scaled_size)

    def _return_selected_card(self) -> Optional[dict]:
        if not self.selected_letter:
            return None

        success = game_state.return_alphabet_card(self.selected_letter)
        if not success:
            return self._finalize(None)
        return self._finalize(self.selected_letter)
