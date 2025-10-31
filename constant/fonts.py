"""
Fonts Module
Centralized font management for the game
"""
import pygame
import os

DEFAULT_FONT = 'Inknut Antiqua'

# Path to font files (if available)
FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')


class Fonts:
    """Manages all game fonts"""
    
    # Initialize pygame font system
    pygame.font.init()
    
    # Try to load Inknut Antiqua from file, fallback to system font
    inknut_regular = os.path.join(FONT_DIR, 'InknutAntiqua-Regular.ttf')
    inknut_bold = os.path.join(FONT_DIR, 'InknutAntiqua-Bold.ttf')
    
    if os.path.exists(inknut_bold):
        # Use font file for bold fonts
        BUTTON_FONT = pygame.font.Font(inknut_bold, 48)
        BUTTON_FONT_LARGE = pygame.font.Font(inknut_bold, 56)
        BUTTON_FONT_SMALL = pygame.font.Font(inknut_bold, 36)
        TITLE_FONT = pygame.font.Font(inknut_bold, 72)
        TEXT_FONT_BOLD = pygame.font.Font(inknut_bold, 24)
    else:
        # Fallback to Baskerville (similar classic serif font on macOS)
        print("Warning: Inknut Antiqua font files not found, using Baskerville as fallback")
        BUTTON_FONT = pygame.font.SysFont('Baskerville', 48, bold=True)
        BUTTON_FONT_LARGE = pygame.font.SysFont('Baskerville', 56, bold=True)
        BUTTON_FONT_SMALL = pygame.font.SysFont('Baskerville', 36, bold=True)
        TITLE_FONT = pygame.font.SysFont('Baskerville', 72, bold=True)
        TEXT_FONT_BOLD = pygame.font.SysFont('Baskerville', 24, bold=True)
    
    if os.path.exists(inknut_regular):
        # Use font file for regular fonts
        SUBTITLE_FONT = pygame.font.Font(inknut_regular, 48)
        TEXT_FONT = pygame.font.Font(inknut_regular, 24)
    else:
        # Fallback
        SUBTITLE_FONT = pygame.font.SysFont('Baskerville', 48, bold=False)
        TEXT_FONT = pygame.font.SysFont('Baskerville', 24, bold=False)
    
    @staticmethod
    def get_button_font():
        """Get the standard button font"""
        return Fonts.BUTTON_FONT
    
    @staticmethod
    def get_title_font():
        """Get the title font"""
        return Fonts.TITLE_FONT
    
    @staticmethod
    def get_text_font():
        """Get the standard text font"""
        return Fonts.TEXT_FONT


# Export individual fonts for easy import
BUTTON_FONT = Fonts.BUTTON_FONT
BUTTON_FONT_LARGE = Fonts.BUTTON_FONT_LARGE
BUTTON_FONT_SMALL = Fonts.BUTTON_FONT_SMALL
TITLE_FONT = Fonts.TITLE_FONT
SUBTITLE_FONT = Fonts.SUBTITLE_FONT
TEXT_FONT = Fonts.TEXT_FONT
TEXT_FONT_BOLD = Fonts.TEXT_FONT_BOLD
