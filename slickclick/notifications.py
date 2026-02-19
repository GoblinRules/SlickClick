"""Toast notifications and on-screen indicator (OSD) for SlickClick.

Uses Tkinter Toplevel windows — no third-party dependencies.
The OSD uses ctypes to set WS_EX_TRANSPARENT so clicks pass through.
"""

import ctypes
import ctypes.wintypes as wintypes
import tkinter as tk

from .constants import COLORS
from .logging_config import logger

# Windows constants for click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008

user32 = ctypes.windll.user32


def _make_click_through(toplevel: tk.Toplevel):
    """Make a Toplevel window click-through using Windows extended styles.

    Only adds WS_EX_TRANSPARENT (pass-through clicks) and WS_EX_TOOLWINDOW
    (hide from taskbar).  Do NOT add WS_EX_LAYERED here — Tkinter already
    sets that via the ``-alpha`` attribute, and re-setting it wipes the
    rendered content to a grey box.
    """
    try:
        # Get the actual Win32 HWND from Tkinter's frame id
        frame_id = toplevel.wm_frame()
        hwnd = int(frame_id, 16) if frame_id else toplevel.winfo_id()
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE,
            style | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW,
        )
    except Exception as e:
        logger.error("Failed to set click-through: %s", e)


class ToastNotification:
    """Ephemeral toast popup in the bottom-right corner of the screen."""

    _DISPLAY_MS = 2000       # how long the toast stays visible
    _ANIM_STEP_MS = 16       # ~60 fps animation
    _SLIDE_DISTANCE = 120    # pixels to slide in from
    _TOAST_WIDTH = 220
    _TOAST_HEIGHT = 44
    _MARGIN = 20             # margin from screen edge

    def __init__(self, root: tk.Tk):
        self._root = root
        self._win: tk.Toplevel | None = None
        self._anim_id = None
        self._dismiss_id = None

    def show(self, running: bool):
        """Show a toast for starting or stopping."""
        self._cancel()

        text = "● Clicker Started" if running else "● Clicker Stopped"
        fg = COLORS["success"] if running else COLORS["accent"]

        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.92)
        win.configure(bg=COLORS["bg_dark"])
        win.withdraw()  # hide until positioned

        # Content
        frame = tk.Frame(win, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text=text, font=("Segoe UI", 11, "bold"),
            fg=fg, bg=COLORS["bg_card"],
        ).pack(padx=16, pady=10)

        self._win = win

        # Calculate final position (bottom-right)
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()

        self._final_x = screen_w - self._TOAST_WIDTH - self._MARGIN
        self._final_y = screen_h - self._TOAST_HEIGHT - self._MARGIN - 40  # above taskbar
        self._current_x = self._final_x + self._SLIDE_DISTANCE

        # Start slide-in animation
        win.geometry(f"{self._TOAST_WIDTH}x{self._TOAST_HEIGHT}"
                     f"+{self._current_x}+{self._final_y}")
        win.deiconify()

        # Make click-through so the toast doesn't steal focus
        win.update_idletasks()
        hwnd = int(win.wm_frame(), 16) if win.wm_frame() else ctypes.windll.user32.GetForegroundWindow()
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, None)
            hwnd = win.winfo_id()
        except Exception:
            pass

        self._slide_in()

    def _slide_in(self):
        """Animate the toast sliding in from the right."""
        if self._win is None:
            return
        if self._current_x > self._final_x:
            step = max(2, (self._current_x - self._final_x) // 4)
            self._current_x -= step
            if self._current_x < self._final_x:
                self._current_x = self._final_x
            self._win.geometry(f"{self._TOAST_WIDTH}x{self._TOAST_HEIGHT}"
                               f"+{self._current_x}+{self._final_y}")
            self._anim_id = self._root.after(self._ANIM_STEP_MS, self._slide_in)
        else:
            # Arrived — schedule dismiss
            self._dismiss_id = self._root.after(self._DISPLAY_MS, self._fade_out)

    def _fade_out(self):
        """Fade out the toast."""
        if self._win is None:
            return
        try:
            alpha = self._win.attributes("-alpha")
            if alpha > 0.1:
                self._win.attributes("-alpha", alpha - 0.08)
                self._anim_id = self._root.after(self._ANIM_STEP_MS, self._fade_out)
            else:
                self._destroy()
        except Exception:
            self._destroy()

    def _cancel(self):
        """Cancel any running animation and destroy existing toast."""
        if self._anim_id:
            self._root.after_cancel(self._anim_id)
            self._anim_id = None
        if self._dismiss_id:
            self._root.after_cancel(self._dismiss_id)
            self._dismiss_id = None
        self._destroy()

    def _destroy(self):
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None


class OSDIndicator:
    """Small persistent on-screen indicator while the clicker is running.

    Appears in the top-right corner of the screen. Click-through so
    it never interferes with the auto-clicker's target area.
    """

    _WIDTH = 110
    _HEIGHT = 28
    _MARGIN = 16

    def __init__(self, root: tk.Tk):
        self._root = root
        self._win: tk.Toplevel | None = None
        self._pulse_id = None
        self._pulse_on = True

    def show(self):
        """Show the OSD indicator."""
        if self._win is not None:
            return  # already showing

        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.85)
        win.configure(bg=COLORS["bg_dark"])

        # Position: top-right corner
        screen_w = self._root.winfo_screenwidth()
        x = screen_w - self._WIDTH - self._MARGIN
        y = self._MARGIN
        win.geometry(f"{self._WIDTH}x{self._HEIGHT}+{x}+{y}")

        frame = tk.Frame(win, bg=COLORS["accent"],
                         highlightbackground=COLORS["accent_dim"],
                         highlightthickness=1)
        frame.pack(fill="both", expand=True)

        self._dot_label = tk.Label(
            frame, text="●", font=("Segoe UI", 10),
            fg="white", bg=COLORS["accent"],
        )
        self._dot_label.pack(side="left", padx=(8, 4))

        tk.Label(
            frame, text="CLICKING", font=("Segoe UI", 9, "bold"),
            fg="white", bg=COLORS["accent"],
        ).pack(side="left", padx=(0, 8))

        self._win = win

        # Make click-through
        win.update_idletasks()
        _make_click_through(win)

        # Start pulsing dot
        self._pulse_on = True
        self._pulse()

    def hide(self):
        """Hide the OSD indicator."""
        if self._pulse_id:
            self._root.after_cancel(self._pulse_id)
            self._pulse_id = None
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

    def _pulse(self):
        """Pulse the dot to indicate activity."""
        if self._win is None or self._dot_label is None:
            return
        try:
            self._pulse_on = not self._pulse_on
            color = "white" if self._pulse_on else COLORS["accent"]
            self._dot_label.configure(fg=color)
            self._pulse_id = self._root.after(600, self._pulse)
        except Exception:
            pass
