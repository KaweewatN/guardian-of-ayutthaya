"""
Fonts Module
Centralized font management for the game
"""
import pygame

DEFAULT_FONT = 'Inknut Antiqua'


class Fonts:
    """Manages all game fonts"""
    
    # Initialize pygame font system
    pygame.font.init()
    
    # Button fonts
    BUTTON_FONT = pygame.font.SysFont(DEFAULT_FONT, 48, bold=True)
    BUTTON_FONT_LARGE = pygame.font.SysFont(DEFAULT_FONT, 56, bold=True)
    BUTTON_FONT_SMALL = pygame.font.SysFont(DEFAULT_FONT, 36, bold=True)
    
    # Title fonts
    TITLE_FONT = pygame.font.SysFont(DEFAULT_FONT, 72, bold=True)
    SUBTITLE_FONT = pygame.font.SysFont(DEFAULT_FONT, 48, bold=False)
    
    # Text fonts
    TEXT_FONT = pygame.font.SysFont(DEFAULT_FONT, 24, bold=False)
    TEXT_FONT_BOLD = pygame.font.SysFont(DEFAULT_FONT, 24, bold=True)
    
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
