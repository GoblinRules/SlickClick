"""SlickClick — Persistent settings stored as JSON in user's AppData."""

import json
import os

from .constants import DEFAULT_HOTKEY, DEFAULT_INTERVAL_MS

# Config file lives in %APPDATA%/SlickClick/config.json
_APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "SlickClick")
CONFIG_PATH = os.path.join(_APP_DIR, "config.json")

DEFAULTS = {
    "hotkey": DEFAULT_HOTKEY,
    "interval_hours": 0,
    "interval_mins": 0,
    "interval_secs": 0,
    "interval_ms": DEFAULT_INTERVAL_MS,
    "mouse_button": "Left",
    "click_type": "Single",
    "repeat_mode": "infinite",
    "repeat_count": 50,
    "show_toast": True,
    "show_osd": True,
}


def load() -> dict:
    """Load settings from disk, returning defaults for any missing keys."""
    data = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        data.update(saved)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return data


def save(settings: dict) -> None:
    """Save settings to disk."""
    try:
        os.makedirs(_APP_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
