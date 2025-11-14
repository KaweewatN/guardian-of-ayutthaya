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
        self.base_bg_size = self.bg_rect.size

        self.scale_factor = self._determine_scale_factor()
        if self.bg_image and self.scale_factor != 1.0:
            scaled_size = (
                max(120, int(self.base_bg_size[0] * self.scale_factor)),
                max(100, int(self.base_bg_size[1] * self.scale_factor)),
            )
            self.bg_image = pygame.transform.smoothscale(self.bg_image, scaled_size)
            self.bg_rect = self.bg_image.get_rect()

        self.card_size = self._scaled_card_size()
        self.top_slots: List[Tuple[int, int]] = []
        self.extra_slots: List[Tuple[int, int]] = []
        self.letter_images = self._load_letter_images()

        self.text_font = TEXT_FONT
        self.text_font_bold = TEXT_FONT_BOLD

        # Expanded view state
        self.is_expanded = False
        self.view_button_rect = pygame.Rect(0, 0, 100, 30)
        self.close_button_rect = pygame.Rect(0, 0, 50, 50)
        self.view_button_hover = False
        self.close_button_hover = False
        self.button_font = pygame.font.SysFont('Arial', 16, bold=True)

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
    def _determine_scale_factor(self) -> float:
        """Compute a scaling factor so the deck matches the dice section height."""
        if not self.bg_rect:
            return 1.0

        target_height = None
        if self.dice:
            dice_height = 0
            dice_bg = getattr(self.dice, 'dice_bg_image', None)
            if dice_bg:
                dice_height += dice_bg.get_height()
            else:
                dice_height += getattr(self.dice, 'dice_size', 0) + 40

            button_rect = getattr(self.dice, 'button_rect', None)
            if button_rect:
                dice_height += 20 + button_rect.height

            if dice_height > 0:
                target_height = dice_height

        if target_height:
            scale = target_height / self.bg_rect.height
            scale *= 0.9
            return max(0.35, min(scale, 1.0))

        return 1.0

    def _scaled_card_size(self) -> Tuple[int, int]:
        width = max(18, int(42 * self.scale_factor))
        height = max(28, int(64 * self.scale_factor))
        return width, height

    def _scale_length(self, base: int, minimum: int = 0) -> int:
        scaled = int(round(base * self.scale_factor))
        if minimum:
            return max(minimum, scaled)
        return scaled

    def _compute_layout(self) -> None:
        bg_width = self.bg_rect.width
        bg_height = self.bg_rect.height

        if self.dice and hasattr(self.dice, 'bg_x') and hasattr(self.dice, 'bg_y'):
            x = self.screen_rect.width - bg_width - 10
            y = max(140, self.dice.bg_y - bg_height - 80)
        else:
            x = self.screen_rect.width - bg_width - 90
            y = 180

        self.bg_position = (int(x), int(y))

        slot_width, slot_height = self.card_size

        top_margin_x = self._scale_length(18, minimum=10)
        top_margin_y = self._scale_length(110, minimum=30)
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
        extra_margin_x = self._scale_length(18, minimum=10)
        extra_margin_y = top_margin_y + slot_height + self._scale_length(52, minimum=24)
        if extra_columns > 1:
            extra_spacing_x = (bg_width - 2 * extra_margin_x - extra_columns * slot_width) / (extra_columns - 1)
        else:
            extra_spacing_x = 0
        extra_spacing_x = max(6, extra_spacing_x)
        extra_spacing_y = slot_height + self._scale_length(16, minimum=8)

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

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for view/close buttons. Returns True if event was handled."""
        if event.type == pygame.MOUSEMOTION:
            if self.is_expanded:
                self.close_button_hover = self.close_button_rect.collidepoint(event.pos)
            else:
                self.view_button_hover = self.view_button_rect.collidepoint(event.pos)
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_expanded:
                if self.close_button_rect.collidepoint(event.pos):
                    self.is_expanded = False
                    return True
            else:
                if self.view_button_rect.collidepoint(event.pos):
                    self.is_expanded = True
                    return True
        
        return False

    def draw(self) -> None:
        if self.is_expanded:
            self._draw_expanded_view()
        else:
            self._draw_compact_view()

    def _draw_compact_view(self) -> None:
        """Draw the normal small view at top-right."""
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

        # Draw "View Cards" button inside the deck at bottom center
        self._draw_view_button()

    def _draw_view_button(self) -> None:
        """Draw the 'View Cards' button inside the deck at bottom center."""
        # Position button at bottom center of the deck, inside the background
        button_x = self.bg_position[0] + (self.bg_rect.width - self.view_button_rect.width) // 2
        button_y = self.bg_position[1] + self.bg_rect.height - self.view_button_rect.height - 15
        self.view_button_rect.topleft = (button_x, button_y)

        # Dark brown button colors
        bg_color = (100, 70, 50) if self.view_button_hover else (70, 50, 35)
        border_color = (50, 35, 25)
        text_color = (255, 255, 255)

        # Draw button
        pygame.draw.rect(self.screen, bg_color, self.view_button_rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, self.view_button_rect, width=2, border_radius=6)

        # Draw text with smaller font
        button_text = self.button_font.render("View Cards", True, text_color)
        text_rect = button_text.get_rect(center=self.view_button_rect.center)
        self.screen.blit(button_text, text_rect)

    def _draw_expanded_view(self) -> None:
        """Draw a large centered view of the alphabet deck."""
        # Semi-transparent backdrop
        backdrop = pygame.Surface((self.screen_rect.width, self.screen_rect.height), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 180))
        self.screen.blit(backdrop, (0, 0))

        # Scale up the background (2.0x to fit better on screen)
        expanded_scale = 2.0
        expanded_width = int(self.base_bg_size[0] * expanded_scale)
        expanded_height = int(self.base_bg_size[1] * expanded_scale)
        
        # Ensure it fits on screen with padding
        max_width = self.screen_rect.width - 100
        max_height = self.screen_rect.height - 100
        if expanded_width > max_width:
            scale_factor = max_width / expanded_width
            expanded_width = max_width
            expanded_height = int(expanded_height * scale_factor)
            expanded_scale *= scale_factor
        if expanded_height > max_height:
            scale_factor = max_height / expanded_height
            expanded_height = max_height
            expanded_width = int(expanded_width * scale_factor)
            expanded_scale *= scale_factor
        
        # Load and scale background
        expanded_bg = pygame.transform.smoothscale(
            self._load_background(), 
            (expanded_width, expanded_height)
        )
        
        # Center position
        expanded_x = (self.screen_rect.width - expanded_width) // 2
        expanded_y = (self.screen_rect.height - expanded_height) // 2
        
        self.screen.blit(expanded_bg, (expanded_x, expanded_y))

        # Calculate expanded card size and slots
        expanded_card_width = int(42 * expanded_scale)
        expanded_card_height = int(64 * expanded_scale)
        
        # Load scaled letter images
        expanded_letter_images = {}
        for letter in ['A', 'Y', 'U', 'T', 'H']:
            path = self._assets_path('alphabet', 'letter', f"{letter.lower()}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    expanded_letter_images[letter] = pygame.transform.smoothscale(
                        img, (expanded_card_width, expanded_card_height)
                    )
                except Exception:
                    pass

        # Get counts
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

        # Draw top row (AYUTTHAYA)
        top_margin_x = int(18 * expanded_scale)
        top_margin_y = int(110 * expanded_scale)
        
        if len(self.WORD) > 1:
            slot_spacing = (expanded_width - 2 * top_margin_x - len(self.WORD) * expanded_card_width) / (len(self.WORD) - 1)
        else:
            slot_spacing = 0
        slot_spacing = max(10, slot_spacing)

        frame_color = (255, 221, 142)
        empty_color = (120, 80, 40)

        for index, letter in enumerate(top_letters):
            slot_x = expanded_x + top_margin_x + int(index * (expanded_card_width + slot_spacing))
            slot_y = expanded_y + top_margin_y
            rect = pygame.Rect(slot_x, slot_y, expanded_card_width, expanded_card_height)
            
            pygame.draw.rect(self.screen, frame_color, rect.inflate(12, 12), border_radius=8, width=4)
            if letter and letter in expanded_letter_images:
                self.screen.blit(expanded_letter_images[letter], rect)
            else:
                pygame.draw.rect(self.screen, empty_color, rect, border_radius=6)

        # Draw extra letters (2 rows, 8 columns) - only up to 16 slots
        extra_rows = 2
        extra_columns = 8
        max_extra_slots = extra_rows * extra_columns  # 16 slots max
        extra_margin_x = int(18 * expanded_scale)
        extra_margin_y = top_margin_y + expanded_card_height + int(52 * expanded_scale)
        
        if extra_columns > 1:
            extra_spacing_x = (expanded_width - 2 * extra_margin_x - extra_columns * expanded_card_width) / (extra_columns - 1)
        else:
            extra_spacing_x = 0
        extra_spacing_x = max(10, extra_spacing_x)
        extra_spacing_y = expanded_card_height + int(16 * expanded_scale)

        # Only draw extras that fit in the grid (max 16)
        extras_to_draw = extras[:max_extra_slots]
        
        extra_index = 0
        for row in range(extra_rows):
            for col in range(extra_columns):
                if extra_index >= len(extras_to_draw):
                    break
                letter = extras_to_draw[extra_index]
                slot_x = expanded_x + extra_margin_x + int(col * (expanded_card_width + extra_spacing_x))
                slot_y = expanded_y + extra_margin_y + int(row * extra_spacing_y)
                rect = pygame.Rect(slot_x, slot_y, expanded_card_width, expanded_card_height)
                
                pygame.draw.rect(self.screen, (90, 58, 32), rect.inflate(10, 10), border_radius=6)
                if letter in expanded_letter_images:
                    self.screen.blit(expanded_letter_images[letter], rect)
                extra_index += 1
            if extra_index >= len(extras_to_draw):
                break

        # Draw close button (X)
        self._draw_close_button(expanded_x, expanded_y, expanded_width)

    def _draw_close_button(self, deck_x=None, deck_y=None, deck_width=None) -> None:
        """Draw the close (X) button for expanded view."""
        # Position close button at top-right of the expanded deck
        if deck_x is not None and deck_width is not None:
            self.close_button_rect.topright = (deck_x + deck_width - 10, deck_y + 10)
        
        # Button colors
        bg_color = (220, 60, 60) if self.close_button_hover else (180, 40, 40)
        border_color = (140, 20, 20)
        text_color = (255, 255, 255)

        # Draw button
        pygame.draw.rect(self.screen, bg_color, self.close_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, self.close_button_rect, width=3, border_radius=8)

        # Draw X using lines instead of unicode character for better visibility
        center_x = self.close_button_rect.centerx
        center_y = self.close_button_rect.centery
        offset = 12
        
        # Draw two diagonal lines forming an X
        pygame.draw.line(self.screen, text_color, 
                        (center_x - offset, center_y - offset), 
                        (center_x + offset, center_y + offset), 4)
        pygame.draw.line(self.screen, text_color, 
                        (center_x + offset, center_y - offset), 
                        (center_x - offset, center_y + offset), 4)

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
