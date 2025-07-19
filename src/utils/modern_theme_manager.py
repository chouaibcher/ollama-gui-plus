"""
Modern theme manager using TKinterModernThemes.
Provides better modern themes and easier theme switching.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

try:
    import TKinterModernThemes as TKMT
except ImportError:
    print("TKinterModernThemes not installed. Please install with: pip install TKinterModernThemes")
    TKMT = None


class ModernTheme(Enum):
    """Available modern themes."""
    PARK_DARK = ("park", "dark")
    PARK_LIGHT = ("park", "light")
    SUN_VALLEY_DARK = ("sun-valley", "dark")
    SUN_VALLEY_LIGHT = ("sun-valley", "light")
    AZURE_DARK = ("azure", "dark")
    AZURE_LIGHT = ("azure", "light")


class SimpleThemeManager:
    """Simple theme manager for TKinterModernThemes integration."""
    
    def __init__(self):
        self.current_theme = ModernTheme.PARK_DARK
        self.theme_callbacks: List[Callable] = []
        
        # Theme descriptions
        self.theme_descriptions = {
            ModernTheme.PARK_DARK: "Dark theme with green accents (Excel-inspired)",
            ModernTheme.PARK_LIGHT: "Light theme with green accents (Excel-inspired)",
            ModernTheme.SUN_VALLEY_DARK: "Dark theme (Windows 11 style)",
            ModernTheme.SUN_VALLEY_LIGHT: "Light theme (Windows 11 style)",
            ModernTheme.AZURE_DARK: "Dark theme with blue accents",
            ModernTheme.AZURE_LIGHT: "Light theme with blue accents"
        }
        
        self.dark_themes = [
            ModernTheme.PARK_DARK,
            ModernTheme.SUN_VALLEY_DARK,
            ModernTheme.AZURE_DARK
        ]
        
        self.light_themes = [
            ModernTheme.PARK_LIGHT,
            ModernTheme.SUN_VALLEY_LIGHT,
            ModernTheme.AZURE_LIGHT
        ]
        
        # Accent colors for dark and light themes
        self.accent_colors = {
            "dark": {
                "accent": "#60A5FA",  # Blue accent
                "error": "#F87171",   # Red for errors
                "success": "#34D399"  # Green for success
            },
            "light": {
                "accent": "#3B82F6",  # Blue accent
                "error": "#DC2626",   # Red for errors
                "success": "#059669"  # Green for success
            }
        }
    
    def get_available_themes(self) -> List[ModernTheme]:
        """Get list of all available themes."""
        return list(ModernTheme)
    
    def get_dark_themes(self) -> List[ModernTheme]:
        """Get list of dark themes."""
        return self.dark_themes.copy()
    
    def get_light_themes(self) -> List[ModernTheme]:
        """Get list of light themes."""
        return self.light_themes.copy()
    
    def is_dark_mode(self) -> bool:
        """Check if current theme is dark."""
        return self.current_theme in self.dark_themes
    
    def get_current_theme(self) -> ModernTheme:
        """Get the current theme."""
        return self.current_theme
    
    def set_theme(self, theme: ModernTheme) -> bool:
        """Set a specific theme (requires app restart)."""
        self.current_theme = theme
        
        # Notify callbacks about theme change
        for callback in self.theme_callbacks:
            try:
                callback(theme)
            except Exception as e:
                print(f"Error in theme callback: {e}")
        
        return True
    
    def toggle_theme_mode(self) -> ModernTheme:
        """Toggle between dark and light themes."""
        if self.is_dark_mode():
            # Switch to corresponding light theme
            if self.current_theme == ModernTheme.PARK_DARK:
                new_theme = ModernTheme.PARK_LIGHT
            elif self.current_theme == ModernTheme.SUN_VALLEY_DARK:
                new_theme = ModernTheme.SUN_VALLEY_LIGHT
            elif self.current_theme == ModernTheme.AZURE_DARK:
                new_theme = ModernTheme.AZURE_LIGHT
            else:
                new_theme = ModernTheme.PARK_LIGHT
        else:
            # Switch to corresponding dark theme
            if self.current_theme == ModernTheme.PARK_LIGHT:
                new_theme = ModernTheme.PARK_DARK
            elif self.current_theme == ModernTheme.SUN_VALLEY_LIGHT:
                new_theme = ModernTheme.SUN_VALLEY_DARK
            elif self.current_theme == ModernTheme.AZURE_LIGHT:
                new_theme = ModernTheme.AZURE_DARK
            else:
                new_theme = ModernTheme.PARK_DARK
        
        self.set_theme(new_theme)
        return new_theme
    
    def get_theme_description(self, theme: Optional[ModernTheme] = None) -> str:
        """Get description of a theme."""
        theme = theme or self.current_theme
        return self.theme_descriptions.get(theme, "Unknown theme")
    
    def add_theme_callback(self, callback: Callable[[ModernTheme], None]) -> None:
        """Add a callback to be called when theme changes."""
        self.theme_callbacks.append(callback)
    
    def remove_theme_callback(self, callback: Callable[[ModernTheme], None]) -> None:
        """Remove a theme callback."""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
    
    def create_theme_menu(self, parent_menu) -> tk.Menu:
        """Create a theme submenu for the menu bar."""
        theme_menu = tk.Menu(parent_menu, tearoff=0)
        
        # Add theme categories
        dark_menu = tk.Menu(theme_menu, tearoff=0)
        light_menu = tk.Menu(theme_menu, tearoff=0)
        
        # Add dark themes
        for theme in self.dark_themes:
            theme_name, mode = theme.value
            dark_menu.add_command(
                label=f"{theme_name.title()} - {self.get_theme_description(theme)}",
                command=lambda t=theme: self._show_restart_message(t)
            )
        
        # Add light themes
        for theme in self.light_themes:
            theme_name, mode = theme.value
            light_menu.add_command(
                label=f"{theme_name.title()} - {self.get_theme_description(theme)}",
                command=lambda t=theme: self._show_restart_message(t)
            )
        
        # Add submenus
        theme_menu.add_cascade(label="🌙 Dark Themes", menu=dark_menu)
        theme_menu.add_cascade(label="☀️ Light Themes", menu=light_menu)
        theme_menu.add_separator()
        theme_menu.add_command(
            label="🔄 Toggle Light/Dark (Restart Required)",
            command=self._toggle_with_restart_message
        )
        
        return theme_menu
    
    def _show_restart_message(self, theme: ModernTheme) -> None:
        """Show restart message when theme is changed."""
        self.set_theme(theme)
        try:
            from tkinter import messagebox
            theme_name, mode = theme.value
            messagebox.showinfo(
                "Theme Changed", 
                f"Theme changed to {theme_name.title()} ({mode.title()}).\n\n"
                "Please restart the application to see the changes."
            )
        except ImportError:
            print(f"Theme changed to {theme.value[0]} ({theme.value[1]}). Please restart the application.")
    
    def _toggle_with_restart_message(self) -> None:
        """Toggle theme and show restart message."""
        new_theme = self.toggle_theme_mode()
        self._show_restart_message(new_theme)
    
    def get_chat_bubble_colors(self, is_user: bool = False) -> Dict[str, str]:
        """Get chat bubble colors for current theme."""
        # These colors work well with all TKinterModernThemes
        if self.is_dark_mode():
            if is_user:
                return {
                    'bg': '#0078D4',      # Blue for user messages
                    'fg': '#FFFFFF',      # White text
                    'relief': 'flat',
                    'borderwidth': 0
                }
            else:
                return {
                    'bg': '#3A3A3A',      # Dark gray for AI messages
                    'fg': '#FFFFFF',      # White text
                    'relief': 'flat',
                    'borderwidth': 0
                }
        else:
            if is_user:
                return {
                    'bg': '#0078D4',      # Blue for user messages
                    'fg': '#FFFFFF',      # White text
                    'relief': 'flat',
                    'borderwidth': 0
                }
            else:
                return {
                    'bg': '#F3F2F1',      # Light gray for AI messages
                    'fg': '#323130',      # Dark text
                    'relief': 'flat',
                    'borderwidth': 0
                }
    
    def style_chat_widget(self, widget: tk.Text) -> None:
        """Apply modern styling to chat text widget."""
        # TKinterModernThemes handles most styling automatically
        # We just need to ensure proper colors for readability
        if self.is_dark_mode():
            widget.configure(
                selectbackground='#0078D4',
                selectforeground='#FFFFFF',
                insertbackground='#FFFFFF'
            )
        else:
            widget.configure(
                selectbackground='#0078D4',
                selectforeground='#FFFFFF',
                insertbackground='#323130'
            )
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get current theme information."""
        theme_name, mode = self.current_theme.value
        return {
            'name': theme_name,
            'mode': mode,
            'description': self.get_theme_description(),
            'is_dark': self.is_dark_mode(),
            'category': 'Dark' if self.is_dark_mode() else 'Light'
        }
    
    def style_tk_widget(self, widget, widget_type: str = "default") -> None:
        """Apply theme styling to standard tkinter widgets."""
        # TKinterModernThemes handles most styling automatically
        # This is a simple fallback method for custom widgets
        
        if widget_type == "menu":
            # Style menu with appropriate colors based on theme
            if self.is_dark_mode():
                widget.configure(
                    bg='#2D2D2D',
                    fg='#FFFFFF',
                    activebackground='#3A3A3A',
                    activeforeground='#FFFFFF',
                    selectcolor='#60A5FA'
                )
            else:
                widget.configure(
                    bg='#F0F0F0',
                    fg='#000000',
                    activebackground='#E0E0E0',
                    activeforeground='#000000',
                    selectcolor='#3B82F6'
                )
        elif widget_type == "text":
            # Style text widgets
            if self.is_dark_mode():
                widget.configure(
                    bg='#2D2D2D',
                    fg='#FFFFFF',
                    insertbackground='#FFFFFF',
                    selectbackground='#0078D4',
                    selectforeground='#FFFFFF'
                )
            else:
                widget.configure(
                    bg='#FFFFFF',
                    fg='#000000',
                    insertbackground='#000000',
                    selectbackground='#0078D4',
                    selectforeground='#FFFFFF'
                )
        else:
            # Default styling for other widgets
            if self.is_dark_mode():
                widget.configure(
                    bg='#2D2D2D',
                    fg='#FFFFFF'
                )
            else:
                widget.configure(
                    bg='#FFFFFF',
                    fg='#000000'
                )


# Global theme manager instance
theme_manager = SimpleThemeManager()
