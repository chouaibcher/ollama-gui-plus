"""
Enhanced UI components and styling for the Ollama GUI application.
Provides modern, beautiful UI elements with theme support.
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Callable, Optional, Any, Dict
from ..utils.theme_manager import ThemeManager


class ModernButton(tk.Frame):
    """A modern, customizable button widget."""
    
    def __init__(self, parent, text: str = "", command: Optional[Callable] = None, 
                 style: str = "primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.style_type = style
        
        # Create button label
        self.label = tk.Label(
            self,
            text=text,
            cursor="hand2",
            relief="flat",
            borderwidth=0
        )
        self.label.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Bind events
        self.label.bind("<Button-1>", self._on_click)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Configure initial style
        self._apply_style()
    
    def _apply_style(self):
        """Apply styling based on theme and button type."""
        # This will be called by theme manager
        pass
    
    def _on_click(self, event=None):
        """Handle button click."""
        if self.command:
            self.command()
    
    def _on_enter(self, event=None):
        """Handle mouse enter."""
        # Hover effect will be handled by theme manager
        pass
    
    def _on_leave(self, event=None):
        """Handle mouse leave."""
        # Reset to normal state
        pass
    
    def configure_text(self, text: str):
        """Update button text."""
        self.label.configure(text=text)


class ModernEntry(tk.Frame):
    """A modern entry widget with placeholder support."""
    
    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_active = False
        
        # Create entry widget
        self.entry = tk.Entry(
            self,
            relief="flat",
            borderwidth=0,
            highlightthickness=2
        )
        self.entry.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Bind events for placeholder
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Set initial placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text."""
        if not self.entry.get() and self.placeholder:
            self.placeholder_active = True
            self.entry.insert(0, self.placeholder)
            # Placeholder styling will be handled by theme manager
    
    def _hide_placeholder(self):
        """Hide placeholder text."""
        if self.placeholder_active:
            self.placeholder_active = False
            self.entry.delete(0, tk.END)
    
    def _on_focus_in(self, event=None):
        """Handle focus in event."""
        self._hide_placeholder()
    
    def _on_focus_out(self, event=None):
        """Handle focus out event."""
        if not self.entry.get():
            self._show_placeholder()
    
    def get(self) -> str:
        """Get entry value."""
        if self.placeholder_active:
            return ""
        return self.entry.get()
    
    def set(self, value: str):
        """Set entry value."""
        self._hide_placeholder()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def clear(self):
        """Clear entry value."""
        self.entry.delete(0, tk.END)
        self._show_placeholder()


class ModernScrollableText(tk.Frame):
    """A modern scrollable text widget with better styling."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create text widget
        self.text = tk.Text(
            self,
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=15,
            pady=15
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.text.yview,
            style="Themed.Vertical.TScrollbar"
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure scrolling
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel
        self.text.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def insert(self, index, text, *args):
        """Insert text."""
        self.text.insert(index, text, *args)
    
    def delete(self, start, end=None):
        """Delete text."""
        self.text.delete(start, end)
    
    def see(self, index):
        """Scroll to see index."""
        self.text.see(index)
    
    def config(self, **kwargs):
        """Configure text widget."""
        self.text.config(**kwargs)
    
    def configure(self, **kwargs):
        """Configure text widget."""
        self.text.configure(**kwargs)


class ModernChatBubble(tk.Frame):
    """A modern chat bubble widget."""
    
    def __init__(self, parent, text: str = "", is_user: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_user = is_user
        self.text_content = text
        
        # Configure bubble container
        self.configure(relief="flat", borderwidth=0)
        
        # Create content frame with padding
        self.content_frame = tk.Frame(self, relief="flat", borderwidth=0)
        
        # Position bubble based on sender
        if is_user:
            self.content_frame.pack(side="right", padx=(50, 10), pady=5)
        else:
            self.content_frame.pack(side="left", padx=(10, 50), pady=5)
        
        # Create text label
        self.label = tk.Label(
            self.content_frame,
            text=text,
            wraplength=400,
            justify="left",
            relief="flat",
            borderwidth=0
        )
        self.label.pack(padx=15, pady=10)
        
        # Apply initial styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply bubble styling based on theme."""
        # This will be called by theme manager
        pass
    
    def update_text(self, text: str):
        """Update bubble text."""
        self.text_content = text
        self.label.configure(text=text)
    
    def get_text(self) -> str:
        """Get bubble text."""
        return self.text_content


class ModernProgressBar(tk.Frame):
    """A modern progress bar with enhanced styling."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create progress bar
        self.progress = ttk.Progressbar(
            self,
            mode="indeterminate",
            style="Themed.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x", expand=True, padx=10, pady=5)
    
    def start(self, interval=None):
        """Start progress animation."""
        self.progress.start(interval)
    
    def stop(self):
        """Stop progress animation."""
        self.progress.stop()


class EnhancedUI:
    """Enhanced UI components manager."""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.components = []
    
    def create_modern_button(self, parent, text: str, command: Optional[Callable] = None,
                           style: str = "primary") -> ModernButton:
        """Create a modern styled button."""
        button = ModernButton(parent, text=text, command=command, style=style)
        self._apply_button_theme(button)
        self.components.append(button)
        return button
    
    def create_modern_entry(self, parent, placeholder: str = "") -> ModernEntry:
        """Create a modern styled entry."""
        entry = ModernEntry(parent, placeholder=placeholder)
        self._apply_entry_theme(entry)
        self.components.append(entry)
        return entry
    
    def create_scrollable_text(self, parent) -> ModernScrollableText:
        """Create a modern scrollable text widget."""
        text_widget = ModernScrollableText(parent)
        self._apply_text_theme(text_widget)
        self.components.append(text_widget)
        return text_widget
    
    def create_chat_bubble(self, parent, text: str, is_user: bool = False) -> ModernChatBubble:
        """Create a modern chat bubble."""
        bubble = ModernChatBubble(parent, text=text, is_user=is_user)
        self._apply_bubble_theme(bubble)
        self.components.append(bubble)
        return bubble
    
    def create_progress_bar(self, parent) -> ModernProgressBar:
        """Create a modern progress bar."""
        progress = ModernProgressBar(parent)
        self.components.append(progress)
        return progress
    
    def _apply_button_theme(self, button: ModernButton):
        """Apply theme to button."""
        theme = self.theme_manager.get_current_theme()
        
        if button.style_type == "primary":
            bg_color = theme.button_bg
            text_color = theme.button_text
            hover_color = theme.button_hover
        elif button.style_type == "secondary":
            bg_color = theme.bg_secondary
            text_color = theme.text_primary
            hover_color = theme.bg_hover
        else:  # default
            bg_color = theme.bg_tertiary
            text_color = theme.text_primary
            hover_color = theme.bg_hover
        
        button.configure(bg=bg_color)
        button.label.configure(bg=bg_color, fg=text_color)
        
        # Store hover colors for event handling
        button.normal_bg = bg_color
        button.hover_bg = hover_color
        
        # Rebind events with theme colors
        def on_enter(event=None):
            button.configure(bg=hover_color)
            button.label.configure(bg=hover_color)
        
        def on_leave(event=None):
            button.configure(bg=bg_color)
            button.label.configure(bg=bg_color)
        
        button.label.bind("<Enter>", on_enter, add=False)
        button.label.bind("<Leave>", on_leave, add=False)
        button.bind("<Enter>", on_enter, add=False)
        button.bind("<Leave>", on_leave, add=False)
    
    def _apply_entry_theme(self, entry: ModernEntry):
        """Apply theme to entry."""
        theme = self.theme_manager.get_current_theme()
        
        entry.configure(bg=theme.bg_primary, highlightbackground=theme.border)
        entry.entry.configure(
            bg=theme.bg_secondary,
            fg=theme.text_primary,
            insertbackground=theme.text_primary,
            selectbackground=theme.text_accent,
            selectforeground=theme.bg_primary,
            highlightcolor=theme.text_accent
        )
    
    def _apply_text_theme(self, text_widget: ModernScrollableText):
        """Apply theme to text widget."""
        theme = self.theme_manager.get_current_theme()
        
        text_widget.configure(bg=theme.bg_primary)
        text_widget.text.configure(
            bg=theme.bg_primary,
            fg=theme.text_primary,
            insertbackground=theme.text_primary,
            selectbackground=theme.text_accent,
            selectforeground=theme.bg_primary
        )
    
    def _apply_bubble_theme(self, bubble: ModernChatBubble):
        """Apply theme to chat bubble."""
        bubble_style = self.theme_manager.create_chat_bubble_style(bubble.is_user)
        
        bubble.configure(bg=self.theme_manager.get_current_theme().bg_primary)
        bubble.content_frame.configure(bg=bubble_style['background'])
        bubble.label.configure(**bubble_style)
    
    def update_all_themes(self):
        """Update themes for all components."""
        for component in self.components:
            if hasattr(component, 'winfo_exists') and component.winfo_exists():
                if isinstance(component, ModernButton):
                    self._apply_button_theme(component)
                elif isinstance(component, ModernEntry):
                    self._apply_entry_theme(component)
                elif isinstance(component, ModernScrollableText):
                    self._apply_text_theme(component)
                elif isinstance(component, ModernChatBubble):
                    self._apply_bubble_theme(component)
        
        # Clean up destroyed components
        self.components = [c for c in self.components if hasattr(c, 'winfo_exists') and c.winfo_exists()]
