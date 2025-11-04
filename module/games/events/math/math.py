"""Math event mini-game implementation."""
import os
import sys
from typing import List, Optional, Dict, Any

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
    """Math puzzle event for the Ayutthaya project (button 3 implementation)."""

    STATE_INTRO_ONE = "intro_one"
    STATE_INTRO_TWO = "intro_two"
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

        # Colors used in the puzzle overlay
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (136, 103, 50)
        self.BROWN_DIM = (176, 160, 134)

        # State management
        self.state = self.STATE_INTRO_ONE
        self.puzzle_result: Optional[str] = None
        self._result_reported = False

        # Assets
        self.intro_one_bg = self._load_and_scale(
            f"assets/scene/event/math/intro1/{self.block_number}.png"
        )
        self.intro_two_bg = self._load_and_scale(
            f"assets/scene/event/math/intro2/{self.block_number}.png"
        )
        # Puzzle background is a shared asset for the math event
        self.puzzle_bg = self._load_and_scale("assets/scene/empty/3.png")

        self.submit_rect = pygame.Rect(0, 0, 243, 60)
        self.submit_rect.center = (self.screen_width // 2, 675)
        self.submit_button_img = self._load_button_image(
            "assets/scene/event/math/component/submit.png"
        )
        self.win_bg = self._load_and_scale(
            f"assets/scene/event/math/win/{self.block_number}.png"
        )
        self.lose_bg = self._load_and_scale(
            f"assets/scene/event/math/lose/{self.block_number}.png"
        )

        # Expression slots and selectable numbers
        self.slots = self._create_slots()
        self.number_tiles = self._create_number_tiles([2, 3, 4, 9])

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

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------
    def _create_slots(self) -> List[Dict[str, Any]]:
        slot_positions = [
            pygame.Rect(199, 364, 87, 87),
            pygame.Rect(400, 364, 87, 87),
            pygame.Rect(641, 364, 87, 87),
            pygame.Rect(878, 364, 87, 87),
        ]
        return [
            {"rect": rect, "value": None, "tile": None}
            for rect in slot_positions
        ]

    def _create_number_tiles(self, numbers: List[int]) -> List[Dict[str, Any]]:
        tile_size = (87, 87)
        start_x = 320
        spacing = 120
        y = 540
        tiles = []
        for index, number in enumerate(numbers):
            rect = pygame.Rect(0, 0, *tile_size)
            rect.center = (start_x + index * spacing, y)
            tiles.append({"rect": rect, "value": number, "selected": False})
        return tiles

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

        equation_rect = pygame.Rect(61, 340, 1157, 129)
        pygame.draw.rect(self.screen, (217, 217, 217), equation_rect, border_radius=15)

        # Draw static equation symbols
        equation_color = (81, 62, 62)
        target_text = self.target_font.render("49", True, equation_color)
        target_rect = target_text.get_rect(center=(self.screen_width // 2, 110))
        self.screen.blit(target_text, target_rect)

        static_elements = [
            {"text": "(", "pos": (95, 407)},
            {"text": "(", "pos": (145, 407)},
            {"text": ")", "pos": (525, 407)},
            {"text": "÷", "pos": (330, 407)},
            {"text": ")", "pos": (770, 407)},
            {"text": "×", "pos": (590, 407)},
            {"text": "×", "pos": (824, 407)},
            {"text": "= 24", "pos": (1030, 407)},
        ]

        for element in static_elements:
            text_surface = self.operator_font.render(element["text"], True, self.BLACK)
            rect = text_surface.get_rect()
            rect.midleft = element["pos"]
            self.screen.blit(text_surface, rect)

        # Draw slots
        for slot in self.slots:
            rect: pygame.Rect = slot["rect"]
            pygame.draw.rect(self.screen, self.BROWN, rect, width=4, border_radius=8)
            tile_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            tile_surface.fill((136, 103, 50, 120))
            self.screen.blit(tile_surface, rect.topleft)
            if slot["value"] is not None:
                value_surface = self.number_font.render(str(slot["value"]), True, self.BLACK)
                value_rect = value_surface.get_rect(center=rect.center)
                self.screen.blit(value_surface, value_rect)

        # Draw number tiles to choose from
        for tile in self.number_tiles:
            rect = tile["rect"]
            color = self.BROWN_DIM if tile["selected"] else (136, 103, 50)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, rect, width=3, border_radius=10)
            value_surface = self.number_font.render(str(tile["value"]), True, self.BLACK)
            value_rect = value_surface.get_rect(center=rect.center)
            self.screen.blit(value_surface, value_rect)

        # Draw submit button
        if self.submit_button_img:
            self.screen.blit(self.submit_button_img, self.submit_rect)
        else:
            pygame.draw.rect(self.screen, self.BROWN_DIM, self.submit_rect, border_radius=15)
            pygame.draw.rect(self.screen, self.BLACK, self.submit_rect, width=3, border_radius=15)
            submit_text = self.button_font.render("SUBMIT", True, self.BLACK)
            submit_rect = submit_text.get_rect(center=self.submit_rect.center)
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
        if self.state == self.STATE_INTRO_ONE:
            self.draw_intro_screen(self.intro_one_bg)
        elif self.state == self.STATE_INTRO_TWO:
            self.draw_intro_screen(self.intro_two_bg)
        elif self.state == self.STATE_PUZZLE:
            self.draw_puzzle()
        elif self.state == self.STATE_RESULT:
            self.draw_result()

    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_INTRO_ONE:
                    self.state = self.STATE_INTRO_TWO
                elif self.state == self.STATE_INTRO_TWO:
                    self.state = self.STATE_PUZZLE
                elif self.state == self.STATE_RESULT:
                    return self._finalize_result()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == self.STATE_INTRO_ONE:
                self.state = self.STATE_INTRO_TWO
            elif self.state == self.STATE_INTRO_TWO:
                self.state = self.STATE_PUZZLE
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
                if tile:
                    tile["selected"] = False
                slot["value"] = None
                slot["tile"] = None
                return

        # Otherwise check number tiles to select
        for tile in self.number_tiles:
            if tile["rect"].collidepoint(pos) and not tile["selected"]:
                for slot in self.slots:
                    if slot["value"] is None:
                        slot["value"] = tile["value"]
                        slot["tile"] = tile
                        tile["selected"] = True
                        return

    def _evaluate_puzzle(self) -> None:
        values = [slot["value"] for slot in self.slots]
        if None in values:
            return
        n1, n2, n3, n4 = [int(v) for v in values]  # type: ignore
        try:
            result = ((n1 / n2) * n3) * n4
        except ZeroDivisionError:
            result = None
        self.puzzle_result = self.RESULT_WIN if result == 24 else self.RESULT_LOSE
        self.state = self.STATE_RESULT
        self._result_reported = False

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
        self.state = self.STATE_INTRO_ONE
        self.puzzle_result = None
        self._result_reported = False
        for slot in self.slots:
            slot["value"] = None
            slot["tile"] = None
        for tile in self.number_tiles:
            tile["selected"] = False

    def update_screen_size(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.submit_rect.center = (self.screen_width // 2, int(self.screen_height * 0.81))
        # Rescaling assets is skipped for now to keep implementation focused on gameplay logic.
