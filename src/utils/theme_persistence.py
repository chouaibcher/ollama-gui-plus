"""
Theme persistence utility for saving and loading theme preferences.
"""

import json
import os
from typing import Tuple, Optional
from pathlib import Path


class ThemePersistence:
    """Handle saving and loading theme preferences."""
    
    def __init__(self):
        # Use user's home directory for config
        self.config_dir = Path.home() / ".ollama-gui-plus"
        self.config_file = self.config_dir / "theme_config.json"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Default theme
        self.default_theme = ("park", "dark")
    
    def save_theme(self, theme_name: str, mode: str) -> bool:
        """Save the current theme preference."""
        try:
            config = {
                "theme": theme_name,
                "mode": mode
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving theme preference: {e}")
            return False
    
    def load_theme(self) -> Tuple[str, str]:
        """Load the saved theme preference."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                theme = config.get("theme", self.default_theme[0])
                mode = config.get("mode", self.default_theme[1])
                
                return (theme, mode)
            else:
                return self.default_theme
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return self.default_theme
    
    def get_next_theme_mode(self, current_theme: str, current_mode: str) -> Tuple[str, str]:
        """Get the next theme mode (toggle between light and dark)."""
        if current_mode == "dark":
            return (current_theme, "light")
        else:
            return (current_theme, "dark")


# Global theme persistence instance
theme_persistence = ThemePersistence()
