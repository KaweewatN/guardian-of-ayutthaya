"""Final outcome screen shown when the player reaches the end of the board."""

from __future__ import annotations

import os
import random
from typing import Optional

import pygame

_CONSTANT_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'constant'))
if _CONSTANT_BASE not in os.sys.path:
    os.sys.path.insert(0, _CONSTANT_BASE)

try:  # pragma: no cover - runtime dependency
    from fonts import TITLE_FONT, TEXT_FONT
except Exception:  # pragma: no cover - fallback when fonts unavailable
    TITLE_FONT = pygame.font.SysFont('Arial', 68, bold=True)
    TEXT_FONT = pygame.font.SysFont('Arial', 28)


class GameOutcomeScreen:
    """Modal overlay summarising the game's final outcome."""

    def __init__(self, screen: pygame.Surface, outcome: str) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.outcome = outcome

        self.background = self._load_background(outcome)
        self.title_font = TITLE_FONT
        self.text_font = TEXT_FONT

        if outcome == 'win':
            title = "Victory!"
            message = "You gathered AYUTTHAYA and protected the kingdom."
        else:
            title = "Defeat"
            message = "You reached the capital without the sacred letters."

        self.title_surface = self.title_font.render(title, True, (255, 240, 200))
        self.message_surface = self.text_font.render(message, True, (255, 255, 255))
        self.prompt_surface = self.text_font.render("Press SPACE to return to the board", True, (255, 218, 150))

        self._result_reported = False

    def _assets_path(self, *parts: str) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        return os.path.join(base, 'assets', *parts)

    def _load_background(self, outcome: str) -> Optional[pygame.Surface]:
        folder = 'win' if outcome == 'win' else 'lose'
        directory = self._assets_path(folder)
        if not os.path.isdir(directory):
            print(f"Warning: outcome directory not found: {directory}")
            return None

        candidates = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.lower().endswith('.png')
        ]

        if not candidates:
            print(f"Warning: no outcome images in {directory}")
            return None

        chosen_path = random.choice(candidates)
        try:
            img = pygame.image.load(chosen_path).convert_alpha()
            return pygame.transform.scale(img, (self.screen_rect.width, self.screen_rect.height))
        except Exception as exc:  # pragma: no cover
            print(f"Warning: unable to load outcome image {chosen_path}: {exc}")
        return None

    def update(self) -> None:
        """Static screen - nothing to update."""

    def draw(self) -> None:
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            base_color = (60, 45, 30) if self.outcome == 'win' else (40, 20, 20)
            self.screen.fill(base_color)

        title_rect = self.title_surface.get_rect(center=(self.screen_rect.centerx, 180))
        message_rect = self.message_surface.get_rect(center=(self.screen_rect.centerx, 270))
        prompt_rect = self.prompt_surface.get_rect(center=(self.screen_rect.centerx, self.screen_rect.height - 120))

        self.screen.blit(self.title_surface, title_rect)
        self.screen.blit(self.message_surface, message_rect)
        self.screen.blit(self.prompt_surface, prompt_rect)

    def handle_event(self, event: pygame.event.Event) -> Optional[dict]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return self._finalize()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._finalize()
        return None

    def _finalize(self) -> Optional[dict]:
        if self._result_reported:
            return None
        self._result_reported = True
        return {
            'result': 'game-finished',
            'outcome': self.outcome,
        }
