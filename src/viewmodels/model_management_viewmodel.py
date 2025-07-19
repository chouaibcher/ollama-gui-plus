"""
ViewModel for model management functionality.
"""

from threading import Thread
from typing import List, Callable, Optional, Dict, Any
from ..models.chat_models import Model
from ..services.ollama_service import OllamaApiService


class ModelManagementViewModel:
    """ViewModel for managing Ollama models."""
    
    def __init__(self, api_service: OllamaApiService):
        self.api_service = api_service
        self.available_models: List[Model] = []
        
        # Event callbacks for the view
        self.on_models_updated: Optional[Callable[[List[Model]], None]] = None
        self.on_download_progress: Optional[Callable[[str], None]] = None
        self.on_download_complete: Optional[Callable[[str], None]] = None
        self.on_download_error: Optional[Callable[[str], None]] = None
        self.on_delete_complete: Optional[Callable[[str], None]] = None
        self.on_delete_error: Optional[Callable[[str], None]] = None
        self.on_operation_started: Optional[Callable[[], None]] = None
        self.on_operation_finished: Optional[Callable[[], None]] = None
    
    def refresh_models(self) -> None:
        """Refresh the list of available models."""
        Thread(target=self._fetch_models_async, daemon=True).start()
    
    def _fetch_models_async(self) -> None:
        """Fetch models in a background thread."""
        try:
            self.available_models = self.api_service.fetch_models()
            if self.on_models_updated:
                self.on_models_updated(self.available_models)
        except Exception as e:
            if self.on_download_error:
                self.on_download_error(f"Failed to fetch models: {e}")
    
    def download_model(self, model_name: str, insecure: bool = False) -> None:
        """Download a model asynchronously."""
        if not model_name.strip():
            return
        
        # Handle "ollama run" prefix
        if model_name.startswith("ollama run "):
            model_name = model_name[11:]
        
        Thread(target=self._download_model_async, args=(model_name, insecure), daemon=True).start()
    
    def _download_model_async(self, model_name: str, insecure: bool) -> None:
        """Download model in a background thread."""
        if self.on_operation_started:
            self.on_operation_started()
        
        try:
            for progress_data in self.api_service.pull_model(model_name, insecure):
                log_message = progress_data.get("error") or progress_data.get("status") or "No response"
                
                if "status" in progress_data:
                    total = progress_data.get("total")
                    completed = progress_data.get("completed", 0)
                    if total:
                        log_message += f" [{completed}/{total}]"
                
                if self.on_download_progress:
                    self.on_download_progress(log_message)
            
            if self.on_download_complete:
                self.on_download_complete(f"Model '{model_name}' downloaded successfully")
            
            # Refresh models after download
            self.refresh_models()
            
        except Exception as e:
            if self.on_download_error:
                self.on_download_error(f"Failed to download model '{model_name}': {e}")
        finally:
            if self.on_operation_finished:
                self.on_operation_finished()
    
    def delete_model(self, model_name: str) -> None:
        """Delete a model asynchronously."""
        if not model_name.strip():
            return
        
        Thread(target=self._delete_model_async, args=(model_name,), daemon=True).start()
    
    def _delete_model_async(self, model_name: str) -> None:
        """Delete model in a background thread."""
        if self.on_operation_started:
            self.on_operation_started()
        
        try:
            success = self.api_service.delete_model(model_name)
            if success:
                if self.on_delete_complete:
                    self.on_delete_complete(f"Model '{model_name}' deleted successfully")
            else:
                if self.on_delete_error:
                    self.on_delete_error(f"Failed to delete model '{model_name}'")
            
            # Refresh models after deletion
            self.refresh_models()
            
        except ValueError as e:
            if self.on_delete_error:
                self.on_delete_error(str(e))
        except Exception as e:
            if self.on_delete_error:
                self.on_delete_error(f"Failed to delete model '{model_name}': {e}")
        finally:
            if self.on_operation_finished:
                self.on_operation_finished()
    
    def get_available_models(self) -> List[Model]:
        """Get the list of available models."""
        return self.available_models
