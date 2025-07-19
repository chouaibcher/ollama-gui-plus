"""
System utilities for the Ollama GUI application.
"""

import platform
import tkinter as tk
from typing import Optional


def system_check(root: tk.Tk) -> Optional[str]:
    """
    Detect system and software compatibility issues.
    
    :param root: Tk instance
    :return: None or warning message string
    """
    
    def _version_tuple(v):
        """A lazy way to avoid importing third-party libraries"""
        filled = []
        for point in v.split("."):
            filled.append(point.zfill(8))
        return tuple(filled)

    # Tcl and macOS issue: https://github.com/python/cpython/issues/110218
    if platform.system().lower() == "darwin":
        version = platform.mac_ver()[0]
        if version and 14 <= float(version) < 15:
            tcl_version = root.tk.call("info", "patchlevel")
            if _version_tuple(tcl_version) <= _version_tuple("8.6.12"):
                return (
                    "Warning: Tkinter Responsiveness Issue Detected\n\n"
                    "You may experience unresponsive GUI elements when "
                    "your cursor is inside the window during startup. "
                    "This is a known issue with Tcl/Tk versions 8.6.12 "
                    "and older on macOS Sonoma.\n\nTo resolve this:\n"
                    "Update to Python 3.11.7+ or 3.12+\n"
                    "Or install Tcl/Tk 8.6.13 or newer separately\n\n"
                    "Temporary workaround: Move your cursor out of "
                    "the window and back in if elements become unresponsive.\n\n"
                    "For more information, visit: https://github.com/python/cpython/issues/110218"
                )
    
    return None


def get_platform_right_click_event() -> str:
    """Get the correct right-click event for the current platform."""
    return "<Button-2>" if platform.system().lower() == "darwin" else "<Button-3>"
