import pygame
import os
import sys
import json

# Add constant directory to path for font imports
# Import fonts: prefer package-style import (recommended). If that fails,
# fall back to inserting the top-level `constant` directory into sys.path
# (when running tests or importing directly) and import the legacy `fonts`
# module. As a last resort create simple pygame fallback fonts so the
# module can still be imported in headless or test environments.
try:
    # Preferred: when repo is on PYTHONPATH or run as a package
    from constant.fonts import BUTTON_FONT, BUTTON_FONT_LARGE, TEXT_FONT, TEXT_FONT_BOLD, SUBTITLE_FONT
except Exception:
    try:
        # Fallback: add the top-level constant folder relative to repo root.
        const_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'constant'))
        if const_path not in sys.path:
            sys.path.insert(0, const_path)
        from fonts import BUTTON_FONT, BUTTON_FONT_LARGE, TEXT_FONT, TEXT_FONT_BOLD, SUBTITLE_FONT
    except Exception as e:
        # Final fallback: create basic pygame fonts so module import doesn't fail.
        # This keeps tests and importers running even if the project's font module
        # isn't available on PYTHONPATH.
        print(f"Warning: Fonts import failed ({e}). Using pygame fallback fonts.")
        # Ensure pygame.font is available; SysFont works even if fonts not initialized.
        try:
            pygame_font = pygame.font.SysFont(None, 28)
        except Exception:
            # If pygame.font isn't available for some reason, define a dummy object
            class _DummyFont:
                def render(self, text, aa, color):
                    # Return a simple surface placeholder
                    surf = pygame.Surface((max(200, len(text) * 10), 30))
                    surf.fill((200, 200, 200))
                    return surf
            pygame_font = _DummyFont()

        BUTTON_FONT = pygame_font
        BUTTON_FONT_LARGE = pygame_font
        TEXT_FONT = pygame_font
        TEXT_FONT_BOLD = pygame_font
        SUBTITLE_FONT = pygame_font


class GuessGame:
    """Simple quiz/guess mini-game.

    Loads questions from `module/games/events/guess/quiz.json` and presents a
    single question (selected deterministically from `block_number`). The player
    types an answer and submits; the game returns a result dict when complete.
    """

    # States
    STATE_INTRO = "intro"
    STATE_PLAYING = "playing"
    STATE_RESULT = "result"

    def __init__(self, screen, block_number=0):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.block_number = block_number

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BG_COLOR = (245, 235, 220)
        self.INPUT_BG = (255, 255, 255)
        self.INPUT_BORDER = (120, 120, 120)
        self.BUTTON_COLOR = (200, 155, 91)
        self.BUTTON_HOVER = (220, 175, 111)

        # Fonts
        self.title_font = BUTTON_FONT_LARGE
        self.subtitle_font = SUBTITLE_FONT
        self.current_question_font = SUBTITLE_FONT
        self.text_font = TEXT_FONT
        self.small_font = TEXT_FONT
        self.button_font = BUTTON_FONT

        # Game state
        self.state = self.STATE_INTRO
        self.quiz = []
        self.current_question = None
        self.current_answer = None
        self.user_input = ""
        self.result = None  # 'win' or 'lose'
        self.final_result = None

        # UI
        self.input_rect = pygame.Rect(0, 0, min(700, self.screen_width - 200), 60)
        self.input_rect.center = (self.screen_width // 2, self.screen_height // 2 + 80)

        self.submit_rect = pygame.Rect(0, 0, 220, 60)
        self.submit_rect.center = (self.screen_width // 2, self.input_rect.bottom + 60)

        self.hovered = None

        # Load quiz
        self.load_quiz()
        # Load images for this block (bg/result)
        self.load_images()
        self.select_question()

    def load_quiz(self):
        """Load quiz JSON from the event folder bundled with the module."""
        quiz_path = os.path.join(os.path.dirname(__file__), 'quiz.json')
        if os.path.exists(quiz_path):
            try:
                with open(quiz_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Expecting a list of objects like {"question":..., "answer":...}
                    if isinstance(data, list):
                        self.quiz = data
                    else:
                        print(f"Warning: {quiz_path} does not contain a JSON array")
            except Exception as e:
                print(f"Error loading quiz.json: {e}")
        else:
            print(f"Warning: quiz file not found at {quiz_path}")

    def select_question(self):
        """Select a question from the quiz list.

        Uses a deterministic selection based on block_number so every block can
        map to a predictable question.
        """
        if not self.quiz:
            self.current_question = "(No questions available)"
            self.current_answer = ""
            return

        idx = 0
        try:
            idx = int(self.block_number) % len(self.quiz)
        except Exception:
            idx = 0

        qobj = self.quiz[idx]
        self.current_question = qobj.get('question', '')
        self.current_answer = qobj.get('answer', '')

    def load_images(self):
        """Load background and result images for the given block number.

        Note: intro image support has been removed — the game uses the same
        background for intro and playing screens.
        """
        # Path for playing/background image. Use plain `{n}.png` only.
        candidates = [
            f"assets/scene/event/guess/blocks/{self.block_number}.png",
        ]
        self.background = None
        for bg_path in candidates:
            if os.path.exists(bg_path):
                try:
                    img = pygame.image.load(bg_path)
                    self.background = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                    break
                except Exception as e:
                    print(f"Warning: failed to load bg image {bg_path}: {e}")
                    self.background = None
        # If none found, self.background remains None and we fall back to BG_COLOR

        # Result images (win/lose)
        self.result_images = {"win": None, "lose": None}
        for res in ["win", "lose"]:
            res_path = f"assets/scene/event/guess/blocks/{self.block_number}-{res}.png"
            if os.path.exists(res_path):
                try:
                    img = pygame.image.load(res_path)
                    self.result_images[res] = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                except Exception as e:
                    print(f"Warning: failed to load result image {res_path}: {e}")
                    self.result_images[res] = None
            else:
                self.result_images[res] = None

    def draw_intro(self):
        # Background (intro uses the same background image if available)
        if getattr(self, 'background', None):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Layout constants
        max_width = min(800, self.screen_width - 400)
        padding = 18
        container_left = (self.screen_width - max_width) // 2 - padding
        container_top = 180
        container_w = max_width + padding * 2

        # Title
        title = self.title_font.render("Guess the Answer", True, self.BLACK)
        title_rect = title.get_rect()
        title_rect.topleft = (container_left + padding, container_top + padding)

        # Subtitle/instruction
        subtitle = self.small_font.render("Type the answer and press ENTER or click Submit", True, self.BLACK)
        subtitle_rect = subtitle.get_rect()
        subtitle_rect.topleft = (container_left + padding, title_rect.bottom + 10)

        # Question preview (wrapped, but with larger font)
        q_rect = pygame.Rect(container_left + padding, subtitle_rect.bottom + 10, max_width, 120)

        # Container panel height
        container_bottom = q_rect.top + q_rect.height + padding
        container_h = container_bottom - container_top

        # Semi-transparent panel (using SRCALPHA surface) so background shows
        panel_surf = pygame.Surface((container_w, container_h), pygame.SRCALPHA)
        # Optionally fill with a semi-transparent color for effect
        self.screen.blit(panel_surf, (container_left, container_top))

        # Now blit the texts inside the panel, all left-aligned
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        # Use larger font for current_question
        self.draw_wrapped_text(self.current_question, self.subtitle_font, self.BLACK, q_rect)

        # Instruction to continue (centered at bottom)
        instr = self.small_font.render("Press SPACE or CLICK to start", True, self.BLACK)
        instr_rect = instr.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(instr, instr_rect)

    def draw_playing(self):
        # Background
        if getattr(self, 'background', None):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Question text (wrap if needed, use larger font)
        self.draw_wrapped_text(self.current_question, self.title_font, self.BLACK,
                               pygame.Rect(100, 140, self.screen_width - 200, 200))

        # Input box
        pygame.draw.rect(self.screen, self.INPUT_BG, self.input_rect)
        pygame.draw.rect(self.screen, self.INPUT_BORDER, self.input_rect, 2)

        # Render user input
        input_surf = self.text_font.render(self.user_input, True, self.BLACK)
        input_rect = input_surf.get_rect(midleft=(self.input_rect.left + 10, self.input_rect.centery))
        self.screen.blit(input_surf, input_rect)

        # Submit button
        btn_color = self.BUTTON_HOVER if self.hovered == 'submit' else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, btn_color, self.submit_rect)
        pygame.draw.rect(self.screen, self.INPUT_BORDER, self.submit_rect, 2)
        btn_text = self.button_font.render("Submit", True, self.WHITE)
        btn_text_rect = btn_text.get_rect(center=self.submit_rect.center)
        self.screen.blit(btn_text, btn_text_rect)

        # Hint
        hint = self.small_font.render("Answers are not case-sensitive", True, self.BLACK)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.submit_rect.bottom + 30))
        self.screen.blit(hint, hint_rect)

    def draw_result(self):
        # If full-screen result image exists show it, otherwise fallback to text
        img = None
        if hasattr(self, 'result_images'):
            img = self.result_images.get(self.result)

        if img:
            self.screen.blit(img, (0, 0))
        else:
            if getattr(self, 'background', None):
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.BG_COLOR)

            # Result text
            if self.result == 'win':
                text = "Correct!"
            else:
                text = f"Incorrect! Correct answer: {self.current_answer}"

            res_surf = self.title_font.render(text, True, self.BLACK)
            res_rect = res_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(res_surf, res_rect)

        instr = self.small_font.render("Press SPACE or CLICK to continue", True, self.BLACK)
        instr_rect = instr.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(instr, instr_rect)

    def draw_wrapped_text(self, text, font, color, rect, line_spacing=4):
        """Draw multiline wrapped text into rect area."""
        words = text.split(' ')
        lines = []
        cur = ''
        for w in words:
            test = cur + (' ' if cur else '') + w
            if font.size(test)[0] <= rect.width:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        y = rect.top
        for line in lines:
            surf = font.render(line, True, color)
            self.screen.blit(surf, (rect.left, y))
            y += surf.get_height() + line_spacing

    def draw(self):
        if self.state == self.STATE_INTRO:
            self.draw_intro()
        elif self.state == self.STATE_PLAYING:
            self.draw_playing()
        elif self.state == self.STATE_RESULT:
            self.draw_result()

    def handle_event(self, event):
        """Handle pygame events. Returns result dict when finished, else None."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = None
            if self.state == self.STATE_PLAYING:
                if self.submit_rect.collidepoint(event.pos):
                    self.hovered = 'submit'

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    return None
                elif self.state == self.STATE_RESULT:
                    # finalize and return
                    return self._finalize()

            elif self.state == self.STATE_PLAYING:
                # Handle text input
                if event.key == pygame.K_RETURN:
                    # submit
                    self.check_answer()
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                else:
                    # Add character if printable
                    char = event.unicode
                    if char and len(char) == 1:
                        self.user_input += char

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    return None
                elif self.state == self.STATE_PLAYING:
                    if self.submit_rect.collidepoint(event.pos):
                        self.check_answer()
                        return None
                elif self.state == self.STATE_RESULT:
                    return self._finalize()

        return None

    def check_answer(self):
        """Compare the typed answer with the expected answer and set result state."""
        # Normalize answers: lowercase, strip spaces and trailing punctuation
        def normalize(s):
            if s is None:
                return ""
            s = str(s).lower().strip()
            # remove common punctuation
            for ch in ['.', '!', '?', ',', '\'"']:
                s = s.replace(ch, '')
            return s

        user = normalize(self.user_input)
        expected = normalize(self.current_answer)

        if user == expected and user != "":
            self.result = 'win'
        else:
            self.result = 'lose'

        self.state = self.STATE_RESULT

    def _finalize(self):
        """Return the result dict to caller after result screen.

        The caller (game engine) can decide how to reward the player.
        """
        self.final_result = self.result
        return {"result": self.result}

    def update_screen_size(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.input_rect = pygame.Rect(0, 0, min(700, self.screen_width - 200), 60)
        self.input_rect.center = (self.screen_width // 2, self.screen_height // 2 + 80)
        self.submit_rect.center = (self.screen_width // 2, self.input_rect.bottom + 60)
