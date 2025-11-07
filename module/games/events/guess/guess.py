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
        self.screen_width = 1280
        self.screen_height = 832
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
        # Create a custom question font (between TEXT_FONT 24px and SUBTITLE_FONT 48px)
        try:
            # Try to create a 36px version of the same font used for TEXT_FONT
            font_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'assets', 'fonts', 'InknutAntiqua-Regular.ttf')
            if os.path.exists(font_path):
                self.current_question_font = pygame.font.Font(font_path, 30)
            else:
                # Fallback to system font
                self.current_question_font = pygame.font.SysFont('Baskerville', 30, bold=False)
        except Exception:
            # Final fallback: use TEXT_FONT_BOLD as compromise
            self.current_question_font = TEXT_FONT_BOLD
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

        # UI - Optimized for 1280x832
        self.input_rect = pygame.Rect(0, 0, 600, 60)
        self.input_rect.center = (self.screen_width // 2, self.screen_height // 2 + 140)

        self.submit_rect = pygame.Rect(0, 0, 220, 60)
        self.submit_rect.center = (self.screen_width // 2, self.input_rect.bottom + 50)

        self.hovered = None

        # Cursor blinking for text input
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_interval = 500  # milliseconds

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
        # Background
        if getattr(self, 'background', None):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Create white opacity mask
        white_mask = pygame.Surface((self.screen_width, self.screen_height))
        white_mask.fill((255, 255, 255))
        white_mask.set_alpha(204)  # 80% opacity
        self.screen.blit(white_mask, (0, 0))

        # Title at top center
        title = self.title_font.render("Guess the Answer", True, self.BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        # Subtitle/instruction below title
        subtitle = self.text_font.render("Type the answer and press ENTER or click Submit", True, self.BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # Question preview (wrapped, centered area)
        q_rect = pygame.Rect(200, 280, self.screen_width - 400, 200)
        self.draw_wrapped_text(self.current_question, self.current_question_font, self.BLACK, q_rect)

        # Instruction to continue (at bottom like random_event)
        instr = self.text_font.render("Press SPACE or CLICK to start", True, self.BLACK)
        instr_rect = instr.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(instr, instr_rect)

    def draw_playing(self):
        # Background
        if getattr(self, 'background', None):
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Create white opacity mask
        white_mask = pygame.Surface((self.screen_width, self.screen_height))
        white_mask.fill((255, 255, 255))
        white_mask.set_alpha(204)  # 80% opacity
        self.screen.blit(white_mask, (0, 0))

        # Title at top
        title = self.title_font.render("Guess the Answer", True, self.BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        # Question text (wrap if needed, centered) - same position as intro
        question_rect = pygame.Rect(200, 280, self.screen_width - 400, 200)
        self.draw_wrapped_text(self.current_question, self.current_question_font, self.BLACK, question_rect)

        # Input box - Draw with clear white background
        pygame.draw.rect(self.screen, self.INPUT_BG, self.input_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.INPUT_BORDER, self.input_rect, 3, border_radius=8)

        # Render user input with padding
        if self.user_input:
            input_surf = self.text_font.render(self.user_input, True, self.BLACK)
            input_rect = input_surf.get_rect(midleft=(self.input_rect.left + 20, self.input_rect.centery))
            self.screen.blit(input_surf, input_rect)
            
            # Draw blinking cursor after text
            if self.cursor_visible:
                cursor_x = input_rect.right + 2
                cursor_y_top = self.input_rect.centery - 15
                cursor_y_bottom = self.input_rect.centery + 15
                pygame.draw.line(self.screen, self.BLACK, (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)
        else:
            # Show placeholder text when empty
            placeholder = self.text_font.render("Type your answer here...", True, (150, 150, 150))
            placeholder_rect = placeholder.get_rect(midleft=(self.input_rect.left + 20, self.input_rect.centery))
            self.screen.blit(placeholder, placeholder_rect)
            
            # Draw blinking cursor at start position when empty
            if self.cursor_visible:
                cursor_x = self.input_rect.left + 20
                cursor_y_top = self.input_rect.centery - 15
                cursor_y_bottom = self.input_rect.centery + 15
                pygame.draw.line(self.screen, (150, 150, 150), (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)

        # Submit button with better styling (like random_event)
        btn_color = self.BUTTON_HOVER if self.hovered == 'submit' else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, btn_color, self.submit_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.INPUT_BORDER, self.submit_rect, 3, border_radius=10)
        btn_text = self.button_font.render("Submit", True, self.WHITE)
        btn_text_rect = btn_text.get_rect(center=self.submit_rect.center)
        self.screen.blit(btn_text, btn_text_rect)

        # Hint - positioned at bottom (like random_event instruction)
        hint = self.text_font.render("Answers are not case-sensitive", True, self.BLACK)
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
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

            # Create white opacity mask
            white_mask = pygame.Surface((self.screen_width, self.screen_height))
            white_mask.fill((255, 255, 255))
            white_mask.set_alpha(204)  # 80% opacity
            self.screen.blit(white_mask, (0, 0))

            # Result title (like random_event "Your Card")
            if self.result == 'win':
                result_title = "Correct!"
                result_color = (34, 139, 34)  # Green
            else:
                result_title = "Incorrect!"
                result_color = (220, 20, 60)  # Red

            title_surf = self.title_font.render(result_title, True, result_color)
            title_rect = title_surf.get_rect(center=(self.screen_width // 2, 200))
            self.screen.blit(title_surf, title_rect)

            # Show correct answer if wrong
            if self.result == 'lose':
                answer_text = f"The correct answer is: {self.current_answer}"
                answer_surf = self.subtitle_font.render(answer_text, True, self.BLACK)
                answer_rect = answer_surf.get_rect(center=(self.screen_width // 2, 350))
                self.screen.blit(answer_surf, answer_rect)

        # Instruction at bottom (like random_event)
        instr = self.text_font.render("Press SPACE or CLICK to continue", True, self.BLACK)
        instr_rect = instr.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
        self.screen.blit(instr, instr_rect)

    def draw_wrapped_text(self, text, font, color, rect, line_spacing=8):
        """Draw multiline wrapped text into rect area (centered)."""
        words = text.split(' ')
        lines = []
        cur = ''
        for w in words:
            test = cur + (' ' if cur else '') + w
            if font.size(test)[0] <= rect.width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        # Center vertically
        total_height = sum(font.size(line)[1] + line_spacing for line in lines) - line_spacing
        y = rect.top + (rect.height - total_height) // 2
        
        for line in lines:
            surf = font.render(line, True, color)
            # Center horizontally
            x = rect.left + (rect.width - surf.get_width()) // 2
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + line_spacing

    def draw(self):
        # Update cursor blink
        if self.state == self.STATE_PLAYING:
            current_time = pygame.time.get_ticks()
            if current_time - self.cursor_timer >= self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = current_time
        
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
                    # Reset cursor when entering playing state
                    self.cursor_visible = True
                    self.cursor_timer = pygame.time.get_ticks()
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
                    # Reset cursor visibility when typing
                    self.cursor_visible = True
                    self.cursor_timer = pygame.time.get_ticks()
                else:
                    # Add character if printable
                    char = event.unicode
                    if char and len(char) == 1:
                        self.user_input += char
                        # Reset cursor visibility when typing
                        self.cursor_visible = True
                        self.cursor_timer = pygame.time.get_ticks()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.state == self.STATE_INTRO:
                    self.state = self.STATE_PLAYING
                    # Reset cursor when entering playing state
                    self.cursor_visible = True
                    self.cursor_timer = pygame.time.get_ticks()
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
        """Update screen size and recalculate UI positions."""
        self.screen = screen
        self.screen_width = 1280
        self.screen_height = 832
        
        # Recalculate input rect position
        self.input_rect = pygame.Rect(0, 0, 600, 60)
        self.input_rect.center = (self.screen_width // 2, self.screen_height // 2 + 140)
        
        # Recalculate submit button position
        self.submit_rect = pygame.Rect(0, 0, 220, 60)
        self.submit_rect.center = (self.screen_width // 2, self.input_rect.bottom + 50)
