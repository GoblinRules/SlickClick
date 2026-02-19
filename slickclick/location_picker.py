"""Location picker (floating toolbar) and dry-run preview."""

import tkinter as tk
import pyautogui

from .constants import COLORS, ICON_PATH


# Palette for numbered dot markers
DOT_COLORS = [
    "#e94560", "#2ecc71", "#3498db", "#f1c40f",
    "#9b59b6", "#e67e22", "#1abc9c", "#e74c3c",
    "#2980b9", "#27ae60", "#f39c12", "#8e44ad",
]


class LocationPicker:
    """
    Floating toolbar approach for picking screen coordinates.

    Instead of a fragile fullscreen overlay, this shows a small always-on-top
    instruction bar. The user moves their mouse to the desired position and
    presses Space/Enter to capture the coordinates. Works reliably on all
    Windows versions.
    """

    def __init__(self, parent, on_location_picked):
        self._parent = parent
        self._on_location_picked = on_location_picked
        self._on_undo_callback = None  # set externally by main.py
        self._toolbar = None
        self._pick_count = 0
        self._coord_label = None
        self._count_label = None
        self._polling_id = None

    def show(self, existing_locations: list[tuple[int, int]] | None = None):
        """Open the picker toolbar."""
        if self._toolbar is not None:
            return

        self._pick_count = len(existing_locations) if existing_locations else 0

        self._toolbar = tk.Toplevel(self._parent)
        self._toolbar.title("SlickClick — Pick Locations")
        self._toolbar.overrideredirect(True)
        self._toolbar.attributes("-topmost", True)
        self._toolbar.configure(bg=COLORS["bg_dark"])

        try:
            self._toolbar.iconbitmap(ICON_PATH)
        except Exception:
            pass

        # --- Layout ---
        bar_width = 420
        bar_height = 110

        # Position at top-center of screen
        screen_w = self._toolbar.winfo_screenwidth()
        x_pos = (screen_w - bar_width) // 2
        self._toolbar.geometry(f"{bar_width}x{bar_height}+{x_pos}+20")

        # Title bar (draggable)
        title_bar = tk.Frame(self._toolbar, bg=COLORS["accent"], height=28)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        title_lbl = tk.Label(
            title_bar, text="⚡ Pick Locations", font=("Segoe UI", 10, "bold"),
            fg="white", bg=COLORS["accent"],
        )
        title_lbl.pack(side="left", padx=8)

        close_btn = tk.Label(
            title_bar, text="✕", font=("Segoe UI", 10, "bold"),
            fg="white", bg=COLORS["accent"], cursor="hand2", padx=8,
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._close())

        # Make title bar draggable
        title_bar.bind("<Button-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)
        title_lbl.bind("<Button-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>", self._do_drag)

        # Body
        body = tk.Frame(self._toolbar, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True)

        # Instructions
        tk.Label(
            body,
            text="Move mouse to target → press Space to capture",
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
        ).pack(pady=(8, 2))

        # Live coordinate display + count
        info_frame = tk.Frame(body, bg=COLORS["bg_card"])
        info_frame.pack(fill="x", padx=12, pady=(0, 4))

        self._coord_label = tk.Label(
            info_frame,
            text="Cursor: (-, -)",
            font=("Consolas", 10),
            fg=COLORS["accent"], bg=COLORS["bg_card"],
            anchor="w",
        )
        self._coord_label.pack(side="left")

        self._count_label = tk.Label(
            info_frame,
            text=f"Saved: {self._pick_count}",
            font=("Segoe UI", 10, "bold"),
            fg=COLORS["success"], bg=COLORS["bg_card"],
            anchor="e",
        )
        self._count_label.pack(side="right")

        # Bottom row: Escape hint
        tk.Label(
            body,
            text="Press Escape or close to finish  •  Ctrl+Z to undo",
            font=("Segoe UI", 8),
            fg=COLORS["text_muted"], bg=COLORS["bg_card"],
        ).pack(pady=(0, 6))

        # Bind keyboard events
        self._toolbar.bind("<space>", self._on_capture)
        self._toolbar.bind("<Return>", self._on_capture)
        self._toolbar.bind("<Escape>", lambda e: self._close())
        self._toolbar.bind("<Control-z>", self._on_undo)

        self._toolbar.focus_force()

        # Delayed focus grab — needed because the tkinter menu holds focus
        # until it fully closes, so immediate focus_force isn't enough
        def _grab_focus():
            if self._toolbar:
                self._toolbar.lift()
                self._toolbar.focus_force()
        self._toolbar.after(150, _grab_focus)

        # Start polling mouse position
        self._poll_mouse()

    # ------------------------------------------------------------------
    # Mouse position polling
    # ------------------------------------------------------------------

    def _poll_mouse(self):
        """Update the coordinate display with current mouse position."""
        if self._toolbar is None:
            return
        try:
            x, y = pyautogui.position()
            self._coord_label.configure(text=f"Cursor: ({x}, {y})")
        except Exception:
            pass
        self._polling_id = self._toolbar.after(50, self._poll_mouse)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_capture(self, event):
        """Capture the current mouse position."""
        try:
            x, y = pyautogui.position()
        except Exception:
            return

        self._pick_count += 1
        self._count_label.configure(text=f"Saved: {self._pick_count}")

        # Flash the coordinate display
        color = DOT_COLORS[(self._pick_count - 1) % len(DOT_COLORS)]
        self._coord_label.configure(
            text=f"✓ Captured #{self._pick_count}: ({x}, {y})",
            fg=color,
        )

        if self._on_location_picked:
            self._on_location_picked(x, y)

        # Show a brief dot at the captured position
        self._show_capture_dot(x, y, self._pick_count)

    def _on_undo(self, event):
        """Signal undo — remove last captured location."""
        if self._pick_count > 0:
            self._pick_count -= 1
            self._count_label.configure(text=f"Saved: {self._pick_count}")
            self._coord_label.configure(
                text=f"Undone → {self._pick_count} remaining",
                fg="#e67e22",
            )
            # Notify main.py to remove last location
            if self._on_undo_callback:
                self._on_undo_callback()

    def _show_capture_dot(self, x, y, number):
        """Show a temporary colored dot at the captured position."""
        color = DOT_COLORS[(number - 1) % len(DOT_COLORS)]

        dot = tk.Toplevel(self._toolbar)
        dot.overrideredirect(True)
        dot.attributes("-topmost", True)
        dot.attributes("-transparentcolor", "#010101")
        dot.configure(bg="#010101")

        size = 52
        dot.geometry(f"{size}x{size}+{x - size // 2}+{y - size // 2}")

        canvas = tk.Canvas(dot, width=size, height=size,
                           bg="#010101", highlightthickness=0)
        canvas.pack()

        cx, cy = size // 2, size // 2
        r = 16

        # Glow ring
        canvas.create_oval(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4,
                           outline=color, width=2)
        # Filled circle
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=color, outline="white", width=2)
        # Number
        canvas.create_text(cx, cy, text=str(number),
                           font=("Segoe UI", 10, "bold"), fill="white")

        # Auto-destroy after 1.5 seconds
        dot.after(1500, dot.destroy)

    # ------------------------------------------------------------------
    # Dragging
    # ------------------------------------------------------------------

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self._toolbar.winfo_x() + event.x - self._drag_x
        y = self._toolbar.winfo_y() + event.y - self._drag_y
        self._toolbar.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _close(self):
        if self._polling_id:
            try:
                self._toolbar.after_cancel(self._polling_id)
            except Exception:
                pass
            self._polling_id = None
        if self._toolbar:
            self._toolbar.destroy()
            self._toolbar = None


class DryRunPreview:
    """
    Shows numbered colored dots at each click location for a few seconds,
    simulating the click sequence without actually clicking.
    """

    def __init__(self, parent):
        self._parent = parent
        self._windows: list[tk.Toplevel] = []
        self._after_ids: list[str] = []

    def show(self, locations: list[tuple[int, int]], interval_ms: int = 300, display_time_ms: int = 4000):
        """
        Display dots at each location sequentially, then clear after display_time_ms.

        Args:
            locations: List of (x, y) positions.
            interval_ms: Delay between each dot appearing (staggered reveal).
            display_time_ms: How long all dots stay visible after the last one appears.
        """
        if not locations:
            return

        self._cleanup()

        for i, (x, y) in enumerate(locations):
            delay = i * interval_ms
            after_id = self._parent.after(delay, self._spawn_dot, x, y, i + 1, len(locations))
            self._after_ids.append(after_id)

        # Schedule cleanup after all dots shown + display time
        total_time = len(locations) * interval_ms + display_time_ms
        cleanup_id = self._parent.after(total_time, self._cleanup)
        self._after_ids.append(cleanup_id)

    def _spawn_dot(self, x, y, number, total):
        """Create a small always-on-top dot window at the given position."""
        color = DOT_COLORS[(number - 1) % len(DOT_COLORS)]

        dot_win = tk.Toplevel(self._parent)
        dot_win.overrideredirect(True)
        dot_win.attributes("-topmost", True)

        # Transparent background (Windows)
        dot_win.attributes("-transparentcolor", "#010101")
        dot_win.configure(bg="#010101")

        size = 64
        dot_win.geometry(f"{size}x{size + 20}+{x - size // 2}+{y - size // 2}")

        canvas = tk.Canvas(dot_win, width=size, height=size + 20,
                           bg="#010101", highlightthickness=0)
        canvas.pack()

        cx, cy = size // 2, size // 2
        r = 18

        # Outer pulse ring
        canvas.create_oval(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6,
                           outline=color, width=2)
        # Main dot
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=color, outline="white", width=2)
        # Number
        canvas.create_text(cx, cy, text=str(number),
                           font=("Segoe UI", 11, "bold"), fill="white")
        # Coordinate text
        canvas.create_text(cx, cy + r + 12, text=f"({x},{y})",
                           font=("Consolas", 7), fill=color)

        self._windows.append(dot_win)

    def _cleanup(self):
        """Remove all dot windows and cancel pending timers."""
        for after_id in self._after_ids:
            try:
                self._parent.after_cancel(after_id)
            except Exception:
                pass
        self._after_ids.clear()

        for win in self._windows:
            try:
                win.destroy()
            except Exception:
                pass
        self._windows.clear()
