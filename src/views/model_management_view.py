"""
Model management view for downloading and deleting Ollama models.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from threading import Thread
from typing import List, Optional
from ..models.chat_models import Model
from ..services.ollama_service import OllamaApiService
from ..viewmodels.model_management_viewmodel import ModelManagementViewModel


class ModelManagementView:
    """View for managing Ollama models."""
    
    def __init__(self, parent: tk.Tk, api_service: OllamaApiService):
        self.parent = parent
        self.viewmodel = ModelManagementViewModel(api_service)
        self.window: Optional[tk.Toplevel] = None
        
        # UI Components
        self.model_name_input: Optional[ttk.Entry] = None
        self.download_button: Optional[ttk.Button] = None
        self.delete_button: Optional[ttk.Button] = None
        self.models_list: Optional[tk.Listbox] = None
        self.log_textbox: Optional[tk.Text] = None
        
        self._setup_viewmodel_callbacks()
        self._create_window()
        self.viewmodel.refresh_models()
    
    def _setup_viewmodel_callbacks(self) -> None:
        """Setup callbacks between viewmodel and view."""
        self.viewmodel.on_models_updated = self._on_models_updated
        self.viewmodel.on_download_progress = self._on_download_progress
        self.viewmodel.on_download_complete = self._on_download_complete
        self.viewmodel.on_download_error = self._on_download_error
        self.viewmodel.on_delete_complete = self._on_delete_complete
        self.viewmodel.on_delete_error = self._on_delete_error
        self.viewmodel.on_operation_started = self._on_operation_started
        self.viewmodel.on_operation_finished = self._on_operation_finished
    
    def _create_window(self) -> None:
        """Create the model management window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Model Management")
        
        # Center the window
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = int((screen_width / 2) - (400 / 2))
        y = int((screen_height / 2) - (500 / 2))
        self.window.geometry(f"400x500+{x}+{y}")
        
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        
        self._create_download_frame()
        self._create_models_list_frame()
        self._create_log_frame()
    
    def _create_download_frame(self) -> None:
        """Create the model download input frame."""
        frame = ttk.Frame(self.window)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)

        self.model_name_input = ttk.Entry(frame)
        self.model_name_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.model_name_input.bind("<Return>", lambda e: self._download_model())

        self.download_button = ttk.Button(frame, text="Download", command=self._download_model)
        self.download_button.grid(row=0, column=1, sticky="ew")

        tips = tk.Label(
            frame,
            text="find models: https://ollama.com/library",
            fg="blue",
            cursor="hand2",
        )
        tips.bind("<Button-1>", lambda e: webbrowser.open("https://ollama.com/library"))
        tips.grid(row=1, column=0, sticky="W", padx=(0, 5), pady=5)
    
    def _create_models_list_frame(self) -> None:
        """Create the models list and delete button frame."""
        list_frame = ttk.Frame(self.window)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self.models_list = tk.Listbox(list_frame)
        self.models_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.models_list.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.models_list.config(yscrollcommand=scrollbar.set)

        self.delete_button = ttk.Button(
            list_frame, text="Delete", command=self._delete_model
        )
        self.delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
    
    def _create_log_frame(self) -> None:
        """Create the log output frame."""
        self.log_textbox = tk.Text(self.window)
        self.log_textbox.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_textbox.config(state="disabled")
    
    def _download_model(self) -> None:
        """Handle download model button click."""
        if not self.model_name_input:
            return
        
        model_name = self.model_name_input.get().strip()
        if model_name:
            self._clear_log()
            self.viewmodel.download_model(model_name)
    
    def _delete_model(self) -> None:
        """Handle delete model button click."""
        if not self.models_list:
            return
        
        try:
            selected_model = self.models_list.get(tk.ACTIVE).strip()
            if selected_model:
                self._clear_log()
                self.viewmodel.delete_model(selected_model)
        except tk.TclError:
            pass  # No selection
    
    def _clear_log(self) -> None:
        """Clear the log textbox."""
        if self.log_textbox:
            self.log_textbox.config(state=tk.NORMAL)
            self.log_textbox.delete(1.0, tk.END)
            self.log_textbox.config(state=tk.DISABLED)
    
    def _append_log(self, message: str) -> None:
        """Append a message to the log."""
        if self.log_textbox and self.log_textbox.winfo_exists():
            self.log_textbox.config(state=tk.NORMAL)
            self.log_textbox.insert(tk.END, message + "\n")
            self.log_textbox.config(state=tk.DISABLED)
            self.log_textbox.see(tk.END)
    
    # ViewModel callback handlers
    def _on_models_updated(self, models: List[Model]) -> None:
        """Handle models list update from viewmodel."""
        if not self.models_list or not self.models_list.winfo_exists():
            return
        
        self.models_list.delete(0, tk.END)
        for model in models:
            self.models_list.insert(tk.END, model.name)
    
    def _on_download_progress(self, message: str) -> None:
        """Handle download progress update."""
        self._append_log(message)
    
    def _on_download_complete(self, message: str) -> None:
        """Handle download completion."""
        self._append_log(message)
    
    def _on_download_error(self, error: str) -> None:
        """Handle download error."""
        self._append_log(f"Error: {error}")
    
    def _on_delete_complete(self, message: str) -> None:
        """Handle delete completion."""
        self._append_log(message)
    
    def _on_delete_error(self, error: str) -> None:
        """Handle delete error."""
        self._append_log(f"Error: {error}")
    
    def _on_operation_started(self) -> None:
        """Handle operation start."""
        if self.download_button:
            self.download_button.state(["disabled"])
    
    def _on_operation_finished(self) -> None:
        """Handle operation finish."""
        if self.download_button and self.download_button.winfo_exists():
            self.download_button.state(["!disabled"])
