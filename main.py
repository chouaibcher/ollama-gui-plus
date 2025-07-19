"""
Main entry point for the Ollama GUI application.
This module initializes the application and starts the main event loop.
"""

import sys
import subprocess
from tkinter import messagebox

try:
    import tkinter as tk
    from tkinter import ttk
    import TKinterModernThemes as TKMT
except (ModuleNotFoundError, ImportError) as e:
    print(f"Error importing: {e}")
    if "TKinterModernThemes" in str(e):
        print("TKinterModernThemes not found. Please install it with: pip install TKinterModernThemes")
    else:
        print(
            "Your Python installation does not include the Tk library. \n"
            "Please refer to https://github.com/chyok/ollama-gui?tab=readme-ov-file#-qa"
        )
    sys.exit(0)

from src.views.main_view import MainView
from src.utils.theme_persistence import theme_persistence

__version__ = "1.2.1"


class OllamaApp(TKMT.ThemedTKinterFrame):
    """Main Ollama GUI application using TKinterModernThemes."""
    
    def __init__(self, theme="park", mode="dark"):
        super().__init__("Ollama GUI", theme, mode)
        
        # Store current theme info
        self.current_theme = theme
        self.current_mode = mode
        
        # Configure the root window
        theme_display = f"{theme.title()} {mode.title()}"
        self.master.title(f"🦙 Ollama GUI - {theme_display}")
        
        # Center the window on screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 900
        window_height = 700
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.minsize(800, 600)
        
        # Configure grid weights for proper resizing
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        # Handle window close event to save theme
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Create the main application UI
        self._create_ollama_ui()
        
        # Start the application
        self.run()
    
    def _on_closing(self):
        """Handle application closing."""
        # Save current theme before closing
        theme_persistence.save_theme(self.current_theme, self.current_mode)
        self.master.destroy()
    
    def restart_with_theme(self, new_theme: str, new_mode: str):
        """Restart the application with a new theme."""
        # Save the new theme preference
        theme_persistence.save_theme(new_theme, new_mode)
        
        # Show confirmation message
        response = messagebox.askyesno(
            "Theme Change",
            f"The application will restart to apply the {new_mode} {new_theme} theme.\n\nContinue?",
            icon="question"
        )
        
        if response:
            # Close current application
            self.master.destroy()
            
            # Restart with new theme
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
    
    def _create_ollama_ui(self):
        """Create the Ollama GUI using the existing MainView with theming."""
        # Import here to avoid circular import
        from src.utils.system_utils import system_check
        
        # Check system first
        system_check(self.master)
        
        # Create a main frame that fills the window
        main_frame = tk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)  # Chat area should expand
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize the MainView with the themed frame
        from src.views.main_view import MainView
        self.main_view = MainView(main_frame, app_instance=self)


def main():
    """Main entry point for the application."""
    # Load saved theme preference
    theme, mode = theme_persistence.load_theme()
    
    # Create the themed application with saved preferences
    app = OllamaApp(theme=theme, mode=mode)


if __name__ == "__main__":
    main()
