"""
Main view for the Ollama GUI application.
This module contains the main window and chat interface with modern themes.
"""

import tkinter as tk
from tkinter import ttk, font, messagebox
import webbrowser
import pprint
from typing import List, Optional
from ..models.chat_models import Model, ChatMessage
from ..viewmodels.chat_viewmodel import ChatViewModel
from ..utils.system_utils import system_check, get_platform_right_click_event
from ..utils.modern_theme_manager import SimpleThemeManager, theme_manager
from ..utils.document_processor import document_store
from .model_management_view import ModelManagementView
from .document_management_view import DocumentManagementView


class MainView:
    """Main application window and chat interface with modern themes."""
    
    def __init__(self, parent_frame, app_instance=None):
        self.root = parent_frame
        self.app_instance = app_instance  # Reference to main app for theme switching
        self.viewmodel = ChatViewModel()
        self.default_font = font.nametofont("TkTextFont").actual()["family"]
        self.label_widgets: List[tk.Label] = []
        self.model_management_view: Optional[ModelManagementView] = None
        self.document_management_view: Optional[DocumentManagementView] = None
        self.editor_window: Optional[tk.Toplevel] = None
        
        # Initialize simple theme manager
        self.theme_manager = theme_manager
        
        # UI Components
        self.chat_box: Optional[tk.Text] = None
        self.user_input: Optional[tk.Text] = None
        self.host_input: Optional[ttk.Entry] = None
        self.progress: Optional[ttk.Progressbar] = None
        self.stop_button: Optional[ttk.Button] = None
        self.send_button: Optional[ttk.Button] = None
        self.refresh_button: Optional[ttk.Button] = None
        self.model_select: Optional[ttk.Combobox] = None
        self.theme_button: Optional[ttk.Button] = None
        
        self._setup_viewmodel_callbacks()
        self._configure_fonts()
        self._init_layout()
        self._apply_initial_theme()
        self._check_system()
        self.viewmodel.refresh_models()
    
    def _configure_fonts(self) -> None:
        """Configure application fonts."""
        # Create custom fonts for better typography
        self.heading_font = font.Font(family=self.default_font, size=12, weight="bold")
        self.body_font = font.Font(family=self.default_font, size=10)
        self.ui_font = font.Font(family=self.default_font, size=9)
    
    def _apply_initial_theme(self) -> None:
        """Apply initial theme to the application."""
        # The theme is already applied by ThemedTk in main.py
        # Just configure chat components if they exist
        if self.chat_box:
            self.theme_manager.style_chat_widget(self.chat_box)
    
    def _setup_viewmodel_callbacks(self) -> None:
        """Setup callbacks between viewmodel and view."""
        self.viewmodel.on_models_updated = self._on_models_updated
        self.viewmodel.on_model_error = self._on_model_error
        self.viewmodel.on_chat_response_chunk = self._on_chat_response_chunk
        self.viewmodel.on_chat_response_complete = self._on_chat_response_complete
        self.viewmodel.on_chat_error = self._on_chat_error
        self.viewmodel.on_processing_started = self._on_processing_started
        self.viewmodel.on_processing_finished = self._on_processing_finished
        self.viewmodel.on_message_added = self._on_message_added
        self.viewmodel.on_chat_cleared = self._on_chat_cleared
    
    def _init_layout(self) -> None:
        """Initialize the UI layout."""
        self._create_header_frame()
        self._create_chat_container_frame()
        self._create_processbar_frame()
        self._create_input_frame()
        self._create_menu_bar()
        self._configure_chat_box_tags()
    
    def _create_header_frame(self) -> None:
        """Create the header with model selection, theme toggle, and host input."""
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(6, weight=1)

        # Model selection
        self.model_select = ttk.Combobox(
            header_frame, 
            state="readonly", 
            width=30,
            font=self.body_font
        )
        self.model_select.grid(row=0, column=0)
        self.model_select.bind("<<ComboboxSelected>>", self._on_model_selected)

        # Settings button with enhanced styling
        settings_button = ttk.Button(
            header_frame, 
            text="⚙️", 
            command=self._show_model_management, 
            width=3
        )
        settings_button.grid(row=0, column=1, padx=(5, 0))

        # Refresh button
        self.refresh_button = ttk.Button(
            header_frame, 
            text="🔄", 
            command=self._on_refresh_models
        )
        self.refresh_button.grid(row=0, column=2, padx=(5, 0))

        # Theme toggle button
        current_mode = self.app_instance.current_mode if self.app_instance else "dark"
        self.theme_button = ttk.Button(
            header_frame,
            text="☀️" if current_mode == "dark" else "🌙",
            command=self._toggle_theme,
            width=3
        )
        self.theme_button.grid(row=0, column=3, padx=(5, 0))

        # RAG/Documents button with indicator
        self.rag_enabled = tk.BooleanVar(value=True)  # RAG enabled by default
        self.rag_button = ttk.Button(
            header_frame,
            text="📄✓" if self.rag_enabled.get() else "📄✗",
            command=self._toggle_rag_mode,
            width=4
        )
        self.rag_button.grid(row=0, column=4, padx=(5, 0))
        
        # Documents management button
        self.docs_button = ttk.Button(
            header_frame,
            text="📁",
            command=self._show_document_management,
            width=3
        )
        self.docs_button.grid(row=0, column=5, padx=(5, 0))

        # Host label and input
        host_label = ttk.Label(
            header_frame, 
            text="Host:",
            font=self.body_font
        )
        host_label.grid(row=0, column=7, padx=(10, 5))

        self.host_input = ttk.Entry(
            header_frame, 
            width=24,
            font=self.body_font
        )
        self.host_input.grid(row=0, column=8, padx=(0, 0))
        self.host_input.insert(0, self.viewmodel.state.api_url)
        self.host_input.bind("<Return>", self._on_host_changed)
        self.host_input.bind("<FocusOut>", self._on_host_changed)
    
    def _create_chat_container_frame(self) -> None:
        """Create the chat display area with a scrollable text widget."""
        chat_frame = ttk.Frame(self.root)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        # Create a scrollable text widget
        self.chat_box = tk.Text(
            chat_frame,
            font=(self.default_font, 11),
            spacing1=8,
            spacing2=4,
            spacing3=8,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew")

        # Add vertical scrollbar
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_box.yview)
        chat_scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_box.configure(yscrollcommand=chat_scrollbar.set)

        # Context menu for chat box
        chat_box_menu = tk.Menu(self.chat_box, tearoff=0)
        chat_box_menu.add_command(label="Copy All", command=self._copy_all)
        chat_box_menu.add_separator()
        chat_box_menu.add_command(label="Clear Chat", command=self._clear_chat)

        self.chat_box.bind("<Configure>", self._resize_inner_text_widget)
        right_click = get_platform_right_click_event()
        self.chat_box.bind(right_click, lambda e: chat_box_menu.post(e.x_root, e.y_root))

        # Apply theme to context menu
        self.theme_manager.style_tk_widget(chat_box_menu, "menu")
    
    def _create_processbar_frame(self) -> None:
        """Create the progress bar area."""
        self.process_frame = ttk.Frame(self.root, height=40)
        self.process_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.process_frame.grid_columnconfigure(0, weight=1)

        # Create standard ttk progress bar
        self.progress = ttk.Progressbar(self.process_frame, mode="indeterminate")
        self.progress.grid(row=0, column=0, sticky="ew")

        self.stop_button = ttk.Button(
            self.process_frame,
            width=8,
            text="⏹ Stop",
            command=self._on_stop_processing
        )
    
    def _create_input_frame(self) -> None:
        """Create the enhanced user input area."""
        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)

        # Create input container with better styling
        input_container = ttk.Frame(input_frame)
        input_container.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        input_container.grid_columnconfigure(0, weight=1)

        self.user_input = tk.Text(
            input_container, 
            font=(self.default_font, 11), 
            height=4, 
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            highlightthickness=2,
            padx=12,
            pady=8
        )
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Key>", self._handle_key_press)
        
        # Apply theme to user input
        self.theme_manager.style_tk_widget(self.user_input, "text")

        # Enhanced send button
        self.send_button = ttk.Button(
            input_container,
            text="📤 Send",
            command=self._on_send_message
        )
        self.send_button.grid(row=0, column=1, sticky="ns")
        self.send_button.state(["disabled"])
    
    def _create_menu_bar(self) -> None:
        """Create the enhanced application menu bar."""
        # Find the root window (might be master's master in themed frames)
        root_window = self.root
        while hasattr(root_window, 'master') and root_window.master:
            root_window = root_window.master
        
        menubar = tk.Menu(root_window)
        root_window.config(menu=menubar)
        
        # Apply theme to menubar
        self.theme_manager.style_tk_widget(menubar, "menu")

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Model Management", command=self._show_model_management)
        file_menu.add_command(label="📄 Document Management (RAG)", command=self._show_document_management)
        file_menu.add_separator()
        file_menu.add_command(label="📊 RAG Statistics", command=self._show_rag_statistics)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root_window.quit)
        self.theme_manager.style_tk_widget(file_menu, "menu")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy All", command=self._copy_all)
        edit_menu.add_command(label="Clear Chat", command=self._clear_chat)
        self.theme_manager.style_tk_widget(edit_menu, "menu")

        # View menu with theme options
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Add theme submenu with restart functionality
        theme_submenu = self._create_theme_menu(view_menu)
        view_menu.add_cascade(label="🎨 Themes", menu=theme_submenu)
        
        view_menu.add_separator()
        current_mode = self.app_instance.current_mode if self.app_instance else "dark"
        next_mode = "Light" if current_mode == "dark" else "Dark"
        view_menu.add_command(
            label=f"Switch to {next_mode} Mode", 
            command=self._toggle_theme
        )
        
        # RAG settings submenu
        view_menu.add_separator()
        rag_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="📄 RAG Settings", menu=rag_menu)
        
        rag_menu.add_checkbutton(
            label="Enable RAG Context", 
            variable=self.rag_enabled,
            command=self._update_rag_button_from_menu
        )
        
        # Context preview toggle
        self.show_context_preview = tk.BooleanVar(value=False)
        rag_menu.add_checkbutton(
            label="Show Context Preview", 
            variable=self.show_context_preview
        )
        
        self.theme_manager.style_tk_widget(rag_menu, "menu")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Source Code", command=self._open_homepage)
        help_menu.add_command(label="Help", command=self._show_help)
        self.theme_manager.style_tk_widget(help_menu, "menu")
    
    def _configure_chat_box_tags(self) -> None:
        """Configure text tags for the chat box."""
        is_dark = self.theme_manager.is_dark_mode()
        
        # Use appropriate colors based on dark/light mode
        if is_dark:
            accent_color = '#60A5FA'    # Blue accent for dark mode
            error_color = '#F87171'     # Red for errors in dark mode
            success_color = '#34D399'   # Green for success in dark mode
        else:
            accent_color = '#3B82F6'    # Blue accent for light mode
            error_color = '#DC2626'     # Red for errors in light mode
            success_color = '#059669'   # Green for success in light mode
        
        self.chat_box.tag_configure(
            "Bold", 
            foreground=accent_color, 
            font=(self.default_font, 11, "bold")
        )
        self.chat_box.tag_configure("Error", foreground=error_color)
        self.chat_box.tag_configure("Success", foreground=success_color)
        self.chat_box.tag_configure("info", foreground=accent_color, font=(self.default_font, 10, "italic"))
        self.chat_box.tag_configure("rag_info", foreground=success_color, font=(self.default_font, 10, "bold"))
        self.chat_box.tag_configure("rag_warning", foreground=error_color, font=(self.default_font, 10, "italic"))
        self.chat_box.tag_configure("context_preview", foreground=accent_color, font=(self.default_font, 9, "italic"))
        self.chat_box.tag_configure("user", foreground=accent_color, font=(self.default_font, 11, "bold"))
        self.chat_box.tag_configure("Right", justify="right")
        self.chat_box.tag_configure("Center", justify="center")
    
    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes with application restart."""
        if not self.app_instance:
            # Fallback if no app instance available
            messagebox.showinfo(
                "Theme Change", 
                "Please restart the application manually to change themes."
            )
            return
        
        # Get current theme info from app instance
        current_theme = self.app_instance.current_theme
        current_mode = self.app_instance.current_mode
        
        # Toggle the mode
        new_mode = "light" if current_mode == "dark" else "dark"
        
        # Restart application with new theme
        self.app_instance.restart_with_theme(current_theme, new_mode)
    
    def _create_theme_menu(self, parent_menu) -> tk.Menu:
        """Create a theme submenu that works with app restart."""
        theme_menu = tk.Menu(parent_menu, tearoff=0)
        
        # Available themes with proper names
        themes = [
            ("park", "Park (Excel-style)"),
            ("sun-valley", "Sun Valley (Windows 11)"),
            ("azure", "Azure (Blue accents)")
        ]
        
        # Create submenus for dark and light themes
        dark_menu = tk.Menu(theme_menu, tearoff=0)
        light_menu = tk.Menu(theme_menu, tearoff=0)
        
        # Add dark themes
        for theme_key, theme_name in themes:
            dark_menu.add_command(
                label=theme_name,
                command=lambda t=theme_key: self._change_theme_with_restart(t, "dark")
            )
        
        # Add light themes
        for theme_key, theme_name in themes:
            light_menu.add_command(
                label=theme_name,
                command=lambda t=theme_key: self._change_theme_with_restart(t, "light")
            )
        
        # Add submenus
        theme_menu.add_cascade(label="🌙 Dark Themes", menu=dark_menu)
        theme_menu.add_cascade(label="☀️ Light Themes", menu=light_menu)
        
        # Style the menus
        self.theme_manager.style_tk_widget(theme_menu, "menu")
        self.theme_manager.style_tk_widget(dark_menu, "menu")
        self.theme_manager.style_tk_widget(light_menu, "menu")
        
        return theme_menu
    
    def _change_theme_with_restart(self, theme: str, mode: str):
        """Change to a specific theme with restart."""
        if self.app_instance:
            self.app_instance.restart_with_theme(theme, mode)
        else:
            messagebox.showinfo(
                "Theme Change", 
                f"Please restart the application manually to apply {theme} {mode} theme."
            )
    
    def _update_menu_labels(self) -> None:
        """Update menu labels after theme change."""
        try:
            menubar = self.root['menu']
            if menubar:
                # Find and update view menu
                for i in range(menubar.index('end') + 1):
                    try:
                        menu_label = menubar.entrycget(i, 'label')
                        if menu_label == "View":
                            view_menu = menubar.nametowidget(menubar.entrycget(i, 'menu'))
                            # Update the toggle menu item (should be the last one after separator)
                            try:
                                view_menu.entryconfig(
                                    'end', 
                                    label=f"Switch to {'Light' if self.theme_manager.is_dark_mode() else 'Dark'} Mode"
                                )
                            except tk.TclError:
                                pass
                            break
                    except (tk.TclError, AttributeError):
                        continue
        except (tk.TclError, AttributeError):
            pass
    
    # Event handlers
    def _on_model_selected(self, event=None) -> None:
        """Handle model selection change."""
        if self.model_select:
            selected_model = self.model_select.get()
            self.viewmodel.set_current_model(selected_model)
    
    def _on_refresh_models(self) -> None:
        """Handle refresh models button click."""
        self._update_host()
        self.viewmodel.refresh_models()
        if self.refresh_button:
            self.refresh_button.state(["disabled"])
    
    def _on_host_changed(self, event=None) -> None:
        """Handle host input change."""
        self._update_host()
    
    def _update_host(self) -> None:
        """Update the API host URL."""
        if self.host_input:
            new_url = self.host_input.get()
            self.viewmodel.update_api_url(new_url)
    
    def _handle_key_press(self, event: tk.Event) -> str:
        """Handle key press in user input area."""
        if event.keysym == "Return":
            if event.state & 0x1 == 0x1:  # Shift key is pressed
                self.user_input.insert("end", "\n")
            elif self.send_button and "disabled" not in self.send_button.state():
                self._on_send_message()
            return "break"
        return ""
    
    def _on_send_message(self) -> None:
        """Handle send message button click with enhanced RAG context integration."""
        if not self.user_input:
            return
        
        message = self.user_input.get("1.0", "end-1c")
        if not message.strip():
            return
            
        # Clear input immediately
        self.user_input.delete("1.0", "end")
        
        # Show user message in chat first
        self._append_text_to_chat(f"You: {message}\n", "user")
        
        # Check if RAG is enabled and we have documents
        if (self.rag_enabled.get() and 
            self.document_management_view and 
            self.document_management_view.has_documents()):
            
            # Get relevant context from documents with details
            search_results = self.document_management_view.search_documents_with_details(message)
            
            if search_results:
                # Show RAG indicator with source info
                source_files = list(set([r['filename'] for r in search_results]))
                sources_text = ", ".join(source_files)
                
                self._append_text_to_chat(
                    f"📄 RAG Context: Found {len(search_results)} relevant chunks from: {sources_text}\n", 
                    "rag_info"
                )
                
                # Create enhanced message with context and source citations
                context_parts = []
                for i, result in enumerate(search_results, 1):
                    context_parts.append(
                        f"[Source {i}: {result['filename']} - Relevance: {result['relevance']:.2f}]\n"
                        f"{result['text']}"
                    )
                
                context = "\n\n".join(context_parts)
                
                enhanced_message = f"""[SYSTEM: You are provided with relevant context from the user's uploaded documents. Please use this information to answer their question accurately. If the context doesn't contain relevant information, say so clearly.]

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

USER QUESTION: {message}

Please answer the user's question using the provided context when relevant. If you use information from the context, mention which source(s) you're referencing."""
                
                # Show context preview (optional - can be toggled)
                if hasattr(self, 'show_context_preview') and self.show_context_preview:
                    self._append_text_to_chat(f"Context preview (first 200 chars): {context[:200]}...\n", "context_preview")
                
            else:
                self._append_text_to_chat(
                    f"📄 RAG: No relevant context found in uploaded documents for this query\n", 
                    "rag_warning"
                )
                enhanced_message = message
        else:
            if not self.rag_enabled.get():
                enhanced_message = message
            else:
                self._append_text_to_chat(
                    f"📄 RAG: No documents uploaded. Upload documents to enable context-aware responses.\n", 
                    "rag_warning"
                )
                enhanced_message = message
        
        # Send the message to the model
        self.viewmodel.send_message(enhanced_message)
    
    def _on_stop_processing(self) -> None:
        """Handle stop processing button click."""
        if self.stop_button:
            self.stop_button.state(["disabled"])
    
    def _show_model_management(self) -> None:
        """Show the model management window."""
        if not self.model_management_view or not self.model_management_view.window.winfo_exists():
            self.model_management_view = ModelManagementView(
                self.root, self.viewmodel.api_service
            )
        else:
            self.model_management_view.window.lift()
    
    def _show_document_management(self) -> None:
        """Show the document management window for RAG functionality."""
        if not self.document_management_view:
            self.document_management_view = DocumentManagementView(self.root)
        self.document_management_view.show_window()
    
    def _toggle_rag_mode(self) -> None:
        """Toggle RAG functionality on/off."""
        self.rag_enabled.set(not self.rag_enabled.get())
        
        # Update button appearance
        if self.rag_enabled.get():
            self.rag_button.configure(text="📄✓")
            status_msg = "📄 RAG Mode: ENABLED - Documents will be used as context"
        else:
            self.rag_button.configure(text="📄✗")
            status_msg = "📄 RAG Mode: DISABLED - Documents will NOT be used"
        
        # Show status in chat
        self._append_text_to_chat(f"{status_msg}\n", "info")
    
    def _update_rag_button_from_menu(self) -> None:
        """Update RAG button when toggled from menu."""
        if self.rag_enabled.get():
            self.rag_button.configure(text="📄✓")
        else:
            self.rag_button.configure(text="📄✗")
    
    def _show_rag_statistics(self) -> None:
        """Show RAG system statistics and status."""
        if not self.document_management_view:
            self.document_management_view = DocumentManagementView(self.root)
        
        docs = self.document_management_view.list_documents() if hasattr(self.document_management_view, 'list_documents') else []
        doc_count = len(docs) if docs else len(document_store.list_documents())
        
        total_words = sum(doc.get('word_count', 0) for doc in document_store.list_documents())
        
        stats_msg = f"""📊 RAG System Status:
• Status: {'ENABLED' if self.rag_enabled.get() else 'DISABLED'}
• Documents: {doc_count} uploaded
• Total Words: {total_words:,}
• Context Preview: {'ON' if getattr(self, 'show_context_preview', False) and self.show_context_preview.get() else 'OFF'}
• Storage: {document_store.storage_dir}

💡 Tip: When RAG is enabled, your questions will be answered using context from uploaded documents when relevant."""
        
        messagebox.showinfo("RAG Statistics", stats_msg)
    
    def _copy_all(self) -> None:
        """Copy all chat history to clipboard."""
        history = self.viewmodel.get_chat_history_copy()
        formatted_history = pprint.pformat(history)
        self._copy_text(formatted_history)
    
    def _copy_text(self, text: str) -> None:
        """Copy text to clipboard."""
        if text and self.chat_box:
            self.chat_box.clipboard_clear()
            self.chat_box.clipboard_append(text)
    
    def _clear_chat(self) -> None:
        """Clear the chat display and history."""
        self.viewmodel.clear_chat()
    
    def _open_homepage(self) -> None:
        """Open the project homepage."""
        webbrowser.open("https://github.com/chyok/ollama-gui")
    
    def _show_help(self) -> None:
        """Show the help dialog."""
        info = ("Project: Ollama GUI\n"
                "Version: 1.2.1\n"
                "Author: chyok\n"
                "Github: https://github.com/chyok/ollama-gui\n\n"
                "<Enter>: send\n"
                "<Shift+Enter>: new line\n"
                "<Double click dialog>: edit dialog\n")
        messagebox.showinfo("About", info, parent=self.root)
    
    def _check_system(self) -> None:
        """Check for system compatibility issues."""
        self.root.after(200, self._perform_system_check)
    
    def _perform_system_check(self) -> None:
        """Perform the actual system check."""
        message = system_check(self.root)
        if message:
            messagebox.showwarning("Warning", message, parent=self.root)
    
    # ViewModel callback handlers
    def _on_models_updated(self, models: List[Model]) -> None:
        """Handle models list update from viewmodel."""
        if not self.model_select:
            return
        
        model_names = [model.name for model in models]
        self.model_select["values"] = model_names
        self.model_select.config(foreground="black")
        
        if models:
            self.model_select.set(models[0].name)
            if self.send_button:
                self.send_button.state(["!disabled"])
        else:
            self._show_error("You need to download a model!")
        
        if self.refresh_button:
            self.refresh_button.state(["!disabled"])
    
    def _on_model_error(self, error: str) -> None:
        """Handle model loading error from viewmodel."""
        self._show_error("Error! Please check the host.")
        if self.refresh_button:
            self.refresh_button.state(["!disabled"])
    
    def _show_error(self, text: str) -> None:
        """Show error message in model selector."""
        if self.model_select:
            self.model_select.set(text)
            self.model_select.config(foreground="red")
            self.model_select["values"] = []
        if self.send_button:
            self.send_button.state(["disabled"])
    
    def _on_message_added(self, message: ChatMessage) -> None:
        """Handle new message added to chat."""
        if message.role == "user":
            self._create_inner_label(on_right_side=True)
            self._append_text_to_chat(message.content, use_label=True)
            self._append_text_to_chat("\n\n")
    
    def _on_chat_response_chunk(self, chunk: str) -> None:
        """Handle streaming chat response chunk."""
        self._append_text_to_chat(chunk, use_label=True)
    
    def _on_chat_response_complete(self, response: str) -> None:
        """Handle complete chat response."""
        self._append_text_to_chat("\n\n")
    
    def _on_chat_error(self, error: str) -> None:
        """Handle chat error."""
        self._append_text_to_chat("\nAI error!\n\n", ("Error",))
    
    def _on_processing_started(self) -> None:
        """Handle processing started."""
        self._show_process_bar()
        if self.send_button:
            self.send_button.state(["disabled"])
        if self.refresh_button:
            self.refresh_button.state(["disabled"])
        
        # Show model name before response
        current_model = self.viewmodel.get_current_model()
        if current_model:
            self._append_text_to_chat(f"{current_model}\n", ("Bold",))
            self._create_inner_label()
    
    def _on_processing_finished(self) -> None:
        """Handle processing finished."""
        self._hide_process_bar()
        if self.send_button:
            self.send_button.state(["!disabled"])
        if self.refresh_button:
            self.refresh_button.state(["!disabled"])
        if self.stop_button:
            self.stop_button.state(["!disabled"])
    
    def _on_chat_cleared(self) -> None:
        """Handle chat cleared."""
        for label in self.label_widgets:
            label.destroy()
        self.label_widgets.clear()
        
        if self.chat_box:
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.delete(1.0, tk.END)
            self.chat_box.config(state=tk.DISABLED)
    
    # UI Helper methods
    def _show_process_bar(self) -> None:
        """Show the enhanced progress bar."""
        if self.progress and self.stop_button:
            self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.stop_button.grid(row=0, column=1, sticky="ns")
            self.progress.start(8)  # Slightly faster animation
    
    def _hide_process_bar(self) -> None:
        """Hide the enhanced progress bar."""
        if self.progress and self.stop_button:
            self.progress.stop()
            self.stop_button.grid_remove()
            self.progress.grid_remove()
    
    def _append_text_to_chat(self, text: str, *args, use_label: bool = False) -> None:
        """Append text to the chat display."""
        if not self.chat_box:
            return
        
        self.chat_box.config(state=tk.NORMAL)
        if use_label and self.label_widgets:
            cur_label_widget = self.label_widgets[-1]
            cur_label_widget.config(text=cur_label_widget.cget("text") + text)
        else:
            self.chat_box.insert(tk.END, text, *args)
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)
    
    def _resize_inner_text_widget(self, event: tk.Event) -> None:
        """Resize inner text widgets when chat box is resized."""
        current_width = event.widget.winfo_width()
        max_width = int(current_width) * 0.7
        for label in self.label_widgets:
            label.config(wraplength=max_width)
    
    def _create_inner_label(self, on_right_side: bool = False) -> None:
        """Create a new enhanced label for chat messages."""
        if not self.chat_box:
            return
        
        # Get current theme colors for styling
        bubble_colors = self.theme_manager.get_chat_bubble_colors(on_right_side)
        max_width = int(self.chat_box.winfo_reqwidth()) * 0.65
        
        inner_label = tk.Label(
            self.chat_box,
            justify=tk.LEFT,
            wraplength=max_width,
            font=(self.default_font, 11),
            bg=bubble_colors['bg'],
            fg=bubble_colors['fg'],
            relief=bubble_colors['relief'],
            borderwidth=bubble_colors['borderwidth'],
            padx=12,
            pady=8
        )
        self.label_widgets.append(inner_label)

        # Enhanced mouse interactions
        inner_label.bind(
            "<MouseWheel>",
            lambda e: self.chat_box.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )
        inner_label.bind("<Double-1>", lambda e: self._show_editor_window(inner_label))

        # Enhanced context menu with theme support
        right_menu = tk.Menu(inner_label, tearoff=0)
        right_menu.add_command(
            label="✏️ Edit", command=lambda: self._show_editor_window(inner_label)
        )
        right_menu.add_command(
            label="📋 Copy This", command=lambda: self._copy_text(inner_label.cget("text"))
        )
        right_menu.add_separator()
        right_menu.add_command(label="🗑️ Clear Chat", command=self._clear_chat)
        
        # Apply theme to context menu
        self.theme_manager.style_tk_widget(right_menu, "menu")
        
        right_click = get_platform_right_click_event()
        inner_label.bind(right_click, lambda e: right_menu.post(e.x_root, e.y_root))
        
        self.chat_box.window_create(tk.END, window=inner_label)
        
        if on_right_side:
            idx = self.chat_box.index("end-1c").split(".")[0]
            self.chat_box.tag_add("Right", f"{idx}.0", f"{idx}.end")
    
    def _show_editor_window(self, inner_label: tk.Label) -> None:
        """Show the enhanced message editor window."""
        if self.editor_window and self.editor_window.winfo_exists():
            self.editor_window.lift()
            return

        self.editor_window = tk.Toplevel(self.root)
        self.editor_window.title("✏️ Edit Message")
        
        # Apply basic theme styling to editor window
        if self.theme_manager.is_dark_mode():
            self.editor_window.configure(bg='#2D2D2D')
        else:
            self.editor_window.configure(bg='#FFFFFF')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (450 / 2))
        y = int((screen_height / 2) - (350 / 2))
        self.editor_window.geometry(f"450x350+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(self.editor_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Editor text widget with enhanced styling
        chat_editor = tk.Text(
            main_frame,
            font=(self.default_font, 11),
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
            highlightthickness=2,
            padx=12,
            pady=12
        )
        chat_editor.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        chat_editor.insert(tk.END, inner_label.cget("text"))
        
        # Apply theme to editor
        self.theme_manager.style_tk_widget(chat_editor, "text")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        def save_edit():
            try:
                idx = self.label_widgets.index(inner_label)
                if len(self.viewmodel.state.chat_session.messages) > idx:
                    new_content = chat_editor.get("1.0", "end-1c")
                    self.viewmodel.state.chat_session.messages[idx].content = new_content
                    inner_label.config(text=new_content)
            except (ValueError, IndexError):
                pass
            self.editor_window.destroy()

        # Enhanced buttons
        save_button = ttk.Button(
            button_frame, 
            text="💾 Save", 
            command=save_edit
        )
        save_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        cancel_button = ttk.Button(
            button_frame, 
            text="❌ Cancel", 
            command=self.editor_window.destroy
        )
        cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Focus on editor
        chat_editor.focus_set()
        chat_editor.mark_set(tk.INSERT, "1.0")
        chat_editor.see(tk.INSERT)
