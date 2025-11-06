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


# Create global instance
game_state = GameState()
