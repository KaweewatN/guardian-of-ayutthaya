"""Math event mini-game implementation."""

import importlib
import importlib.util
import os
import sys
from typing import List, Optional, Dict, Any, Callable


def _ensure_std_math_module() -> None:
    """Restore the stdlib ``math`` module when this file shadows it."""

    existing = sys.modules.get("math")
    if existing is not None and getattr(existing, "__file__", None) != __file__:
        return

    script_dir = os.path.abspath(os.path.dirname(__file__))
    removed_entry: Optional[str] = None
    if sys.path and os.path.abspath(sys.path[0]) == script_dir:
        removed_entry = sys.path.pop(0)

    previous = sys.modules.pop("math", None)
    try:
        std_math = importlib.import_module("math")
    finally:
        if removed_entry is not None:
            sys.path.insert(0, removed_entry)

    if getattr(std_math, "__file__", None) == __file__:
        if previous is not None:
            sys.modules["math"] = previous
        return

    sys.modules["math"] = std_math


_ensure_std_math_module()

import pygame

# Font import strategy similar to other events
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
    except Exception as exc:  # pragma: no cover - fallback safety
        print(f"Warning: fonts import failed ({exc}). Using pygame fallback fonts.")
        fallback_font = pygame.font.SysFont(None, 28)
        BUTTON_FONT = fallback_font  # type: ignore
        BUTTON_FONT_LARGE = fallback_font  # type: ignore
        TEXT_FONT = fallback_font  # type: ignore
        TEXT_FONT_BOLD = fallback_font  # type: ignore
        SUBTITLE_FONT = fallback_font  # type: ignore


class MathEvent:
    """Math puzzle event for the Ayutthaya project (buttons 3 and 11 implementation)."""

    STATE_INTRO = "intro"
    STATE_PUZZLE = "puzzle"
    STATE_RESULT = "result"

    RESULT_WIN = "win"
    RESULT_LOSE = "lose"

    def __init__(self, screen: pygame.Surface, block_number: int) -> None:
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 832
        self.block_number = block_number

        # Fonts mimic the Rock/Paper/Scissors setup for visual consistency
        self.title_font = BUTTON_FONT_LARGE
        self.button_font = BUTTON_FONT
        self.text_font = TEXT_FONT
        self.subtitle_font = SUBTITLE_FONT
        self.small_font = TEXT_FONT

        # Fonts dedicated to the puzzle layout
        self.operator_font = pygame.font.SysFont("Abyssinica SIL", 64)
        self.target_font = pygame.font.SysFont("Abyssinica SIL", 80)
        self.number_font = pygame.font.SysFont("Abyssinica SIL", 64)
        self.timer_font = pygame.font.SysFont("Abyssinica SIL", 78)

        # Colors used in the puzzle overlay
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (136, 103, 50)
        self.BROWN_DIM = (176, 160, 134)

        # State management
        self.state = self.STATE_INTRO
        self.puzzle_result: Optional[str] = None
        self._result_reported = False

        # Assets
        self.intro_bg = self._load_and_scale(
            f"assets/scene/event/math/intro/{self.block_number}.png"
        )
        # Puzzle background can vary per block; fall back to button 3 asset if missing
        self.puzzle_bg = self._load_puzzle_background()
        self.padding_y = int(self.screen_height * 0.05)
        self.submit_rect = pygame.Rect(0, 0, 243, 60)
        self.submit_rect.centerx = self.screen_width // 2
        self.submit_rect.bottom  = self.screen_height - self.padding_y
        self.submit_button_img = self._load_button_image(
            "assets/scene/event/math/component/submit.png"
        )
        self.win_bg = self._load_and_scale(
            f"assets/scene/event/math/win/{self.block_number}.png"
        )
        self.lose_bg = self._load_and_scale(
            f"assets/scene/event/math/lose/{self.block_number}.png"
        )

        # --- Layout metrics (centralized for consistency) ---
        self.slot_size = (96, 96)
        self.tile_size = (88, 88)
        self.slot_spacing = 160
        self.tile_spacing = 150

        # Puzzle configuration (varies by block/button)
        self.slot_count = 4
        self.number_choices: List[int] = []
        self.allow_tile_reuse = False
        self.solution_checker: Callable[[List[int]], bool] = self._check_solution_default
        self._configure_puzzle_settings()

        # Equal top/bottom padding for timer and submit button
        self.padding_y = int(self.screen_height * 0.05)  # top gap == bottom gap

        # Rows
        self.slot_row_y = int(self.screen_height * 0.44)
        self.tile_row_y = int(self.screen_height * 0.70)  # moved up slightly

        # Equation background (mid section) styling
        self.equation_bg_padding_x = 200   # wider than before
        self.equation_bg_height   = 140
        self.equation_bg_radius   = 24
        self.equation_bg_color    = (217, 217, 217)
        self.equation_bg_border_w = 3
        self.equation_bg_border_c = self.BROWN

        # Expression slots and selectable numbers
        self.slots = self._create_slots(self.slot_count)
        self.number_tiles = self._create_number_tiles(self.number_choices)

        # Countdown tracking
        self.countdown_total_ms = 20000
        self.countdown_start_ticks: Optional[int] = None

        # Instruction text surface reused for intro/result screens
        self._instruction_cache: Optional[pygame.Surface] = None

    # ------------------------------------------------------------------
    # Asset helpers
    # ------------------------------------------------------------------
    def _load_and_scale(self, path: str) -> Optional[pygame.Surface]:
        if not os.path.exists(path):
            print(f"Warning: missing asset {path}")
            return None
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (self.screen_width, self.screen_height))

    def _load_button_image(self, path: str) -> Optional[pygame.Surface]:
        if not os.path.exists(path):
            print(f"Warning: missing submit button asset {path}")
            return None
        image = pygame.image.load(path)
        return pygame.transform.scale(image, self.submit_rect.size)

    def _load_puzzle_background(self) -> Optional[pygame.Surface]:
        """Load the puzzle background for the current block with a safe fallback."""

        candidate_paths = [
            f"assets/scene/empty/{self.block_number}.png",
            "assets/scene/empty/3.png",
        ]

        for path in candidate_paths:
            if not os.path.exists(path):
                continue
            background = self._load_and_scale(path)
            if background is not None:
                return background

        print(
            f"Warning: missing puzzle background for math event block {self.block_number}"
        )
        return None

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------
    def _calculate_centers(self, count: int, spacing: int, y: int) -> List[pygame.math.Vector2]:
        if count <= 0:
            return []
        half_span = spacing * (count - 1) / 2
        center_x = self.screen_width / 2
        return [
            pygame.math.Vector2(center_x - half_span + index * spacing, y)
            for index in range(count)
        ]

    def _create_slots(self, count: int) -> List[Dict[str, Any]]:
        centers = self._calculate_centers(count, self.slot_spacing, self.slot_row_y)
        slots: List[Dict[str, Any]] = []
        for center in centers:
            rect = pygame.Rect(0, 0, *self.slot_size)
            rect.center = (int(center.x), int(center.y))
            slots.append({"rect": rect, "value": None, "tile": None})
        return slots

    def _create_number_tiles(self, numbers: List[int]) -> List[Dict[str, Any]]:
        centers = self._calculate_centers(len(numbers), self.tile_spacing, self.tile_row_y)
        tiles: List[Dict[str, Any]] = []
        for center, number in zip(centers, numbers):
            rect = pygame.Rect(0, 0, *self.tile_size)
            rect.center = (int(center.x), int(center.y))
            tiles.append({"rect": rect, "value": number, "selected": False})
        return tiles

    def _scaled_rect(self, rect: pygame.Rect, scale: float) -> pygame.Rect:
        new_width = int(rect.width * scale)
        new_height = int(rect.height * scale)
        scaled = pygame.Rect(0, 0, new_width, new_height)
        scaled.center = rect.center
        return scaled

    def _recalculate_layout(self) -> None:
        slot_centers = self._calculate_centers(len(self.slots), self.slot_spacing, self.slot_row_y)
        for slot, center in zip(self.slots, slot_centers):
            rect = pygame.Rect(0, 0, *self.slot_size)
            rect.center = (int(center.x), int(center.y))
            slot["rect"] = rect

        tile_centers = self._calculate_centers(len(self.number_tiles), self.tile_spacing, self.tile_row_y)
        for tile, center in zip(self.number_tiles, tile_centers):
            rect = pygame.Rect(0, 0, *self.tile_size)
            rect.center = (int(center.x), int(center.y))
            tile["rect"] = rect

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _get_instruction_surface(self) -> pygame.Surface:
        if self._instruction_cache is None:
            self._instruction_cache = self.small_font.render(
                "Press SPACE or CLICK to continue", True, self.WHITE
            )
        return self._instruction_cache

    def draw_intro_screen(self, background: Optional[pygame.Surface]) -> None:
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(self.BLACK)
        instruction = self._get_instruction_surface()
        rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        self.screen.blit(instruction, rect)

    def draw_puzzle(self) -> None:
        if self.puzzle_bg:
            self.screen.blit(self.puzzle_bg, (0, 0))
        else:
            self.screen.fill(self.WHITE)

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((217, 217, 217, 80))
        self.screen.blit(overlay, (0, 0))

        self._draw_countdown()

        slot_rects = [slot["rect"] for slot in self.slots]
        if slot_rects:
            # --- Equation background (perfect fit with padding, rounded, wider) ---
            horizontal_span = slot_rects[-1].right - slot_rects[0].left
            eq_left   = slot_rects[0].left - self.equation_bg_padding_x
            eq_width  = horizontal_span + (self.equation_bg_padding_x * 2)
            eq_top    = slot_rects[0].centery - (self.equation_bg_height // 2)
            equation_rect = pygame.Rect(eq_left, eq_top, eq_width, self.equation_bg_height)
            pygame.draw.rect(self.screen, self.equation_bg_color, equation_rect, border_radius=self.equation_bg_radius)
            pygame.draw.rect(self.screen, self.equation_bg_border_c, equation_rect, width=self.equation_bg_border_w, border_radius=self.equation_bg_radius)

            equation_color = self.BLACK

        # --- Cleaner mid section: consistent Y, tidy helpers ---
        mid_y = slot_rects[0].centery
        text_positions = self._get_expression_text_positions(slot_rects)
        for element in text_positions:
            text_surface = self.operator_font.render(element["text"], True, equation_color)
            rect = text_surface.get_rect()
            rect.center = element["pos"]
            self.screen.blit(text_surface, rect)

        # Draw slots
        for slot in self.slots:
            rect: pygame.Rect = slot["rect"]
            pygame.draw.rect(self.screen, self.BROWN, rect, width=4)
            tile_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            tile_surface.fill((136, 103, 50, 120))
            self.screen.blit(tile_surface, rect.topleft)
            if slot["value"] is not None:
                value_surface = self.number_font.render(str(slot["value"]), True, self.BLACK)
                value_rect = value_surface.get_rect(center=rect.center)
                self.screen.blit(value_surface, value_rect)

        # Draw number tiles to choose from
        mouse_pos = pygame.mouse.get_pos()
        for tile in self.number_tiles:
            base_rect = tile["rect"]
            hover = base_rect.collidepoint(mouse_pos)
            draw_rect = self._scaled_rect(base_rect, 1.08) if hover else base_rect
            color = (136, 103, 50)
            if not self.allow_tile_reuse and tile["selected"]:
                color = self.BROWN_DIM
                color = tuple(min(255, c + 25) for c in color)
            pygame.draw.rect(self.screen, color, draw_rect, border_radius=14)
            pygame.draw.rect(self.screen, self.BLACK, draw_rect, width=3, border_radius=14)
            value_surface = self.number_font.render(str(tile["value"]), True, self.BLACK)
            value_rect = value_surface.get_rect(center=draw_rect.center)
            self.screen.blit(value_surface, value_rect)

        # Draw submit button
        submit_hover = self.submit_rect.collidepoint(mouse_pos)
        submit_draw_rect = self._scaled_rect(self.submit_rect, 1.08) if submit_hover else self.submit_rect
        if self.submit_button_img:
            button_surface = self.submit_button_img
            if submit_hover:
                button_surface = pygame.transform.smoothscale(
                    self.submit_button_img, submit_draw_rect.size
                )
            self.screen.blit(button_surface, submit_draw_rect)
        else:
            base_color = tuple(min(255, c + 25) for c in self.BROWN_DIM) if submit_hover else self.BROWN_DIM
            pygame.draw.rect(self.screen, base_color, submit_draw_rect, border_radius=18)
            pygame.draw.rect(self.screen, self.BLACK, submit_draw_rect, width=3, border_radius=18)
            submit_text = self.button_font.render("SUBMIT", True, self.BLACK)
            submit_rect = submit_text.get_rect(center=submit_draw_rect.center)
            self.screen.blit(submit_text, submit_rect)

    def draw_result(self) -> None:
        background = self.win_bg if self.puzzle_result == self.RESULT_WIN else self.lose_bg
        if background:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill(self.BLACK if self.puzzle_result == self.RESULT_WIN else self.WHITE)

        instruction = self._get_instruction_surface()
        rect = instruction.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        self.screen.blit(instruction, rect)

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------
    def draw(self) -> None:
        if self.state == self.STATE_INTRO:
            self.draw_intro_screen(self.intro_bg)
        elif self.state == self.STATE_PUZZLE:
            self._update_countdown()
            self.draw_puzzle()
        elif self.state == self.STATE_RESULT:
            self.draw_result()

    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_INTRO:
                    self._enter_puzzle()
                elif self.state == self.STATE_RESULT:
                    return self._finalize_result()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == self.STATE_INTRO:
                self._enter_puzzle()
            elif self.state == self.STATE_PUZZLE:
                self._handle_puzzle_click(event.pos)
            elif self.state == self.STATE_RESULT:
                return self._finalize_result()

        return None

    # ------------------------------------------------------------------
    # Puzzle handling
    # ------------------------------------------------------------------
    def _handle_puzzle_click(self, pos) -> None:
        # Click on submit button
        if self.submit_rect.collidepoint(pos):
            if all(slot["value"] is not None for slot in self.slots):
                self._evaluate_puzzle()
            return

        # Check for clicks on slots to clear them
        for slot in self.slots:
            rect: pygame.Rect = slot["rect"]
            if rect.collidepoint(pos) and slot["value"] is not None:
                tile = slot["tile"]
                if tile and not self.allow_tile_reuse:
                    tile["selected"] = False
                slot["value"] = None
                slot["tile"] = None
                return

        # Otherwise check number tiles to select
        for tile in self.number_tiles:
            if not tile["rect"].collidepoint(pos):
                continue
            if not self.allow_tile_reuse and tile["selected"]:
                continue
            for slot in self.slots:
                if slot["value"] is None:
                    slot["value"] = tile["value"]
                    slot["tile"] = None
                    if not self.allow_tile_reuse:
                        slot["tile"] = tile
                        tile["selected"] = True
                    return

    def _get_expression_text_positions(self, slot_rects: List[pygame.Rect]) -> List[Dict[str, Any]]:
        if not slot_rects:
            return []

        mid_y = slot_rects[0].centery

        def mid_x(a: pygame.Rect, b: pygame.Rect) -> int:
            return (a.centerx + b.centerx) // 2

        if self.block_number == 11:
            return [
                {"text": "+", "pos": (mid_x(slot_rects[0], slot_rects[1]), mid_y)},
                {"text": "-", "pos": (mid_x(slot_rects[1], slot_rects[2]), mid_y)},
                {"text": "+", "pos": (mid_x(slot_rects[2], slot_rects[3]), mid_y)},
                {"text": "+", "pos": (mid_x(slot_rects[3], slot_rects[4]), mid_y)},
                {"text": "= 24", "pos": (slot_rects[-1].right + 90, mid_y)},
            ]
        if self.block_number == 20:
            return [
                {"text": "×", "pos": (mid_x(slot_rects[0], slot_rects[1]), mid_y)},
                {"text": "− (", "pos": (mid_x(slot_rects[1], slot_rects[2]), mid_y)},
                {"text": "+", "pos": (mid_x(slot_rects[2], slot_rects[3]), mid_y)},
                {"text": ")", "pos": (slot_rects[3].right + 45, mid_y)},
                {"text": "= 24", "pos": (slot_rects[3].right + 135, mid_y)},
            ]

        return [
            {"text": "(", "pos": (slot_rects[0].left - 95, mid_y)},
            {"text": "(", "pos": (slot_rects[0].left - 55, mid_y)},
            {"text": "÷", "pos": (mid_x(slot_rects[0], slot_rects[1]), mid_y)},
            {"text": ")", "pos": (slot_rects[1].right + 55, mid_y)},
            {"text": "×", "pos": (mid_x(slot_rects[1], slot_rects[2]), mid_y)},
            {"text": ")", "pos": (slot_rects[2].right + 55, mid_y)},
            {"text": "×", "pos": (mid_x(slot_rects[2], slot_rects[3]), mid_y)},
            {"text": "= 24", "pos": (slot_rects[3].right + 125, mid_y)},
        ]

    def _evaluate_puzzle(self) -> None:
        values = [slot["value"] for slot in self.slots]
        if None in values:
            return
        int_values = [int(v) for v in values]  # type: ignore
        success = self.solution_checker(int_values)
        self.puzzle_result = self.RESULT_WIN if success else self.RESULT_LOSE
        self.state = self.STATE_RESULT
        self._result_reported = False
        self._stop_countdown()
    def _configure_puzzle_settings(self) -> None:
        if self.block_number == 11:
            self.slot_count = 5
            self.slot_spacing = 135
            self.number_choices = list(range(0, 11))
            self.allow_tile_reuse = True
            self.tile_spacing = 110
            self.solution_checker = self._check_solution_block11
            return
        if self.block_number == 20:
            self.slot_count = 4
            self.slot_spacing = 160
            self.number_choices = [1, 5, 5, 6]
            self.allow_tile_reuse = False
            self.tile_spacing = 150
            self.solution_checker = self._check_solution_block20
            return

        self.slot_count = 4
        self.slot_spacing = 160
        self.number_choices = [2, 3, 4, 9]
        self.allow_tile_reuse = False
        self.tile_spacing = 150
        self.solution_checker = self._check_solution_default

    def _check_solution_default(self, values: List[int]) -> bool:
        if len(values) != 4:
            return False
        n1, n2, n3, n4 = values
        try:
            return ((n1 / n2) * n3) * n4 == 24
        except ZeroDivisionError:
            return False

    def _check_solution_block11(self, values: List[int]) -> bool:
        if len(values) != 5:
            return False
        n1, n2, n3, n4, n5 = values
        return n1 + n2 - n3 + n4 + n5 == 24
    def _check_solution_block20(self, values: List[int]) -> bool:
        if len(values) != 4:
            return False
        n1, n2, n3, n4 = values
        return (n1 * n2) - (n3 + n4) == 24

    def _finalize_result(self) -> Optional[Dict[str, Any]]:
        if self.state != self.STATE_RESULT or self._result_reported:
            return None
        self._result_reported = True
        result_value = self.puzzle_result or self.RESULT_LOSE
        return {
            "result": result_value,
            "success": result_value == self.RESULT_WIN,
            "block": self.block_number,
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self.state = self.STATE_INTRO
        self.puzzle_result = None
        self._result_reported = False
        for slot in self.slots:
            slot["value"] = None
            slot["tile"] = None
        for tile in self.number_tiles:
            tile["selected"] = False
        self._stop_countdown()

    def update_screen_size(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.padding_y = int(self.screen_height * 0.05)
        self.slot_row_y = int(self.screen_height * 0.44)
        self.tile_row_y = int(self.screen_height * 0.70)
        self.submit_rect.centerx = self.screen_width // 2
        self.submit_rect.bottom  = self.screen_height - self.padding_y
        self._recalculate_layout()
        # Rescaling assets is skipped for now to keep implementation focused on gameplay logic.

    # ------------------------------------------------------------------
    # Countdown helpers
    # ------------------------------------------------------------------
    def _enter_puzzle(self) -> None:
        self.state = self.STATE_PUZZLE
        self._start_countdown()

    def _start_countdown(self) -> None:
        self.countdown_start_ticks = pygame.time.get_ticks()

    def _stop_countdown(self) -> None:
        self.countdown_start_ticks = None

    def _get_countdown_ms(self) -> int:
        if self.countdown_start_ticks is None:
            return self.countdown_total_ms
        elapsed = pygame.time.get_ticks() - self.countdown_start_ticks
        return max(0, self.countdown_total_ms - elapsed)

    def _update_countdown(self) -> None:
        if self.state != self.STATE_PUZZLE:
            return
        if self.countdown_start_ticks is None:
            self._start_countdown()
        if self._get_countdown_ms() <= 0:
            self._handle_timeout()

    def _handle_timeout(self) -> None:
        if self.state != self.STATE_PUZZLE:
            return
        self.puzzle_result = self.RESULT_LOSE
        self.state = self.STATE_RESULT
        self._result_reported = False
        self._stop_countdown()

    def _draw_countdown(self) -> None:
        remaining_ms = self._get_countdown_ms()
        seconds_left = max(0, (remaining_ms + 999) // 1000)
        timer_rect = pygame.Rect(0, 0, 190, 100)
        timer_rect.centerx = self.screen_width // 2
        timer_rect.top = self.padding_y
        pygame.draw.rect(self.screen, (245, 237, 223), timer_rect, border_radius=28)
        pygame.draw.rect(self.screen, self.BROWN, timer_rect, width=4, border_radius=28)

        timer_surface = self.timer_font.render(str(seconds_left), True, self.BROWN)
        timer_text_rect = timer_surface.get_rect(center=timer_rect.center)
        self.screen.blit(timer_surface, timer_text_rect)
