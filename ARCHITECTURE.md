# Ollama GUI Plus - MVVM Architecture

This is a refactored version of the Ollama GUI that follows the MVVM (Model-View-ViewModel) design pattern for better code organization, maintainability, and testability.

## Architecture Overview

The application is now organized into the following layers:

### 📁 Project Structure

```
ollama-gui-plus/
├── src/
│   ├── models/              # Data models and business entities
│   │   ├── __init__.py
│   │   └── chat_models.py   # ChatMessage, Model, ChatSession, ApplicationState
│   ├── views/               # UI components and presentation logic
│   │   ├── __init__.py
│   │   ├── main_view.py     # Main application window
│   │   └── model_management_view.py  # Model management dialog
│   ├── viewmodels/          # Business logic and state management
│   │   ├── __init__.py
│   │   ├── chat_viewmodel.py          # Chat functionality logic
│   │   └── model_management_viewmodel.py  # Model management logic
│   ├── services/            # External service communication
│   │   ├── __init__.py
│   │   └── ollama_service.py  # Ollama API communication
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── system_utils.py  # System compatibility checks
├── main.py                  # New main entry point
├── ollama_gui.py           # Legacy entry point (backward compatible)
├── pyproject.toml
└── README.md
```

## MVVM Pattern Implementation

### Model Layer (`src/models/`)
- **Purpose**: Contains data structures and business entities
- **Files**:
  - `chat_models.py`: Defines `ChatMessage`, `Model`, `ChatSession`, and `ApplicationState` classes
- **Responsibilities**:
  - Data representation
  - Business rules validation
  - State management

### View Layer (`src/views/`)
- **Purpose**: Handles UI presentation and user interactions
- **Files**:
  - `main_view.py`: Main application window with chat interface
  - `model_management_view.py`: Model download/delete dialog
- **Responsibilities**:
  - UI layout and styling
  - User input handling
  - Display updates
  - Event binding

### ViewModel Layer (`src/viewmodels/`)
- **Purpose**: Bridges View and Model, contains business logic
- **Files**:
  - `chat_viewmodel.py`: Manages chat functionality and state
  - `model_management_viewmodel.py`: Handles model operations
- **Responsibilities**:
  - Business logic processing
  - State management
  - View-Model data binding
  - Asynchronous operations coordination

### Service Layer (`src/services/`)
- **Purpose**: External API communication and data fetching
- **Files**:
  - `ollama_service.py`: Ollama API client
- **Responsibilities**:
  - API communication
  - Data transformation
  - Error handling for external services

### Utilities (`src/utils/`)
- **Purpose**: Common utility functions
- **Files**:
  - `system_utils.py`: System compatibility and helper functions

## Benefits of MVVM Architecture

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Testability**: Business logic is separated from UI, making unit testing easier
3. **Maintainability**: Changes in one layer don't affect others
4. **Reusability**: ViewModels can be reused with different Views
5. **Scalability**: Easy to add new features and extend functionality

## Running the Application

### New Entry Point (Recommended)
```bash
python main.py
```

### Legacy Entry Point (Backward Compatible)
```bash
python ollama_gui.py
```

The legacy entry point is maintained for backward compatibility but uses the new MVVM architecture internally.

## Key Features of the Refactored Code

### Event-Driven Architecture
- ViewModels use callback patterns to notify Views of state changes
- Asynchronous operations are handled cleanly with proper separation

### Type Safety
- Extensive use of type hints for better code documentation and IDE support
- Dataclasses for structured data representation

### Error Handling
- Centralized error handling in the service layer
- Proper exception propagation through the layers

### Threading
- Background operations (API calls, model downloads) are handled in separate threads
- UI remains responsive during long-running operations

## Development Guidelines

### Adding New Features
1. **Model**: Define data structures in `src/models/`
2. **Service**: Add API communication logic in `src/services/`
3. **ViewModel**: Implement business logic in `src/viewmodels/`
4. **View**: Create UI components in `src/views/`

### Testing
The MVVM architecture makes it easy to test business logic:
- Unit test ViewModels independently
- Mock services for integration testing
- Test Views with mock ViewModels

### Code Style
- Follow PEP 8 conventions
- Use type hints consistently
- Document classes and methods with docstrings
- Keep methods focused and single-purpose

## Migration from Legacy Code

The refactoring maintains backward compatibility while providing a modern architecture. Existing users can continue using `ollama_gui.py`, while new development should use the MVVM structure starting from `main.py`.

## Future Enhancements

The MVVM architecture enables easy implementation of future features:
- Multiple chat sessions
- Plugin system
- Theme support
- Advanced model management
- Export/import functionality
- Settings persistence
