# Ollama GUI Plus

![GitHub License](https://img.shields.io/github/license/chouaibcher/ollama-gui-plus)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Architecture](https://img.shields.io/badge/architecture-MVVM-green)

A modern Ollama GUI with clean MVVM architecture, implemented using Python Tkinter with professional code organization and no external dependencies.
Provides a simple, maintainable, and extensible visual interface for Ollama.

![ollama-gui-1 2 0](https://github.com/user-attachments/assets/a4bb979b-68a4-4062-b484-7542f2a866e0)


## 🚀 Features

### Core Functionality
+ � **Interactive Chat Interface** - Clean, responsive chat with Ollama models
+ 🔍 **Auto Model Detection** - Automatically discovers available Ollama models  
+ 🌐 **Customizable Host Support** - Connect to local or remote Ollama servers
+ 🗂️ **Model Management** - Download and delete models directly from the GUI
+ 🎨 **Modern UI** - Bubble dialog theme with professional appearance
+ 📝 **Editable Conversations** - Edit and modify chat history
+ 🛑 **Stop Generation** - Interrupt AI responses at any time
+ 📋 **Menu & Context Menus** - Full menu bar and right-click functionality

### Architecture & Code Quality
+ 🏗️ **MVVM Architecture** - Clean separation of concerns for maintainability
+ � **Zero Dependencies** - Uses only Python standard library (tkinter)
+ 🔧 **Type Safety** - Comprehensive type hints throughout codebase  
+ 🧪 **Testable Design** - Business logic separated from UI for easy testing
+ 📚 **Professional Documentation** - Complete architecture and API documentation
+ 🔄 **Backward Compatibility** - Legacy entry point maintained for existing users

### Developer Experience
+ 🛠️ **Development Tools** - Pre-configured linting, formatting, and testing
+ � **Scalable Structure** - Easy to extend with new features
+ 👥 **Team-Friendly** - Clear code organization for collaborative development

## 📎 Before Start

We need to set up Ollama service first.

Please refer to:   
+ [Ollama](https://ollama.com/)  
+ [Ollama Github](https://github.com/ollama/ollama)

## ⚙️ Installation & Usage

### Quick Start (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/chouaibcher/ollama-gui-plus.git
cd ollama-gui-plus
```

2. **Run the application:**
```bash
# Modern MVVM architecture (recommended)
python main.py

# Legacy compatibility mode
python ollama_gui.py
```

### Install as Package

```bash
# Install from source
pip install .

# Run from anywhere
ollama-gui          # Modern MVVM version
ollama-gui-legacy   # Legacy compatibility
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run with development tools
ollama-gui
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

## 🏗️ Architecture

This project follows the **MVVM (Model-View-ViewModel)** design pattern for clean, maintainable code:

```
src/
├── models/          # Data models and business entities
├── views/           # UI components and presentation logic  
├── viewmodels/      # Business logic and state management
├── services/        # External API communication
└── utils/           # Utility functions and helpers
```

### Key Benefits:
- **Separation of Concerns** - Each layer has specific responsibilities
- **Testability** - Business logic is independent of UI
- **Maintainability** - Easy to modify and extend
- **Professional Standards** - Industry-standard code organization

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## �️ Development

### Code Quality Tools
```bash
# Format code
black src/ main.py

# Type checking  
mypy src/

# Linting
flake8 src/

# Run tests
pytest tests/
```

### Project Structure
- `main.py` - Modern MVVM entry point
- `ollama_gui.py` - Legacy compatibility entry point  
- `src/` - MVVM architecture source code
- `tests/` - Unit and integration tests
- `docs/` - Documentation and guides

## 📋 Troubleshooting

### Connection Issues

**"Connection Error" or "Error! Please check the host"**
- Ensure Ollama server is running: `ollama serve`
- Verify the host URL in the GUI (default: http://127.0.0.1:11434)
- Check firewall settings

**"You need to download a model!"**
- Download models via CLI: `ollama pull llama2`
- Or use the GUI's model management feature (⚙️ button)

### Installation Issues

**"ModuleNotFoundError: No module named 'tkinter'"**

For Ubuntu or other distros with Apt:
```bash
sudo apt-get install python3-tk
```

For Fedora:
```bash
sudo dnf install python3-tkinter
```

For macOS:
```bash
brew install python-tk
```

For Windows:
Make sure to **check "tcl/tk and IDLE"** during Python installation.

**Import errors with MVVM structure**
- Ensure you're running from the project root directory
- Check Python version: requires Python 3.8+

### Platform-Specific Issues

**macOS Sonoma - Unresponsive GUI Elements**

The issue affects macOS Sonoma users with Tcl/Tk versions 8.6.12 or older.
When the mouse cursor is inside the window during startup, GUI elements may become unresponsive.

**Solution:**
- Update to Python 3.11.7+ or 3.12+ (includes fixed Tcl/Tk version)
- Or install Tcl/Tk 8.6.13+ separately via Homebrew
- **Temporary workaround:** Move cursor out of window and back in if unresponsive

Reference: https://github.com/python/cpython/issues/110218

## 📚 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions
- **[Architecture Guide](ARCHITECTURE.md)** - MVVM design pattern explanation  
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Migration from monolithic to MVVM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the MVVM architecture
4. Run tests and linting: `pytest && flake8 src/`
5. Submit a pull request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Original Project:** This is a refactored version of [ollama-gui](https://github.com/chyok/ollama-gui) by chyok, enhanced with MVVM architecture and modern development practices.

