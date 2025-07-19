"""
Main entry point for the Ollama GUI application.
This module initializes the application and starts the main event loop.
"""

import sys

try:
    import tkinter as tk
    from tkinter import ttk
except (ModuleNotFoundError, ImportError):
    print(
        "Your Python installation does not include the Tk library. \n"
        "Please refer to https://github.com/chyok/ollama-gui?tab=readme-ov-file#-qa"
    )
    sys.exit(0)

from src.views.main_view import MainView

__version__ = "1.2.1"


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    root.title("Ollama GUI")
    
    # Center the window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 600
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Configure grid weights
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)  # Chat area should expand
    root.grid_rowconfigure(2, weight=0)  # Progress bar fixed height
    root.grid_rowconfigure(3, weight=0)  # Input area fixed height
    
    # Create and initialize the main view
    app = MainView(root)
    
    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
