"""
Main view for the Ollama GUI application.
This module contains the main window and chat interface.
"""

import tkinter as tk
from tkinter import ttk, font, messagebox
import webbrowser
import pprint
from typing import List, Optional
from ..models.chat_models import Model, ChatMessage
from ..viewmodels.chat_viewmodel import ChatViewModel
from ..utils.system_utils import system_check, get_platform_right_click_event
from .model_management_view import ModelManagementView


class MainView:
    """Main application window and chat interface."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.viewmodel = ChatViewModel()
        self.default_font = font.nametofont("TkTextFont").actual()["family"]
        self.label_widgets: List[tk.Label] = []
        self.model_management_view: Optional[ModelManagementView] = None
        self.editor_window: Optional[tk.Toplevel] = None
        
        # UI Components
        self.chat_box: Optional[tk.Text] = None
        self.user_input: Optional[tk.Text] = None
        self.host_input: Optional[ttk.Entry] = None
        self.progress: Optional[ttk.Progressbar] = None
        self.stop_button: Optional[ttk.Button] = None
        self.send_button: Optional[ttk.Button] = None
        self.refresh_button: Optional[ttk.Button] = None
        self.model_select: Optional[ttk.Combobox] = None
        
        self._setup_viewmodel_callbacks()
        self._init_layout()
        self._check_system()
        self.viewmodel.refresh_models()
    
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
        """Create the header with model selection and host input."""
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(3, weight=1)

        self.model_select = ttk.Combobox(header_frame, state="readonly", width=30)
        self.model_select.grid(row=0, column=0)
        self.model_select.bind("<<ComboboxSelected>>", self._on_model_selected)

        settings_button = ttk.Button(
            header_frame, text="⚙️", command=self._show_model_management, width=3
        )
        settings_button.grid(row=0, column=1, padx=(5, 0))

        self.refresh_button = ttk.Button(
            header_frame, text="Refresh", command=self._on_refresh_models
        )
        self.refresh_button.grid(row=0, column=2, padx=(5, 0))

        ttk.Label(header_frame, text="Host:").grid(row=0, column=4, padx=(10, 0))

        self.host_input = ttk.Entry(header_frame, width=24)
        self.host_input.grid(row=0, column=5, padx=(5, 15))
        self.host_input.insert(0, self.viewmodel.state.api_url)
        self.host_input.bind("<Return>", self._on_host_changed)
        self.host_input.bind("<FocusOut>", self._on_host_changed)
    
    def _create_chat_container_frame(self) -> None:
        """Create the chat display area."""
        chat_frame = ttk.Frame(self.root)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        self.chat_box = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=(self.default_font, 12),
            spacing1=5,
            highlightthickness=0,
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_box.configure(yscrollcommand=scrollbar.set)

        # Context menu for chat box
        chat_box_menu = tk.Menu(self.chat_box, tearoff=0)
        chat_box_menu.add_command(label="Copy All", command=self._copy_all)
        chat_box_menu.add_separator()
        chat_box_menu.add_command(label="Clear Chat", command=self._clear_chat)
        
        self.chat_box.bind("<Configure>", self._resize_inner_text_widget)
        right_click = get_platform_right_click_event()
        self.chat_box.bind(right_click, lambda e: chat_box_menu.post(e.x_root, e.y_root))
    
    def _create_processbar_frame(self) -> None:
        """Create the progress bar area."""
        process_frame = ttk.Frame(self.root, height=28)
        process_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.progress = ttk.Progressbar(
            process_frame,
            mode="indeterminate",
            style="LoadingBar.Horizontal.TProgressbar",
        )

        self.stop_button = ttk.Button(
            process_frame,
            width=5,
            text="Stop",
            command=self._on_stop_processing,
        )
    
    def _create_input_frame(self) -> None:
        """Create the user input area."""
        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = tk.Text(
            input_frame, font=(self.default_font, 12), height=4, wrap=tk.WORD
        )
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Key>", self._handle_key_press)

        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self._on_send_message,
        )
        self.send_button.grid(row=0, column=1)
        self.send_button.state(["disabled"])
    
    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Model Management", command=self._show_model_management)
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy All", command=self._copy_all)
        edit_menu.add_command(label="Clear Chat", command=self._clear_chat)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Source Code", command=self._open_homepage)
        help_menu.add_command(label="Help", command=self._show_help)
    
    def _configure_chat_box_tags(self) -> None:
        """Configure text tags for the chat box."""
        self.chat_box.tag_configure(
            "Bold", foreground="#ff007b", font=(self.default_font, 10, "bold")
        )
        self.chat_box.tag_configure("Error", foreground="red")
        self.chat_box.tag_configure("Right", justify="right")
    
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
        """Handle send message button click."""
        if not self.user_input:
            return
        
        message = self.user_input.get("1.0", "end-1c")
        if message.strip():
            self.user_input.delete("1.0", "end")
            self.viewmodel.send_message(message)
    
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
        """Show the progress bar."""
        if self.progress and self.stop_button:
            self.progress.grid(row=0, column=0, sticky="nsew")
            self.stop_button.grid(row=0, column=1, padx=20)
            self.progress.start(5)
    
    def _hide_process_bar(self) -> None:
        """Hide the progress bar."""
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
        """Create a new label for chat messages."""
        if not self.chat_box:
            return
        
        background = "#48a4f2" if on_right_side else "#eaeaea"
        foreground = "white" if on_right_side else "black"
        max_width = int(self.chat_box.winfo_reqwidth()) * 0.7
        
        inner_label = tk.Label(
            self.chat_box,
            justify=tk.LEFT,
            wraplength=max_width,
            background=background,
            highlightthickness=0,
            highlightbackground=background,
            foreground=foreground,
            padx=8,
            pady=8,
            font=(self.default_font, 12),
            borderwidth=0,
        )
        self.label_widgets.append(inner_label)

        # Mouse wheel scrolling
        inner_label.bind(
            "<MouseWheel>",
            lambda e: self.chat_box.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )
        
        # Double-click to edit
        inner_label.bind("<Double-1>", lambda e: self._show_editor_window(inner_label))

        # Context menu
        right_menu = tk.Menu(inner_label, tearoff=0)
        right_menu.add_command(
            label="Edit", command=lambda: self._show_editor_window(inner_label)
        )
        right_menu.add_command(
            label="Copy This", command=lambda: self._copy_text(inner_label.cget("text"))
        )
        right_menu.add_separator()
        right_menu.add_command(label="Clear Chat", command=self._clear_chat)
        
        right_click = get_platform_right_click_event()
        inner_label.bind(right_click, lambda e: right_menu.post(e.x_root, e.y_root))
        
        self.chat_box.window_create(tk.END, window=inner_label)
        
        if on_right_side:
            idx = self.chat_box.index("end-1c").split(".")[0]
            self.chat_box.tag_add("Right", f"{idx}.0", f"{idx}.end")
    
    def _show_editor_window(self, inner_label: tk.Label) -> None:
        """Show the message editor window."""
        if self.editor_window and self.editor_window.winfo_exists():
            self.editor_window.lift()
            return

        self.editor_window = tk.Toplevel(self.root)
        self.editor_window.title("Chat Editor")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (400 / 2))
        y = int((screen_height / 2) - (300 / 2))
        self.editor_window.geometry(f"{400}x{300}+{x}+{y}")

        chat_editor = tk.Text(self.editor_window)
        chat_editor.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        chat_editor.insert(tk.END, inner_label.cget("text"))

        self.editor_window.grid_rowconfigure(0, weight=1)
        self.editor_window.grid_columnconfigure(0, weight=1)
        self.editor_window.grid_columnconfigure(1, weight=1)

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

        save_button = tk.Button(self.editor_window, text="Save", command=save_edit)
        save_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        cancel_button = tk.Button(
            self.editor_window, text="Cancel", command=self.editor_window.destroy
        )
        cancel_button.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.editor_window.grid_columnconfigure(0, weight=1, uniform="btn")
        self.editor_window.grid_columnconfigure(1, weight=1, uniform="btn")
