"""
Ollama API service for handling communication with the Ollama server.
"""

import json
import urllib.parse
import urllib.request
from typing import List, Generator, Dict, Any
from ..models.chat_models import Model, ChatMessage


class OllamaApiService:
    """Service for interacting with the Ollama API."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:11434"):
        self.api_url = api_url
    
    def set_api_url(self, url: str) -> None:
        """Update the API URL."""
        self.api_url = url
    
    def fetch_models(self) -> List[Model]:
        """Fetch available models from the Ollama API."""
        try:
            with urllib.request.urlopen(
                urllib.parse.urljoin(self.api_url, "/api/tags")
            ) as response:
                data = json.load(response)
                models = []
                for model_data in data["models"]:
                    model = Model(
                        name=model_data["name"],
                        size=model_data.get("size"),
                    )
                    models.append(model)
                return models
        except Exception as e:
            raise ConnectionError(f"Failed to fetch models: {e}")
    
    def chat_stream(self, model: str, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Send a chat request and yield streaming responses."""
        request_data = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        
        request = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/chat"),
            data=json.dumps(request_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        try:
            with urllib.request.urlopen(request) as response:
                for line in response:
                    data = json.loads(line.decode("utf-8"))
                    if "message" in data:
                        yield data["message"]["content"]
        except Exception as e:
            raise ConnectionError(f"Failed to get chat response: {e}")
    
    def pull_model(self, model_name: str, insecure: bool = False) -> Generator[Dict[str, Any], None, None]:
        """Pull/download a model and yield progress updates."""
        request_data = {
            "name": model_name,
            "insecure": insecure,
            "stream": True
        }
        
        request = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/pull"),
            data=json.dumps(request_data).encode("utf-8"),
            method="POST",
        )
        
        try:
            with urllib.request.urlopen(request) as response:
                for line in response:
                    data = json.loads(line.decode("utf-8"))
                    yield data
        except Exception as e:
            raise ConnectionError(f"Failed to download model: {e}")
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model from the Ollama server."""
        request = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/delete"),
            data=json.dumps({"name": model_name}).encode("utf-8"),
            method="DELETE",
        )
        
        try:
            with urllib.request.urlopen(request) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError("Model not found")
            raise ConnectionError(f"Failed to delete model: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to delete model: {e}")
