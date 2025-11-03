"""Interactive math puzzle event for block 3."""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

import pygame

# Import shared fonts with a graceful fallback similar to other modules.
try:
    from constant.fonts import (
        BUTTON_FONT,
        BUTTON_FONT_LARGE,
        TEXT_FONT,
        TEXT_FONT_BOLD,
        SUBTITLE_FONT,
    )
except Exception:
    try:
        const_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "constant")
        )
        if const_path not in sys.path:
            sys.path.insert(0, const_path)
        from fonts import (  # type: ignore
            BUTTON_FONT,
            BUTTON_FONT_LARGE,
            TEXT_FONT,
            TEXT_FONT_BOLD,
            SUBTITLE_FONT,
        )
    except Exception as exc:  # pragma: no cover - pygame fallback
        print(f"Warning: Fonts import failed ({exc}). Using pygame fallback fonts.")
        pygame.font.init()

        def _fallback_font(size: int) -> pygame.font.Font:
            return pygame.font.SysFont(None, size)

        BUTTON_FONT = _fallback_font(24)
        BUTTON_FONT_LARGE = _fallback_font(32)
        TEXT_FONT = _fallback_font(28)
        TEXT_FONT_BOLD = _fallback_font(30)
        SUBTITLE_FONT = _fallback_font(30)


class MathEvent:
    """Intro sequence followed by a timed arithmetic puzzle."""

    STATE_INTRO_1 = "intro_1"
    STATE_INTRO_2 = "intro_2"
    STATE_PUZZLE = "puzzle"
    STATE_RESULT_SUCCESS = "result_success"
    STATE_RESULT_FAILURE = "result_failure"
    STATE_SKIPPED = "skipped"

    RESULT_EVENT = pygame.USEREVENT + 42
    RESULT_DELAY_MS = 1500
    TIMER_LIMIT_MS = 20_000

    DIGITS: Sequence[int] = (2, 3, 4, 9)

    def __init__(self, screen: pygame.Surface, block_number: int = 3) -> None:
        self.screen = screen
        self.block_number = block_number
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.scale_x = self.screen_width / 1280
        self.scale_y = self.screen_height / 832
        self.scale_min = min(self.scale_x, self.scale_y)

        self.state = self.STATE_INTRO_1
        self.finished = False
        self.pending_result: Optional[Dict[str, str]] = None

        # --- Text content -------------------------------------------------
        self.intro_texts = [
            "This is Wat Na Phra Men, /brthe only temple untouched by war. /br"
            "Once a royal cremation ground,/brnow it shelters a bronze Buddha in royal robes./br"
            "a peaceful witness to Ayutthaya’s fall and rebirth/br",
            "Solve this to get the /br alphabet cards./br2, 3, 4, 9 Can you make 24?",
        ]
        self.success_text = "Well done! You receive the letter"
        self.failure_text = "That’s not 24 yet. Try again."

        # Intro text layout (smaller font, no background panel)
        intro_font_size = max(22, int(30 * self.scale_min))
        self.intro_font = pygame.font.SysFont("Inknut Antiqua", intro_font_size)
        if self.intro_font is None:
            self.intro_font = pygame.font.SysFont(None, intro_font_size)
        self.intro_line_height = max(int(self.intro_font.get_linesize() * 1.15), 24)
        self.intro_rect = pygame.Rect(
            int(160 * self.scale_x),
            int(120 * self.scale_y),
            int(960 * self.scale_x),
            int(360 * self.scale_y),
        )
        instruction_font_size = max(18, int(80 * self.scale_min))
        self.intro_instruction_font = pygame.font.SysFont(
            "Inknut Antiqua", instruction_font_size
        )
        if self.intro_instruction_font is None:
            self.intro_instruction_font = pygame.font.SysFont(None, instruction_font_size)

        # Result dialog layout retains soft panel background
        self.dialog_rect = self._scaled_rect(250, 170, 780, 280)
        self.dialog_font = SUBTITLE_FONT
        self.dialog_line_height = int(36 * self.scale_y)

        # --- Imagery ------------------------------------------------------
        self.background_intro = self._load_scaled_image(
            f"assets/scene/event/math/blocks/{self.block_number}.png"
        )
        self.background_puzzle = self._load_scaled_image(
            f"assets/scene/empty/{self.block_number}.png"
        )
        self.background_result = self.background_intro

        # --- Puzzle state -------------------------------------------------
        self.selected_slot: Optional[int] = None
        self.slot_values: List[Optional[int]] = [None, None, None, None]
        self.timer_start: Optional[int] = None
        self.timer_expired = False
        self.digit_display_rects: List[pygame.Rect] = []

        # Central puzzle layout
        panel_width = max(int(900 * self.scale_x), 600)
        panel_height = max(int(150 * self.scale_y), 110)
        self.panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        self.panel_rect.center = (
            self.screen_width // 2,
            self.screen_height // 2,
        )

        slot_side = max(int(96 * self.scale_min), 72)
        self.slot_rects = []
        slot_step = self.panel_rect.width / (len(self.slot_values) + 1)
        for index in range(len(self.slot_values)):
            center_x = self.panel_rect.left + slot_step * (index + 1)
            rect = pygame.Rect(0, 0, slot_side, slot_side)
            rect.center = (int(center_x), self.panel_rect.centery)
            self.slot_rects.append(rect)

        self.section_gap = max(int(90 * self.scale_y), 70)

        submit_width = max(int(243 * self.scale_x), 200)
        submit_height = max(int(78 * self.scale_y), 60)
        self.submit_rect = pygame.Rect(0, 0, submit_width, submit_height)
        self.submit_rect.center = (
            self.screen_width // 2,
            self.panel_rect.bottom + self.section_gap + submit_height // 2,
        )
        inner_height = max(submit_height - int(18 * self.scale_y), submit_height - 20)
        inner_width = max(submit_width - int(24 * self.scale_x), submit_width - 24)
        self.submit_inner_rect = pygame.Rect(
            0,
            0,
            inner_width,
            inner_height,
        )
        self.submit_inner_rect.center = self.submit_rect.center

        self.timer_center = (
            self.screen_width // 2,
            max(int(50 * self.scale_y), self.panel_rect.top - self.section_gap - int(20 * self.scale_y)),
        )

        # Fonts for puzzle overlay
        base_operator_size = max(32, int(64 * self.scale_y))
        base_digit_size = max(32, int(48 * self.scale_y))
        base_timer_size = max(40, int(80 * self.scale_y))

        self.operator_font = pygame.font.SysFont("Abyssinica SIL", base_operator_size)
        if self.operator_font is None:
            self.operator_font = pygame.font.SysFont(None, base_operator_size)
        self.result_value_font = pygame.font.SysFont("Abyssinica SIL", max(48, int(89 * self.scale_y)))
        if self.result_value_font is None:
            self.result_value_font = pygame.font.SysFont(None, max(48, int(89 * self.scale_y)))
        self.digit_font = pygame.font.SysFont("Abyssinica SIL", base_digit_size)
        if self.digit_font is None:
            self.digit_font = pygame.font.SysFont(None, base_digit_size)
        self.timer_font = pygame.font.SysFont("Abyssinica SIL", base_timer_size)
        if self.timer_font is None:
            self.timer_font = pygame.font.SysFont(None, base_timer_size)

        self.submit_font = pygame.font.SysFont("Inknut Antiqua", max(18, int(24 * self.scale_y)))
        if self.submit_font is None:
            self.submit_font = pygame.font.SysFont(None, max(18, int(24 * self.scale_y)))

        # Pre-render text lines for intro and results.
        # Pre-render text lines for intro and results.
        self.intro_lines: List[List[str]] = [
            self._prepare_lines(text, self.dialog_font, self.dialog_rect.width)
            for text in self.intro_texts
        ]
        self.result_lines_success = self._prepare_lines(
            self.success_text, self.dialog_font, self.dialog_rect.width
        )
        self.result_lines_failure = self._prepare_lines(
            self.failure_text, self.dialog_font, self.dialog_rect.width
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _scaled_rect(self, x: float, y: float, w: float, h: float) -> pygame.Rect:
        return pygame.Rect(
            int(x * self.scale_x),
            int(y * self.scale_y),
            int(w * self.scale_x),
            int(h * self.scale_y),
        )

    def _load_scaled_image(self, relative_path: str) -> Optional[pygame.Surface]:
        if not os.path.exists(relative_path):
            return None
        try:
            image = pygame.image.load(relative_path)
            return pygame.transform.scale(image, (self.screen_width, self.screen_height))
        except Exception as exc:  # pragma: no cover - IO errors
            print(f"Warning: failed to load {relative_path}: {exc}")
            return None

    def _prepare_lines(
        self, text: str, font: pygame.font.Font, max_width: int
    ) -> List[str]:
        cleaned = text.replace("/br", "\n").replace("\u2028", "\n").replace("\u2029", "\n")
        parts = cleaned.split("\n")
        lines: List[str] = []
        for part in parts:
            words = part.split()
            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if font.size(candidate)[0] <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, str]]:
        if self.finished and self.pending_result is None:
            return None

        if event.type == pygame.QUIT:
            self.finished = True
            self.pending_result = {"result": "quit"}
            return self.pending_result

        if event.type == self.RESULT_EVENT and self.pending_result is not None:
            pygame.time.set_timer(self.RESULT_EVENT, 0)
            result = self.pending_result
            self.pending_result = None
            self.finished = True
            return result

        if self.state in (self.STATE_RESULT_SUCCESS, self.STATE_RESULT_FAILURE):
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                if self.pending_result is not None:
                    pygame.time.set_timer(self.RESULT_EVENT, 0)
                    result = self.pending_result
                    self.pending_result = None
                    self.finished = True
                    return result
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self.STATE_SKIPPED
            self.finished = True
            return {"result": "skipped"}

        if self.state in (self.STATE_INTRO_1, self.STATE_INTRO_2):
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
                    return None
                if event.type == pygame.KEYDOWN and event.key not in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                ):
                    return None
                self._advance_intro()
            return None

        if self.state == self.STATE_PUZZLE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.submit_rect.collidepoint(event.pos):
                    self._submit_solution()
                else:
                    clicked_slot = False
                    for index, rect in enumerate(self.slot_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_slot = index
                            clicked_slot = True
                            break
                    if not clicked_slot:
                        for idx, rect in enumerate(self.digit_display_rects):
                            if rect.collidepoint(event.pos):
                                if self.selected_slot is None:
                                    self.selected_slot = 0
                                self._assign_digit(self.selected_slot, self.DIGITS[idx])
                                break
            elif event.type == pygame.KEYDOWN:
                if self.selected_slot is None:
                    return None
                if event.key == pygame.K_BACKSPACE:
                    self.slot_values[self.selected_slot] = None
                    return None
                value = self._key_to_digit(event)
                if value is None:
                    return None
                self._assign_digit(self.selected_slot, value)
            return None

        return None

    def _advance_intro(self) -> None:
        if self.state == self.STATE_INTRO_1:
            self.state = self.STATE_INTRO_2
        elif self.state == self.STATE_INTRO_2:
            self.state = self.STATE_PUZZLE
            self.timer_start = pygame.time.get_ticks()
            self.selected_slot = 0
            self.slot_values = [None, None, None, None]
            self.timer_expired = False

    def _key_to_digit(self, event: pygame.event.Event) -> Optional[int]:
        try:
            char = event.unicode
        except AttributeError:
            return None
        if not char or not char.isdigit():
            return None
        value = int(char)
        if value in self.DIGITS:
            return value
        return None

    def _assign_digit(self, slot_index: int, value: int) -> None:
        # Remove the value from any other slot so it stays unique.
        for idx, existing in enumerate(self.slot_values):
            if idx != slot_index and existing == value:
                self.slot_values[idx] = None
        self.slot_values[slot_index] = value
        for idx, existing in enumerate(self.slot_values):
            if existing is None:
                self.selected_slot = idx
                break
        else:
            self.selected_slot = slot_index

    def _submit_solution(self) -> None:
        if None in self.slot_values:
            return
        a, b, c, d = [int(v) for v in self.slot_values]
        result = ((a / b) * c) * d
        success = abs(result - 24) < 1e-6
        self._trigger_result(success)

    def _trigger_result(self, success: bool) -> None:
        if success:
            self.state = self.STATE_RESULT_SUCCESS
            self.pending_result = {"result": "continue"}
        else:
            self.state = self.STATE_RESULT_FAILURE
            self.pending_result = {"result": "failed"}
        self.timer_start = None
        self.timer_expired = True
        pygame.time.set_timer(self.RESULT_EVENT, self.RESULT_DELAY_MS)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def draw(self) -> None:
        if self.state == self.STATE_SKIPPED:
            self.screen.fill((0, 0, 0))
            return

        if self.state in (self.STATE_INTRO_1, self.STATE_INTRO_2):
            self._draw_background(self.background_intro)
            index = 0 if self.state == self.STATE_INTRO_1 else 1
            self._draw_intro(self.intro_lines[index])
            return

        if self.state == self.STATE_PUZZLE:
            self._draw_puzzle()
            return

        if self.state == self.STATE_RESULT_SUCCESS:
            self._draw_background(self.background_result)
            self._draw_dialog(self.result_lines_success)
            return

        if self.state == self.STATE_RESULT_FAILURE:
            self._draw_background(self.background_result)
            self._draw_dialog(self.result_lines_failure)
            return

    def _draw_background(self, background: Optional[pygame.Surface]) -> None:
        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((255, 255, 255))

    def _draw_intro(self, lines: Sequence[str]) -> None:
        # Use the same dialog font & line height as the outro
        line_height = self.dialog_line_height
        total_height = len(lines) * line_height
        start_y = self.dialog_rect.top + max(0, (self.dialog_rect.height - total_height) // 2)

        for idx, line in enumerate(lines):
            text_surface = self.dialog_font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.dialog_rect.centerx
            text_rect.y = start_y + idx * line_height
            self.screen.blit(text_surface, text_rect)

        # Render the instruction with the SAME FONT as dialog (self.dialog_font)
        # but keep the SAME SIZE you were using before by scaling down to that height.
        instruction_text = "Press SPACE or CLICK to continue"
        base_surface = self.dialog_font.render(instruction_text, True, (255, 255, 255))

        # target height = whatever your old intro_instruction_font would render
        target_h = self.intro_instruction_font.get_linesize()
        if base_surface.get_height() != target_h:
            scale = target_h / base_surface.get_height()
            scaled_w = max(1, int(base_surface.get_width() * scale))
            instruction_surface = pygame.transform.smoothscale(base_surface, (scaled_w, target_h))
        else:
            instruction_surface = base_surface

        instruction_rect = instruction_surface.get_rect()
        instruction_rect.center = (
            self.screen_width // 2,
            self.screen_height - int(50 * self.scale_y),
        )
        self.screen.blit(instruction_surface, instruction_rect)

    def _draw_dialog(self, lines: Sequence[str]) -> None:
        total_height = len(lines) * self.dialog_line_height
        start_y = self.dialog_rect.top + max(0, (self.dialog_rect.height - total_height) // 2)
        for idx, line in enumerate(lines):
            text_surface = self.dialog_font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.dialog_rect.centerx
            text_rect.y = start_y + idx * self.dialog_line_height
            self.screen.blit(text_surface, text_rect)

    def _draw_puzzle(self) -> None:
        self._draw_background(self.background_puzzle)

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((217, 217, 217, int(0.6 * 255)))
        self.screen.blit(overlay, (0, 0))

        panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface,
            (217, 217, 217, 240),
            panel_surface.get_rect(),
            border_radius=15,
        )
        self.screen.blit(panel_surface, self.panel_rect.topleft)

        # Slot backgrounds
        for index, rect in enumerate(self.slot_rects):
            slot_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                slot_surface,
                (136, 103, 50, int(0.55 * 255)),
                slot_surface.get_rect(),
                border_radius=12,
            )
            self.screen.blit(slot_surface, rect.topleft)
            border_color = (0, 0, 0)
            pygame.draw.rect(self.screen, border_color, rect, width=3, border_radius=12)
            if self.selected_slot == index:
                pygame.draw.rect(self.screen, (255, 215, 0), rect, width=4, border_radius=12)

        self._draw_puzzle_notation()
        self._draw_slot_values()
        self._draw_available_digits()
        self._draw_timer()
        self._draw_submit_button()

        if self.state == self.STATE_PUZZLE and self.timer_start is not None and not self.timer_expired:
            elapsed = pygame.time.get_ticks() - self.timer_start
            if elapsed >= self.TIMER_LIMIT_MS:
                self.timer_expired = True
                self._trigger_result(False)

    def _draw_puzzle_notation(self) -> None:
        margin_small = max(int(24 * self.scale_x), 18)
        margin_large = max(int(40 * self.scale_x), 24)
        center_y = self.panel_rect.centery

        def avg(a: int, b: int) -> int:
            return (a + b) // 2

        elements: List[Tuple[str, int]] = [
            ("(", self.slot_rects[0].left - margin_large),
            ("(", self.slot_rects[1].left - margin_small),
            ("÷", avg(self.slot_rects[0].centerx, self.slot_rects[1].centerx)),
            (")", self.slot_rects[1].right + margin_small),
            ("×", avg(self.slot_rects[1].right, self.slot_rects[2].left)),
            (")", self.slot_rects[2].right + margin_small),
            ("×", avg(self.slot_rects[2].right, self.slot_rects[3].left)),
            ("=", self.slot_rects[3].right + margin_large),
            ("24", self.slot_rects[3].right + margin_large + max(int(60 * self.scale_x), 40)),
        ]

        for symbol, pos_x in elements:
            if symbol == "24":
                surface = self.result_value_font.render(symbol, True, (0, 0, 0))
            else:
                surface = self.operator_font.render(symbol, True, (0, 0, 0))
            rect = surface.get_rect()
            rect.center = (pos_x, center_y)
            self.screen.blit(surface, rect)

    def _draw_slot_values(self) -> None:
        for value, rect in zip(self.slot_values, self.slot_rects):
            if value is None:
                continue
            text_surface = self.digit_font.render(str(value), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    def _draw_available_digits(self) -> None:
        base_y = (self.panel_rect.bottom + self.submit_rect.top) // 2
        spacing = max(int(110 * self.scale_x), 80)
        total_width = spacing * (len(self.DIGITS) - 1)
        start_x = int(self.screen_width // 2 - total_width / 2)
        used_digits = {value for value in self.slot_values if value is not None}
        self.digit_display_rects = []
        for index, digit in enumerate(self.DIGITS):
            x = start_x + index * spacing
            color = (0, 0, 0) if digit not in used_digits else (120, 120, 120)
            label = self.digit_font.render(str(digit), True, color)
            rect = label.get_rect(center=(x, base_y))
            self.screen.blit(label, rect)
            self.digit_display_rects.append(rect)

    def _draw_timer(self) -> None:
        if self.timer_start is None:
            remaining = self.TIMER_LIMIT_MS
        else:
            elapsed = pygame.time.get_ticks() - self.timer_start
            remaining = max(0, self.TIMER_LIMIT_MS - elapsed)
        seconds = max(0, remaining // 1000)
        timer_text = f"{seconds:02d}"
        surface = self.timer_font.render(timer_text, True, (81, 62, 62))
        rect = surface.get_rect(center=self.timer_center)
        self.screen.blit(surface, rect)

    def _draw_submit_button(self) -> None:
        pygame.draw.rect(self.screen, (176, 160, 134), self.submit_rect, border_radius=15)
        pygame.draw.rect(self.screen, (109, 109, 109), self.submit_rect, width=3, border_radius=15)
        inner_surface = pygame.Surface(
            (self.submit_inner_rect.width, self.submit_inner_rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            inner_surface,
            (205, 188, 160, 255),
            inner_surface.get_rect(),
            border_radius=12,
        )
        self.screen.blit(inner_surface, self.submit_inner_rect.topleft)

        label = self.submit_font.render("SUBMIT", True, (0, 0, 0))
        label_rect = label.get_rect(center=self.submit_rect.center)
        self.screen.blit(label, label_rect)


__all__ = ["MathEvent"]
