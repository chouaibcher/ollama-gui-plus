"""
ViewModel for the main chat interface.
This layer handles the business logic and state management between the View and Model.
"""

import time
from threading import Thread
from typing import List, Callable, Optional, Dict, Any
from ..models.chat_models import ApplicationState, Model, ChatMessage
from ..services.ollama_service import OllamaApiService


class ChatViewModel:
    """ViewModel for managing chat functionality."""
    
    def __init__(self):
        self.state = ApplicationState()
        self.api_service = OllamaApiService(self.state.api_url)
        
        # Event callbacks for the view
        self.on_models_updated: Optional[Callable[[List[Model]], None]] = None
        self.on_model_error: Optional[Callable[[str], None]] = None
        self.on_chat_response_chunk: Optional[Callable[[str], None]] = None
        self.on_chat_response_complete: Optional[Callable[[str], None]] = None
        self.on_chat_error: Optional[Callable[[str], None]] = None
        self.on_processing_started: Optional[Callable[[], None]] = None
        self.on_processing_finished: Optional[Callable[[], None]] = None
        self.on_message_added: Optional[Callable[[ChatMessage], None]] = None
        self.on_chat_cleared: Optional[Callable[[], None]] = None
    
    def update_api_url(self, url: str) -> None:
        """Update the API URL and refresh models."""
        self.state.api_url = url
        self.api_service.set_api_url(url)
    
    def refresh_models(self) -> None:
        """Refresh the list of available models asynchronously."""
        Thread(target=self._fetch_models_async, daemon=True).start()
    
    def _fetch_models_async(self) -> None:
        """Fetch models in a background thread."""
        try:
            models = self.api_service.fetch_models()
            self.state.available_models = models
            
            if self.on_models_updated:
                self.on_models_updated(models)
                
            # Set the first model as current if none is selected
            if models and not self.state.current_model:
                self.set_current_model(models[0].name)
                
        except Exception as e:
            if self.on_model_error:
                self.on_model_error(str(e))
    
    def set_current_model(self, model_name: str) -> None:
        """Set the current model for chat."""
        self.state.set_current_model(model_name)
    
    def send_message(self, content: str) -> None:
        """Send a user message and get AI response."""
        if not content.strip() or not self.state.current_model:
            return
        
        # Add user message
        self.state.chat_session.add_message("user", content)
        user_message = self.state.chat_session.messages[-1]
        
        if self.on_message_added:
            self.on_message_added(user_message)
        
        # Start AI response in background
        Thread(target=self._generate_ai_response_async, daemon=True).start()
    
    def _generate_ai_response_async(self) -> None:
        """Generate AI response in a background thread."""
        if not self.state.current_model:
            return
        
        self.state.is_processing = True
        if self.on_processing_started:
            self.on_processing_started()
        
        try:
            ai_response = ""
            messages = self.state.chat_session.get_api_messages()
            
            for chunk in self.api_service.chat_stream(self.state.current_model, messages):
                ai_response += chunk
                if self.on_chat_response_chunk:
                    self.on_chat_response_chunk(chunk)
                time.sleep(0.01)  # Small delay for UI responsiveness
            
            # Add AI message to history
            self.state.chat_session.add_message("assistant", ai_response)
            ai_message = self.state.chat_session.messages[-1]
            
            if self.on_chat_response_complete:
                self.on_chat_response_complete(ai_response)
                
        except Exception as e:
            if self.on_chat_error:
                self.on_chat_error(str(e))
        finally:
            self.state.is_processing = False
            if self.on_processing_finished:
                self.on_processing_finished()
    
    def clear_chat(self) -> None:
        """Clear the chat history."""
        self.state.chat_session.clear_messages()
        if self.on_chat_cleared:
            self.on_chat_cleared()
    
    def get_chat_history_copy(self) -> List[Dict[str, Any]]:
        """Get a copy of the chat history for export."""
        return [message.to_dict() for message in self.state.chat_session.messages]
    
    def get_available_models(self) -> List[Model]:
        """Get the list of available models."""
        return self.state.available_models
    
    def get_current_model(self) -> Optional[str]:
        """Get the current model name."""
        return self.state.current_model
    
    def is_processing(self) -> bool:
        """Check if the system is currently processing a request."""
        return self.state.is_processing
