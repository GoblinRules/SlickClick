"""Global hotkey listener using pynput."""

import threading
from pynput import keyboard

from .constants import DEFAULT_HOTKEY


class HotkeyListener:
    """Listens for a global hotkey and fires a toggle callback."""

    def __init__(self, on_toggle=None):
        self._hotkey_name = DEFAULT_HOTKEY
        self._hotkey_key = self._resolve_key(DEFAULT_HOTKEY)
        self._on_toggle = on_toggle
        self._listener: keyboard.Listener | None = None
        self._capturing = False
        self._on_capture = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def hotkey_name(self) -> str:
        return self._hotkey_name

    def start(self):
        """Start listening for the hotkey in a background thread."""
        if self._listener is not None:
            return
        self._listener = keyboard.Listener(on_press=self._on_key_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        """Stop the listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None

    def set_hotkey(self, key_name: str):
        """Change the hotkey."""
        self._hotkey_name = key_name
        self._hotkey_key = self._resolve_key(key_name)

    def begin_capture(self, callback):
        """
        Enter capture mode — next key press will be used as the new hotkey.
        callback(key_name) is called with the captured key name.
        """
        self._capturing = True
        self._on_capture = callback

    def cancel_capture(self):
        """Cancel capture mode."""
        self._capturing = False
        self._on_capture = None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_key_press(self, key):
        if self._capturing:
            name = self._key_to_name(key)
            if name:
                self._hotkey_name = name
                self._hotkey_key = key
                self._capturing = False
                if self._on_capture:
                    try:
                        self._on_capture(name)
                    except Exception:
                        pass
                self._on_capture = None
            return

        # Normal mode — check if pressed key matches hotkey
        if self._keys_match(key, self._hotkey_key):
            if self._on_toggle:
                try:
                    self._on_toggle()
                except Exception:
                    pass

    def _keys_match(self, pressed, target) -> bool:
        """Compare two pynput keys."""
        try:
            # Both are Key enums
            if hasattr(pressed, "name") and hasattr(target, "name"):
                return pressed == target
            # Both are KeyCode
            if hasattr(pressed, "char") and hasattr(target, "char"):
                return pressed.char == target.char
            # Compare vk codes if available
            if hasattr(pressed, "vk") and hasattr(target, "vk"):
                return pressed.vk == target.vk
        except Exception:
            pass
        return pressed == target

    @staticmethod
    def _resolve_key(name: str):
        """Convert a key name string to a pynput Key object."""
        # Try as a special key (F1-F12, Escape, etc.)
        try:
            return getattr(keyboard.Key, name.lower())
        except AttributeError:
            pass
        # Try as a function key with 'f' prefix
        try:
            return getattr(keyboard.Key, name.lower())
        except AttributeError:
            pass
        # Single character
        if len(name) == 1:
            return keyboard.KeyCode.from_char(name)
        return keyboard.KeyCode.from_char(name)

    @staticmethod
    def _key_to_name(key) -> str | None:
        """Convert a pynput key to a human-readable name."""
        # Special keys
        if hasattr(key, "name"):
            return key.name.capitalize() if key.name else None
        # Regular characters
        if hasattr(key, "char") and key.char:
            return key.char.upper()
        # Virtual key code fallback
        if hasattr(key, "vk") and key.vk:
            return f"VK_{key.vk}"
        return None
