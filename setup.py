"""
Setup configuration for ollama-gui-plus with MVVM architecture.
This provides compatibility for pip installations.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the version from main.py
def get_version():
    """Extract version from main.py."""
    version = "1.2.1"  # Default version
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    version = line.split('"')[1]
                    break
    except FileNotFoundError:
        pass
    return version

setup(
    name="ollama-gui-plus",
    version=get_version(),
    author="chyok, chouaibcher",
    author_email="chyok@hotmail.com",
    description="A modern Ollama GUI with MVVM architecture, implemented using Python Tkinter with clean separation of concerns.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chouaibcher/ollama-gui-plus",
    project_urls={
        "Bug Tracker": "https://github.com/chouaibcher/ollama-gui-plus/issues",
        "Documentation": "https://github.com/chouaibcher/ollama-gui-plus/blob/main/ARCHITECTURE.md",
        "Source Code": "https://github.com/chouaibcher/ollama-gui-plus",
    },
    packages=find_packages(include=["src", "src.*"]),
    py_modules=["main", "ollama_gui"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
        "Framework :: tkinter",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - using only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ollama-gui=main:main",
            "ollama-gui-legacy=ollama_gui:run",
        ],
    },
    keywords=[
        "ollama",
        "gui",
        "chat",
        "ai",
        "llm",
        "tkinter",
        "mvvm",
        "desktop",
        "interface",
    ],
    include_package_data=True,
    zip_safe=False,
)
