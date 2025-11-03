"""Math event intro and puzzle prompt screen."""
import os
import sys
import pygame

# Import shared fonts with fallbacks similar to other event modules
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
        from fonts import (
            BUTTON_FONT,
            BUTTON_FONT_LARGE,
            TEXT_FONT,
            TEXT_FONT_BOLD,
            SUBTITLE_FONT,
        )
    except Exception as e:
        print(f"Warning: Fonts import failed ({e}). Using pygame fallback fonts.")
        try:
            pygame_font = pygame.font.SysFont(None, 28)
        except Exception:
            class _DummyFont:
                def render(self, text, aa, color):
                    surf = pygame.Surface((max(200, len(text) * 10), 30))
                    surf.fill((200, 200, 200))
                    return surf

            pygame_font = _DummyFont()

        BUTTON_FONT = pygame_font
        BUTTON_FONT_LARGE = pygame_font
        TEXT_FONT = pygame_font
        TEXT_FONT_BOLD = pygame_font
        SUBTITLE_FONT = pygame_font


def _wrap_text(font, text, max_width):
    """Wrap text to fit within max_width using the provided font."""
    if not text:
        return []

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = word if not current_line else f"{current_line} {word}"
        if font.size(candidate)[0] <= max_width:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


class MathEvent:
    """Introductory math mini-event for block 3."""

    STATE_INTRO = "intro"
    STATE_PUZZLE = "puzzle"
    STATE_SKIPPED = "skipped"
    STATE_COMPLETE = "complete"

    def __init__(self, screen, block_number=3):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.block_number = block_number

        self.state = self.STATE_INTRO
        self.hovered_skip = False
        self.finished = False

        # Text content
        self.description_text = (
            "This is Wat Na Phra Men, the only temple untouched by war. "
            "Once a royal cremation ground, now it shelters a bronze Buddha in "
            "royal robes. A peaceful witness to Ayutthaya's fall and rebirth."
        )
        self.puzzle_text = (
            "Solve this to get the alphabet cards.\n2, 3, 4, 9 \u2192 Can you make 24?"
        )

        # Layout rectangles based on provided specifications
        self.description_rect = pygame.Rect(279, 244, 578, 184)
        self.puzzle_rect = pygame.Rect(279, 224, 565, 172)

        # Skip button configuration
        self.skip_rect = pygame.Rect(self.screen_width - 200 - 48, 48, 200, 64)

        # Fonts
        self.desc_font = TEXT_FONT
        self.puzzle_font = SUBTITLE_FONT
        self.skip_font = BUTTON_FONT
        self.instruction_font = TEXT_FONT_BOLD

        # Load imagery
        self.background = self._load_scaled_image(
            f"assets/scene/event/math/blocks/{self.block_number}.png"
        )
        self.skip_background = self._load_scaled_image(
            f"assets/scene/empty/{self.block_number}.png"
        )

        # Pre-render text lines
        self.description_lines = _wrap_text(self.desc_font, self.description_text, self.description_rect.width)
        self.puzzle_lines = _wrap_text(self.puzzle_font, self.puzzle_text, self.puzzle_rect.width)

    def _load_scaled_image(self, relative_path):
        """Load and scale an image to the current screen size."""
        if not os.path.exists(relative_path):
            return None
        try:
            image = pygame.image.load(relative_path)
            return pygame.transform.scale(image, (self.screen_width, self.screen_height))
        except Exception as exc:
            print(f"Warning: failed to load {relative_path}: {exc}")
            return None

    def handle_event(self, event):
        if self.finished:
            return None

        if event.type == pygame.MOUSEMOTION:
            self.hovered_skip = self.skip_rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.skip_rect.collidepoint(event.pos):
                self.state = self.STATE_SKIPPED
                self.finished = True
                return {"result": "skipped"}

            if self.state == self.STATE_INTRO:
                self.state = self.STATE_PUZZLE
            elif self.state == self.STATE_PUZZLE:
                self.state = self.STATE_COMPLETE
                self.finished = True
                return {"result": "continue"}

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PUZZLE
                elif self.state == self.STATE_PUZZLE:
                    self.state = self.STATE_COMPLETE
                    self.finished = True
                    return {"result": "continue"}
            elif event.key == pygame.K_ESCAPE:
                # Treat ESC as skipping the event
                self.state = self.STATE_SKIPPED
                self.finished = True
                return {"result": "skipped"}

        return None

    def draw(self):
        if self.state == self.STATE_SKIPPED:
            if self.skip_background:
                self.screen.blit(self.skip_background, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            return

        # Draw background image or fallback color
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((255, 255, 255))

        # Draw text blocks depending on the state
        if self.state == self.STATE_INTRO:
            self._draw_text_block(
                self.description_rect,
                self.description_lines,
                self.desc_font,
                line_height=36,
            )
        elif self.state in (self.STATE_PUZZLE, self.STATE_COMPLETE):
            # Draw description as context and puzzle prompt layered above
            self._draw_text_block(
                self.description_rect,
                self.description_lines,
                self.desc_font,
                line_height=36,
                background_alpha=190,
            )
            self._draw_text_block(
                self.puzzle_rect,
                self.puzzle_lines,
                self.puzzle_font,
                line_height=40,
                background_alpha=210,
            )

        # Instruction text at the bottom for intro/puzzle states
        if self.state != self.STATE_COMPLETE:
            instruction = self.instruction_font.render(
                "Press SPACE or CLICK to continue",
                True,
                (0, 0, 0),
            )
            instruction_rect = instruction.get_rect(
                center=(self.screen_width // 2, self.screen_height - 60)
            )
            self.screen.blit(instruction, instruction_rect)

        # Draw skip button (not shown after completion)
        if self.state != self.STATE_COMPLETE:
            self._draw_skip_button()

    def _draw_text_block(
        self,
        rect,
        lines,
        font,
        line_height,
        color=(0, 0, 0),
        background_alpha=220,
    ):
        """Render multiline text inside a semi-transparent panel."""
        if not lines:
            return

        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((255, 255, 255, background_alpha))
        self.screen.blit(panel, rect.topleft)

        total_height = line_height * len(lines)
        start_y = rect.top + max(0, (rect.height - total_height) // 2)

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = rect.centerx
            text_rect.y = start_y + i * line_height
            self.screen.blit(text_surface, text_rect)

    def _draw_skip_button(self):
        base_color = (200, 155, 91)
        hover_color = (220, 175, 111)
        text_color = (75, 42, 12)

        color = hover_color if self.hovered_skip else base_color
        pygame.draw.rect(self.screen, color, self.skip_rect, border_radius=12)
        pygame.draw.rect(self.screen, (168, 107, 39), self.skip_rect, width=2, border_radius=12)

        label = self.skip_font.render("Skip", True, text_color)
        label_rect = label.get_rect(center=self.skip_rect.center)
        self.screen.blit(label, label_rect)


__all__ = ["MathEvent"]