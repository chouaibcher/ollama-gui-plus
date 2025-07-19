"""
Models for the Ollama GUI application.
This module contains the data models used throughout the application.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for API calls."""
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class Model:
    """Represents an Ollama model."""
    name: str
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return self.name


@dataclass
class ChatSession:
    """Represents a chat session with message history."""
    messages: List[ChatMessage] = field(default_factory=list)
    current_model: Optional[str] = None
    
    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the session."""
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
    
    def clear_messages(self) -> None:
        """Clear all messages from the session."""
        self.messages.clear()
    
    def get_api_messages(self) -> List[Dict[str, Any]]:
        """Get messages in the format expected by the API."""
        return [message.to_dict() for message in self.messages]


@dataclass
class ApplicationState:
    """Represents the overall application state."""
    api_url: str = "http://127.0.0.1:11434"
    available_models: List[Model] = field(default_factory=list)
    chat_session: ChatSession = field(default_factory=ChatSession)
    is_processing: bool = False
    current_model: Optional[str] = None
    
    def set_current_model(self, model_name: str) -> None:
        """Set the current model for the chat session."""
        self.current_model = model_name
        self.chat_session.current_model = model_name
