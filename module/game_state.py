"""
Global Game State Manager
Manages game-wide state including selected character
"""


class GameState:
    """Singleton class to manage global game state"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Character data
        self.selected_character_id = 1  # Default to Plai Dum
        self.selected_character_data = None
        self.selected_character_image = 'elephant-1.png'
        
        # Alphabet deck / card collection state
        self.alphabet_requirements = {
            'A': 3,
            'Y': 2,
            'U': 1,
            'T': 2,
            'H': 1,
        }
        self.reset_alphabet_inventory()

        self._initialized = True
    
    def set_character(self, character_id, character_data):
        """Set the selected character"""
        self.selected_character_id = character_id
        self.selected_character_data = character_data
        self.selected_character_image = character_data.get('image', 'elephant-1.png')
        print(f"Character set: {character_data.get('name', 'Unknown')} (ID: {character_id})")
    
    def get_character_image(self):
        """Get the selected character image filename"""
        return self.selected_character_image
    
    def get_character_id(self):
        """Get the selected character ID"""
        return self.selected_character_id
    
    def get_character_data(self):
        """Get the full character data"""
        return self.selected_character_data
    
    def reset(self):
        """Reset to default state"""
        self.selected_character_id = 1
        self.selected_character_data = None
        self.selected_character_image = 'elephant-1.png'
        self.reset_alphabet_inventory()

    # ------------------------------------------------------------------
    # Alphabet card helpers
    # ------------------------------------------------------------------

    def reset_alphabet_inventory(self):
        """Reset alphabet deck counts and player's collected letters."""
        self.alphabet_deck_counts = {
            'A': 8,
            'Y': 4,
            'U': 2,
            'T': 6,
            'H': 2,
        }
        self.player_alphabet_counts = {
            letter: 0 for letter in self.alphabet_deck_counts
        }

    def get_player_alphabet_counts(self):
        """Return a copy of the player's collected alphabet card counts."""
        return self.player_alphabet_counts.copy()

    def get_alphabet_deck_counts(self):
        """Return a copy of the remaining alphabet deck counts."""
        return self.alphabet_deck_counts.copy()

    def draw_alphabet_cards(self, count):
        """Draw random alphabet cards from the deck.

        Args:
            count (int): Number of cards to draw.

        Returns:
            list[str]: Letters that were successfully drawn.
        """
        if count <= 0:
            return []

        import random

        available_letters = []
        for letter, remaining in self.alphabet_deck_counts.items():
            available_letters.extend(letter for _ in range(remaining))

        drawn_letters = []
        for _ in range(count):
            if not available_letters:
                break
            letter = random.choice(available_letters)
            drawn_letters.append(letter)
            available_letters.remove(letter)
            self.alphabet_deck_counts[letter] = max(0, self.alphabet_deck_counts.get(letter, 0) - 1)
            self.player_alphabet_counts[letter] = self.player_alphabet_counts.get(letter, 0) + 1

        return drawn_letters

    def return_alphabet_card(self, letter):
        """Return a single alphabet card back to the deck."""
        if not letter:
            return False

        letter = letter.upper()
        if letter not in self.player_alphabet_counts:
            return False

        if self.player_alphabet_counts[letter] <= 0:
            return False

        self.player_alphabet_counts[letter] -= 1
        self.alphabet_deck_counts[letter] = self.alphabet_deck_counts.get(letter, 0) + 1
        return True

    def list_player_alphabet_cards(self):
        """Return a list of individual alphabet cards the player holds."""
        letters = []
        for letter, amount in self.player_alphabet_counts.items():
            letters.extend(letter for _ in range(amount))
        return letters

    def has_ayutthaya_letters(self):
        """Check if the player has enough letters to spell AYUTTHAYA."""
        for letter, required in self.alphabet_requirements.items():
            if self.player_alphabet_counts.get(letter, 0) < required:
                return False
        return True


# Create global instance
game_state = GameState()
