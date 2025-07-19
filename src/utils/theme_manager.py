"""
Theme manager for the Ollama GUI application.
Handles light/dark mode themes and UI styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "light"
    DARK = "dark"


@dataclass
class ThemeColors:
    """Color scheme for a theme."""
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str
    bg_active: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_accent: str
    text_error: str
    text_success: str
    
    # Border and separator colors
    border: str
    separator: str
    
    # Chat bubble colors
    user_bubble_bg: str
    user_bubble_text: str
    ai_bubble_bg: str
    ai_bubble_text: str
    
    # Button colors
    button_bg: str
    button_text: str
    button_hover: str
    button_active: str


class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self):
        self.current_mode = ThemeMode.LIGHT
        self.themes = self._create_themes()
        self.style = None
        self._themed_widgets = []
    
    def _create_themes(self) -> Dict[ThemeMode, ThemeColors]:
        """Create light and dark theme color schemes."""
        return {
            ThemeMode.LIGHT: ThemeColors(
                # Light theme
                bg_primary="#FFFFFF",
                bg_secondary="#F5F5F5",
                bg_tertiary="#E9ECEF",
                bg_hover="#E3E6EA",
                bg_active="#D1D5DB",
                
                text_primary="#1F2937",
                text_secondary="#6B7280",
                text_accent="#3B82F6",
                text_error="#DC2626",
                text_success="#059669",
                
                border="#D1D5DB",
                separator="#E5E7EB",
                
                user_bubble_bg="#3B82F6",
                user_bubble_text="#FFFFFF",
                ai_bubble_bg="#F3F4F6",
                ai_bubble_text="#1F2937",
                
                button_bg="#3B82F6",
                button_text="#FFFFFF",
                button_hover="#2563EB",
                button_active="#1D4ED8",
            ),
            
            ThemeMode.DARK: ThemeColors(
                # Dark theme
                bg_primary="#1F2937",
                bg_secondary="#374151",
                bg_tertiary="#4B5563",
                bg_hover="#6B7280",
                bg_active="#9CA3AF",
                
                text_primary="#F9FAFB",
                text_secondary="#D1D5DB",
                text_accent="#60A5FA",
                text_error="#F87171",
                text_success="#34D399",
                
                border="#6B7280",
                separator="#4B5563",
                
                user_bubble_bg="#3B82F6",
                user_bubble_text="#FFFFFF",
                ai_bubble_bg="#4B5563",
                ai_bubble_text="#F9FAFB",
                
                button_bg="#3B82F6",
                button_text="#FFFFFF",
                button_hover="#2563EB",
                button_active="#1D4ED8",
            )
        }
    
    def get_current_theme(self) -> ThemeColors:
        """Get the current theme colors."""
        return self.themes[self.current_mode]
    
    def toggle_theme(self) -> ThemeMode:
        """Toggle between light and dark modes."""
        self.current_mode = ThemeMode.DARK if self.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        return self.current_mode
    
    def set_theme(self, mode: ThemeMode) -> None:
        """Set a specific theme mode."""
        self.current_mode = mode
    
    def configure_ttk_style(self, root: tk.Tk) -> None:
        """Configure ttk styles for current theme."""
        if not self.style:
            self.style = ttk.Style(root)
        
        theme = self.get_current_theme()
        
        # Configure ttk styles
        self.style.theme_use('clam')  # Use clam as base theme
        
        # Configure frame styles
        self.style.configure(
            "Themed.TFrame",
            background=theme.bg_primary,
            borderwidth=0,
            relief="flat"
        )
        
        # Configure button styles
        self.style.configure(
            "Themed.TButton",
            background=theme.button_bg,
            foreground=theme.button_text,
            borderwidth=1,
            focuscolor='none',
            relief="flat",
            padding=(10, 5)
        )
        
        self.style.map(
            "Themed.TButton",
            background=[
                ('active', theme.button_hover),
                ('pressed', theme.button_active)
            ]
        )
        
        # Configure entry styles
        self.style.configure(
            "Themed.TEntry",
            fieldbackground=theme.bg_secondary,
            foreground=theme.text_primary,
            borderwidth=1,
            insertcolor=theme.text_primary
        )
        
        # Configure combobox styles
        self.style.configure(
            "Themed.TCombobox",
            fieldbackground=theme.bg_secondary,
            foreground=theme.text_primary,
            background=theme.bg_secondary,
            borderwidth=1,
            arrowcolor=theme.text_primary
        )
        
        # Configure label styles
        self.style.configure(
            "Themed.TLabel",
            background=theme.bg_primary,
            foreground=theme.text_primary
        )
        
        # Configure progressbar styles
        self.style.configure(
            "Themed.Horizontal.TProgressbar",
            background=theme.text_accent,
            troughcolor=theme.bg_secondary,
            borderwidth=0,
            lightcolor=theme.text_accent,
            darkcolor=theme.text_accent
        )
        
        # Configure scrollbar styles
        self.style.configure(
            "Themed.Vertical.TScrollbar",
            background=theme.bg_secondary,
            troughcolor=theme.bg_primary,
            borderwidth=0,
            arrowcolor=theme.text_secondary,
            darkcolor=theme.bg_secondary,
            lightcolor=theme.bg_secondary
        )
    
    def style_tk_widget(self, widget: tk.Widget, widget_type: str = "default") -> None:
        """Apply theme styling to tkinter widgets."""
        theme = self.get_current_theme()
        
        if widget_type == "text":
            widget.configure(
                bg=theme.bg_primary,
                fg=theme.text_primary,
                insertbackground=theme.text_primary,
                selectbackground=theme.text_accent,
                selectforeground=theme.bg_primary,
                highlightbackground=theme.border,
                highlightcolor=theme.text_accent
            )
        
        elif widget_type == "listbox":
            widget.configure(
                bg=theme.bg_secondary,
                fg=theme.text_primary,
                selectbackground=theme.text_accent,
                selectforeground=theme.bg_primary,
                highlightbackground=theme.border,
                highlightcolor=theme.text_accent
            )
        
        elif widget_type == "menu":
            widget.configure(
                bg=theme.bg_secondary,
                fg=theme.text_primary,
                activebackground=theme.bg_hover,
                activeforeground=theme.text_primary,
                selectcolor=theme.text_accent
            )
        
        elif widget_type == "label":
            widget.configure(
                bg=theme.bg_primary,
                fg=theme.text_primary
            )
        
        else:  # default
            widget.configure(
                bg=theme.bg_primary,
                fg=theme.text_primary
            )
        
        # Track themed widgets for updates
        if widget not in self._themed_widgets:
            self._themed_widgets.append((widget, widget_type))
    
    def create_chat_bubble_style(self, is_user: bool = False) -> Dict[str, Any]:
        """Create styling for chat bubbles."""
        theme = self.get_current_theme()
        
        if is_user:
            return {
                'background': theme.user_bubble_bg,
                'foreground': theme.user_bubble_text,
                'highlightbackground': theme.user_bubble_bg,
                'highlightcolor': theme.user_bubble_bg,
                'relief': 'flat',
                'borderwidth': 0,
                'padx': 12,
                'pady': 8
            }
        else:
            return {
                'background': theme.ai_bubble_bg,
                'foreground': theme.ai_bubble_text,
                'highlightbackground': theme.ai_bubble_bg,
                'highlightcolor': theme.ai_bubble_bg,
                'relief': 'flat',
                'borderwidth': 0,
                'padx': 12,
                'pady': 8
            }
    
    def update_all_widgets(self, root: tk.Tk) -> None:
        """Update all themed widgets when theme changes."""
        # Update ttk styles
        self.configure_ttk_style(root)
        
        # Update root window
        theme = self.get_current_theme()
        root.configure(bg=theme.bg_primary)
        
        # Update tracked widgets
        for widget, widget_type in self._themed_widgets:
            try:
                if widget.winfo_exists():
                    self.style_tk_widget(widget, widget_type)
            except tk.TclError:
                # Widget was destroyed, remove from tracking
                pass
        
        # Clean up destroyed widgets
        self._themed_widgets = [
            (widget, widget_type) for widget, widget_type in self._themed_widgets
            if widget.winfo_exists()
        ]
    
    def is_dark_mode(self) -> bool:
        """Check if current theme is dark mode."""
        return self.current_mode == ThemeMode.DARK
