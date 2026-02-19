"""Global hotkey listener using Windows RegisterHotKey API.

Uses ctypes to call the Windows RegisterHotKey / UnregisterHotKey
functions directly — no third-party dependency required.  This is
more reliable than pynput in PyInstaller-packaged executables.
"""

import ctypes
import ctypes.wintypes as wintypes
import threading
import time

from .logging_config import logger
from .constants import DEFAULT_HOTKEY

user32 = ctypes.windll.user32

WM_HOTKEY = 0x0312
_HOTKEY_ID = 1

# ── Virtual-key code table ────────────────────────────────────────────
_VK_MAP: dict[str, int] = {}

def _build_vk_map():
    m: dict[str, int] = {}
    # Function keys F1–F24
    for i in range(1, 25):
        m[f"F{i}"] = 0x6F + i          # VK_F1 = 0x70
    # Letters A–Z
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        m[c] = ord(c)                   # VK_A = 0x41
    # Digits 0–9
    for c in "0123456789":
        m[c] = ord(c)                   # VK_0 = 0x30
    # Special keys (common hotkey candidates)
    m["SPACE"]      = 0x20
    m["ENTER"]      = 0x0D
    m["RETURN"]     = 0x0D
    m["ESCAPE"]     = 0x1B
    m["TAB"]        = 0x09
    m["INSERT"]     = 0x2D
    m["DELETE"]     = 0x2E
    m["HOME"]       = 0x24
    m["END"]        = 0x23
    m["PAGEUP"]     = 0x21
    m["PAGE_UP"]    = 0x21
    m["PAGEDOWN"]   = 0x22
    m["PAGE_DOWN"]  = 0x22
    m["UP"]         = 0x26
    m["DOWN"]       = 0x28
    m["LEFT"]       = 0x25
    m["RIGHT"]      = 0x27
    m["NUMPAD0"]    = 0x60
    m["NUMPAD1"]    = 0x61
    m["NUMPAD2"]    = 0x62
    m["NUMPAD3"]    = 0x63
    m["NUMPAD4"]    = 0x64
    m["NUMPAD5"]    = 0x65
    m["NUMPAD6"]    = 0x66
    m["NUMPAD7"]    = 0x67
    m["NUMPAD8"]    = 0x68
    m["NUMPAD9"]    = 0x69
    m["PAUSE"]      = 0x13
    m["SCROLL_LOCK"] = 0x91
    m["CAPS_LOCK"]  = 0x14
    return m

_VK_MAP = _build_vk_map()

# Reverse map: Tkinter keysym → our canonical name
_TKINTER_KEYSYM_MAP = {
    "space": "SPACE", "Return": "ENTER", "Escape": "ESCAPE",
    "Tab": "TAB", "Insert": "INSERT", "Delete": "DELETE",
    "Home": "HOME", "End": "END",
    "Prior": "PAGEUP", "Next": "PAGEDOWN",
    "Up": "UP", "Down": "DOWN", "Left": "LEFT", "Right": "RIGHT",
    "Pause": "PAUSE", "Scroll_Lock": "SCROLL_LOCK",
    "Caps_Lock": "CAPS_LOCK",
}


def _name_to_vk(name: str) -> int | None:
    """Convert a key name (e.g. 'F6', 'X') to a Windows virtual-key code."""
    return _VK_MAP.get(name.upper())


def _tkinter_event_to_name(event) -> str | None:
    """Convert a Tkinter <KeyPress> event to our canonical key name."""
    sym = event.keysym
    # Check special keys
    if sym in _TKINTER_KEYSYM_MAP:
        return _TKINTER_KEYSYM_MAP[sym]
    # Function keys
    if sym.startswith("F") and sym[1:].isdigit():
        return sym.upper()
    # Single printable character
    if len(sym) == 1 and sym.isalnum():
        return sym.upper()
    # Numeric keypad
    if sym.startswith("KP_") and sym[3:].isdigit():
        return f"NUMPAD{sym[3:]}"
    # Ignore modifier-only presses (Shift, Ctrl, Alt)
    if sym in ("Shift_L", "Shift_R", "Control_L", "Control_R",
               "Alt_L", "Alt_R", "Super_L", "Super_R", "Meta_L", "Meta_R"):
        return None
    # Fallback: try the character
    if event.char and len(event.char) == 1 and event.char.isalnum():
        return event.char.upper()
    return None


class HotkeyListener:
    """Listens for a global hotkey via Windows RegisterHotKey API."""

    def __init__(self, on_toggle=None):
        self._hotkey_name: str = DEFAULT_HOTKEY
        self._on_toggle = on_toggle
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._change_event = threading.Event()   # signal to re-register

        # Capture state (for Tkinter-based key capture)
        self._capturing = False
        self._on_capture = None
        self._capture_bind_id = None
        self._capture_root = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def hotkey_name(self) -> str:
        return self._hotkey_name

    def start(self):
        """Start listening for the hotkey in a background thread."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._change_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the listener."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        self._thread = None

    def set_hotkey(self, key_name: str):
        """Change the hotkey (thread-safe, triggers re-registration)."""
        self._hotkey_name = key_name
        self._change_event.set()

    def begin_capture(self, root, callback):
        """
        Enter capture mode using Tkinter key binding.
        The next key press on root will be used as the new hotkey.
        """
        self._capturing = True
        self._on_capture = callback
        self._capture_root = root
        self._capture_bind_id = root.bind_all("<KeyPress>", self._on_tk_key_press)
        logger.info("Capture mode started")

    def cancel_capture(self):
        """Cancel capture mode."""
        self._unbind_capture()
        self._capturing = False
        self._on_capture = None

    # ------------------------------------------------------------------
    # Internal — Windows hotkey thread
    # ------------------------------------------------------------------

    def _run(self):
        """Background thread: register hotkey → pump messages → loop."""
        while not self._stop_event.is_set():
            vk = _name_to_vk(self._hotkey_name)
            if vk is None:
                logger.error("Unknown hotkey '%s' — cannot register", self._hotkey_name)
                # Wait for a hotkey change or stop
                while not self._stop_event.is_set() and not self._change_event.is_set():
                    time.sleep(0.1)
                self._change_event.clear()
                continue

            # Register
            ok = user32.RegisterHotKey(None, _HOTKEY_ID, 0, vk)
            if not ok:
                err = ctypes.get_last_error()
                logger.error("RegisterHotKey failed for '%s' (vk=0x%02X), "
                             "error=%d", self._hotkey_name, vk, err)
                time.sleep(1)
                continue

            logger.info("Hotkey registered: %s (vk=0x%02X)", self._hotkey_name, vk)
            self._change_event.clear()

            # Message pump
            msg = wintypes.MSG()
            while not self._stop_event.is_set() and not self._change_event.is_set():
                # PeekMessageW with PM_REMOVE (0x1)
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0x0001):
                    if msg.message == WM_HOTKEY and msg.wParam == _HOTKEY_ID:
                        logger.info("Hotkey triggered: %s", self._hotkey_name)
                        if self._on_toggle:
                            try:
                                self._on_toggle()
                            except Exception as e:
                                logger.error("Toggle callback error: %s", e,
                                             exc_info=True)
                time.sleep(0.01)

            # Unregister before re-registering or exiting
            user32.UnregisterHotKey(None, _HOTKEY_ID)
            logger.info("Hotkey unregistered: %s", self._hotkey_name)
            self._change_event.clear()

    # ------------------------------------------------------------------
    # Internal — Tkinter capture
    # ------------------------------------------------------------------

    def _on_tk_key_press(self, event):
        """Handle Tkinter KeyPress during capture mode."""
        if not self._capturing:
            return
        name = _tkinter_event_to_name(event)
        if name is None:
            return   # Ignore modifier-only keys

        logger.info("Captured key: %s", name)
        self._unbind_capture()
        self._capturing = False

        cb = self._on_capture
        self._on_capture = None
        if cb:
            try:
                cb(name)
            except Exception as e:
                logger.error("Capture callback error: %s", e, exc_info=True)

    def _unbind_capture(self):
        if self._capture_bind_id and self._capture_root:
            try:
                self._capture_root.unbind_all("<KeyPress>")
            except Exception:
                pass
        self._capture_bind_id = None
        self._capture_root = None
