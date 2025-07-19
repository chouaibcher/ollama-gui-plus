# Installation Guide - Ollama GUI Plus

## Overview
Ollama GUI Plus is a modern desktop application with MVVM architecture that provides a clean interface for interacting with Ollama models.

## Requirements
- Python 3.8 or higher
- Tkinter (usually included with Python)
- Ollama server running locally or remotely

## Installation Methods

### Method 1: Direct Download and Run (Recommended)

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/chouaibcher/ollama-gui-plus.git
   cd ollama-gui-plus
   ```

2. **Run directly (no installation needed):**
   ```bash
   # Modern MVVM architecture (recommended)
   python main.py
      ```

### Method 2: Install with pip (From source)

1. **Install from the current directory:**
   ```bash
   pip install .
   ```

2. **Run from anywhere:**
   ```bash
   ollama-gui          
   ```

### Method 3: Development Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chouaibcher/ollama-gui-plus.git
   cd ollama-gui-plus
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .
   ```

### Method 4: Using Poetry (For developers)

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Run the application:**
   ```bash
   poetry run ollama-gui
   ```

## Verification

### Test the Installation
```bash
# Test MVVM structure imports
python -c "from src.models.chat_models import ChatMessage; print('Installation successful!')"

# Test main entry point
python main.py



### Check Available Commands
After pip installation:
```bash
ollama-gui --help          # Should show help or start the GUI
```

## Configuration

### Ollama Server Setup
1. **Install Ollama:** Follow instructions at https://ollama.ai
2. **Start Ollama server:**
   ```bash
   ollama serve
   ```
3. **Download a model:**
   ```bash
   ollama pull llama2
   ```

### GUI Configuration
- The application will default to `http://127.0.0.1:11434`
- You can change the host in the GUI interface
- Models can be downloaded directly through the GUI

## Project Structure
```
ollama-gui-plus/
├── src/                    # MVVM architecture source code
│   ├── models/            # Data models
│   ├── views/             # UI components
│   ├── viewmodels/        # Business logic
│   ├── services/          # API communication
│   └── utils/             # Utilities
├── main.py                # New entry point (MVVM)
├── pyproject.toml         # Poetry configuration
├── setup.py               # Pip installation setup
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── ARCHITECTURE.md        # Architecture documentation
```

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'tkinter'"**
- **Linux:** `sudo apt-get install python3-tk`
- **macOS:** `brew install python-tk`
- **Windows:** Tkinter is usually included with Python

**2. "Connection Error"**
- Ensure Ollama server is running: `ollama serve`
- Check the host URL in the GUI
- Verify firewall settings

**3. "No models available"**
- Download models: `ollama pull llama2`
- Or use the GUI's model management feature

**4. Import errors with MVVM structure**
- Ensure you're running from the project root directory
- Check Python path: `python -c "import sys; print(sys.path)"`

### Development Issues

**1. Type checking with mypy:**
```bash
mypy src/
```

**2. Code formatting with black:**
```bash
black src/ main.py 
```

**3. Linting with flake8:**
```bash
flake8 src/ main.py 
```

**4. Running tests:**
```bash
pytest tests/
```

## Uninstallation

### If installed with pip:
```bash
pip uninstall ollama-gui-plus
```

### If using direct download:
Simply delete the project directory.

### If using Poetry:
```bash
poetry env remove python
```

## Support

- **Issues:** https://github.com/chouaibcher/ollama-gui-plus/issues
- **Documentation:** See ARCHITECTURE.md for technical details
- **Original Project:** https://github.com/chyok/ollama-gui
