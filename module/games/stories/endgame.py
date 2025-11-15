"""Endgame cinematics with sequential story-style transitions and final choice popup."""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Tuple

import pygame

# Fonts live in constant/fonts.py relative to repository root
_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in sys.path:
    sys.path.insert(0, _CONSTANT_BASE)

from fonts import TEXT_FONT_BOLD, BUTTON_FONT_SMALL, HINT_FONT


class EndGameSequence:
    """Play a short cinematic sequence before presenting restart/quit choices."""

    POPUP_FADE_DURATION = 600  # milliseconds
    FRAME_FADE_DURATION = 600
    FRAME_HOLD_DURATION = 1800

    def __init__(self, screen: pygame.Surface, outcome: str,
                 colors: Optional[Dict[str, Tuple[int, int, int]]] = None) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.outcome = outcome if outcome in {"win", "lose"} else "lose"

        self.colors = colors or {}
        self.BLACK = self.colors.get('BLACK', (0, 0, 0))
        self.WHITE = self.colors.get('WHITE', (255, 255, 255))

        # Load frames and maintain originals for potential resize
        self._original_frames: List[pygame.Surface] = []
        self.frames: List[pygame.Surface] = []
        self._load_sequence_images()

        self.current_frame_index = 0
        self.frame_stage = 'fade_in'  # fade_in -> hold -> fade_out
        self.stage_start = pygame.time.get_ticks()
        self.current_alpha = 0

        self.state = 'sequence'  # sequence -> popup
        self.final_frame: Optional[pygame.Surface] = None

        # Popup presentation
        self.popup_start_time: Optional[int] = None
        self.popup_alpha = 0
        self.overlay_alpha = 0

        self.popup_width = 400
        self.popup_height = 300
        self.button_width = 180
        self.button_height = 60
        self.button_spacing = 30

        self.title_font = TEXT_FONT_BOLD
        self.button_font = BUTTON_FONT_SMALL
        self.hint_font = HINT_FONT

        self.popup_color = (240, 230, 220)
        self.popup_border_color = (90, 60, 30)
        self.button_color = (139, 90, 43)
        self.button_hover_color = (180, 120, 60)
        self.button_border_color = (90, 60, 30)

        self.popup_rect = pygame.Rect(0, 0, self.popup_width, self.popup_height)
        self.restart_button_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        self.quit_button_rect = pygame.Rect(0, 0, self.button_width, self.button_height)
        self._recompute_layout()

        self.restart_hover = False
        self.quit_hover = False

        self.result_reported = False
        self._last_screen_size = self.screen_rect.size

    # ------------------------------------------------------------------
    # Loading & layout helpers
    # ------------------------------------------------------------------
    def _assets_base(self) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets'))

    def _load_sequence_images(self) -> None:
        """Load and scale the win/lose cinematic frames."""
        prefix = 'win' if self.outcome == 'win' else 'lose'
        max_frames = 5 if self.outcome == 'win' else 3
        base_dir = os.path.join(self._assets_base(), prefix)

        self._original_frames.clear()
        self.frames.clear()

        for index in range(1, max_frames + 1):
            filename = f"{prefix}-{index}.png"
            path = os.path.join(base_dir, filename)
            if not os.path.exists(path):
                continue
            try:
                image = pygame.image.load(path).convert_alpha()
            except Exception as exc:  # pragma: no cover - surface loading failure fallback
                print(f"Warning: unable to load endgame frame {path}: {exc}")
                continue
            self._original_frames.append(image)
            self.frames.append(self._scale_image(image))

        if not self.frames:
            # Create a fallback surface so the sequence still works
            placeholder = pygame.Surface(self.screen_rect.size)
            placeholder.fill((30, 20, 10) if self.outcome == 'win' else (20, 0, 0))
            self._original_frames.append(placeholder)
            self.frames.append(placeholder.copy())

    def _scale_image(self, image: pygame.Surface) -> pygame.Surface:
        img_rect = image.get_rect()
        scale_factor = min(
            self.screen_rect.width / img_rect.width,
            self.screen_rect.height / img_rect.height
        )
        new_width = max(1, int(img_rect.width * scale_factor))
        new_height = max(1, int(img_rect.height * scale_factor))
        return pygame.transform.smoothscale(image, (new_width, new_height))

    def _recompute_layout(self) -> None:
        self.screen_rect = self.screen.get_rect()
        self.popup_rect = pygame.Rect(
            (self.screen_rect.width - self.popup_width) // 2,
            (self.screen_rect.height - self.popup_height) // 2,
            self.popup_width,
            self.popup_height
        )

        center_x = self.popup_rect.centerx
        center_y = self.popup_rect.centery

        self.restart_button_rect = pygame.Rect(
            center_x - self.button_width // 2,
            center_y - self.button_height - self.button_spacing // 2 + 20,
            self.button_width,
            self.button_height
        )
        self.quit_button_rect = pygame.Rect(
            center_x - self.button_width // 2,
            center_y + self.button_spacing // 2 + 20,
            self.button_width,
            self.button_height
        )

    def _rescale_frames_if_needed(self) -> None:
        current_size = self.screen.get_size()
        if current_size == self._last_screen_size:
            return
        self._last_screen_size = current_size
        self.screen_rect = self.screen.get_rect()
        self.frames = [self._scale_image(image) for image in self._original_frames]
        if self.final_frame is not None and self.frames:
            self.final_frame = self.frames[-1]
        self._recompute_layout()

    # ------------------------------------------------------------------
    # Sequence progression
    # ------------------------------------------------------------------
    def _advance_to_next_frame(self) -> None:
        self.current_frame_index += 1
        if self.current_frame_index >= len(self.frames):
            self._begin_popup()
        else:
            self.frame_stage = 'fade_in'
            self.stage_start = pygame.time.get_ticks()
            self.current_alpha = 0

    def _begin_popup(self) -> None:
        self.state = 'popup'
        self.final_frame = self.frames[-1] if self.frames else None
        self.popup_start_time = pygame.time.get_ticks()
        self.popup_alpha = 0
        self.overlay_alpha = 0
        self.restart_hover = False
        self.quit_hover = False

    # ------------------------------------------------------------------
    # Public API expected by BoardBlock
    # ------------------------------------------------------------------
    def update(self) -> None:
        self._rescale_frames_if_needed()

        if self.state == 'sequence':
            if not self.frames:
                self._begin_popup()
                return

            now = pygame.time.get_ticks()
            elapsed = now - self.stage_start

            if self.frame_stage == 'fade_in':
                if self.FRAME_FADE_DURATION <= 0:
                    self.current_alpha = 255
                    self.frame_stage = 'hold'
                    self.stage_start = now
                else:
                    progress = min(1.0, elapsed / self.FRAME_FADE_DURATION)
                    self.current_alpha = int(progress * 255)
                    if progress >= 1.0:
                        self.frame_stage = 'hold'
                        self.stage_start = now
            elif self.frame_stage == 'hold':
                self.current_alpha = 255
                if elapsed >= self.FRAME_HOLD_DURATION:
                    self.frame_stage = 'fade_out'
                    self.stage_start = now
            elif self.frame_stage == 'fade_out':
                if self.FRAME_FADE_DURATION <= 0:
                    self._advance_to_next_frame()
                else:
                    progress = min(1.0, elapsed / self.FRAME_FADE_DURATION)
                    self.current_alpha = int((1.0 - progress) * 255)
                    if progress >= 1.0:
                        self._advance_to_next_frame()

        elif self.state == 'popup' and self.popup_start_time is not None:
            now = pygame.time.get_ticks()
            elapsed = now - self.popup_start_time
            progress = min(1.0, elapsed / self.POPUP_FADE_DURATION)
            self.popup_alpha = int(progress * 255)
            self.overlay_alpha = int(progress * 180)

    def draw(self) -> None:
        if self.state == 'sequence':
            self._draw_current_frame()
        else:
            self._draw_final_frame_with_popup()

    def _draw_current_frame(self) -> None:
        self.screen.fill(self.BLACK)
        if not self.frames:
            return
        frame = self.frames[self.current_frame_index]
        surface = frame.copy()
        if self.current_alpha < 255:
            surface.set_alpha(self.current_alpha)
        rect = surface.get_rect(center=self.screen_rect.center)
        self.screen.blit(surface, rect)

    def _draw_final_frame_with_popup(self) -> None:
        self.screen.fill(self.BLACK)
        base_frame = self.final_frame or (self.frames[-1] if self.frames else None)
        if base_frame:
            rect = base_frame.get_rect(center=self.screen_rect.center)
            self.screen.blit(base_frame, rect)

        if self.overlay_alpha > 0:
            overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.overlay_alpha))
            self.screen.blit(overlay, (0, 0))

        if self.popup_alpha <= 0:
            return

        popup_surface = pygame.Surface((self.popup_rect.width, self.popup_rect.height), pygame.SRCALPHA)
        popup_rect = popup_surface.get_rect()
        pygame.draw.rect(
            popup_surface,
            (*self.popup_color, self.popup_alpha),
            popup_rect,
            border_radius=20,
        )
        pygame.draw.rect(
            popup_surface,
            (*self.popup_border_color, self.popup_alpha),
            popup_rect,
            width=4,
            border_radius=20,
        )
        self.screen.blit(popup_surface, self.popup_rect)

        # Title text
        title_text = self.title_font.render("start the journey again?", True, (60, 40, 20))
        title_text = title_text.copy()
        title_text.set_alpha(self.popup_alpha)
        title_rect = title_text.get_rect(centerx=self.popup_rect.centerx,
                                         top=self.popup_rect.top + 30)
        self.screen.blit(title_text, title_rect)

        self._draw_buttons()

        hint_text = self.hint_font.render("Press ESC or click outside to close", True, (100, 100, 100))
        hint_text = hint_text.copy()
        hint_text.set_alpha(self.popup_alpha)
        hint_rect = hint_text.get_rect(centerx=self.popup_rect.centerx,
                                       bottom=self.popup_rect.bottom - 10)
        self.screen.blit(hint_text, hint_rect)

    def _draw_buttons(self) -> None:
        restart_surface = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
        restart_rect = restart_surface.get_rect()
        restart_bg = self.button_hover_color if self.restart_hover else self.button_color
        pygame.draw.rect(
            restart_surface,
            (*restart_bg, self.popup_alpha),
            restart_rect,
            border_radius=10,
        )
        pygame.draw.rect(
            restart_surface,
            (*self.button_border_color, self.popup_alpha),
            restart_rect,
            width=3,
            border_radius=10,
        )
        self.screen.blit(restart_surface, self.restart_button_rect)

        restart_text = self.button_font.render("Restart", True, (255, 255, 255))
        restart_text = restart_text.copy()
        restart_text.set_alpha(self.popup_alpha)
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        quit_surface = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
        quit_rect = quit_surface.get_rect()
        quit_bg = self.button_hover_color if self.quit_hover else self.button_color
        pygame.draw.rect(
            quit_surface,
            (*quit_bg, self.popup_alpha),
            quit_rect,
            border_radius=10,
        )
        pygame.draw.rect(
            quit_surface,
            (*self.button_border_color, self.popup_alpha),
            quit_rect,
            width=3,
            border_radius=10,
        )
        self.screen.blit(quit_surface, self.quit_button_rect)

        quit_text = self.button_font.render("Quit", True, (255, 255, 255))
        quit_text = quit_text.copy()
        quit_text.set_alpha(self.popup_alpha)
        quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> Optional[dict]:
        if self.state != 'popup' or self.popup_alpha < 200:
            return None

        if event.type == pygame.MOUSEMOTION:
            self.restart_hover = self.restart_button_rect.collidepoint(event.pos)
            self.quit_hover = self.quit_button_rect.collidepoint(event.pos)
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.restart_button_rect.collidepoint(event.pos):
                return self._finalize('restart')
            if self.quit_button_rect.collidepoint(event.pos) or not self.popup_rect.collidepoint(event.pos):
                return self._finalize('quit')
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._finalize('restart')
            if event.key == pygame.K_ESCAPE:
                return self._finalize('quit')
        return None

    def _finalize(self, choice: str) -> Optional[dict]:
        if self.result_reported:
            return None
        self.result_reported = True
        return {
            'result': 'endgame-choice',
            'choice': choice,
            'outcome': self.outcome,
        }
