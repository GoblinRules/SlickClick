"""Application-wide constants and defaults."""

import os
import sys

APP_NAME = "SlickClick"
APP_VERSION = "1.2.3"


def resource_path(relative_path: str) -> str:
    """Resolve a resource path for both dev and PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ICON_PATH = resource_path("assets/icon.ico")

# Default click interval in milliseconds
DEFAULT_INTERVAL_MS = 100

# Default hotkey
DEFAULT_HOTKEY = "F6"

# Mouse buttons
MOUSE_BUTTONS = ["Left", "Right", "Middle"]
MOUSE_BUTTON_MAP = {
    "Left": "left",
    "Right": "right",
    "Middle": "middle",
}

# Click types
CLICK_TYPES = ["Single", "Double"]

# Repeat modes
REPEAT_FINITE = "finite"
REPEAT_INFINITE = "infinite"

# Theme colors (dark theme)
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "bg_card": "#1f2940",
    "accent": "#e94560",
    "accent_hover": "#ff6b81",
    "accent_dim": "#c23152",
    "text_primary": "#eaeaea",
    "text_secondary": "#a0a0b0",
    "text_muted": "#6c6c80",
    "border": "#2a2a4a",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "input_bg": "#12192b",
    "input_border": "#2a3a5c",
    "button_bg": "#243352",
    "button_hover": "#2d4068",
    "listbox_bg": "#12192b",
    "listbox_select": "#0f3460",
}
