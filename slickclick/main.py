"""SlickClick — Entry point. Wires the GUI, clicker engine, hotkey listener, and location picker."""

import tkinter as tk
import sys

from .logging_config import logger
from .gui import SlickClickGUI
from .clicker import ClickerEngine
from .hotkey import HotkeyListener
from .location_picker import LocationPicker, DryRunPreview
from .notifications import ToastNotification, OSDIndicator
from . import config


class SlickClickApp:
    """Application controller — connects all components."""

    def __init__(self):
        self.root = tk.Tk()
        self.gui = SlickClickGUI(self.root)
        self.engine = ClickerEngine()
        self.hotkey = HotkeyListener(on_toggle=self._toggle_clicking)
        self.picker = LocationPicker(self.root, on_location_picked=self._on_location_picked)
        self.dry_run = DryRunPreview(self.root)
        self.toast = ToastNotification(self.root)
        self.osd = OSDIndicator(self.root)

        # Wire callbacks
        self.engine.set_callbacks(
            on_status_change=self._on_status_change,
            on_click_count_update=self._on_click_count_update,
        )

        # Override GUI stub callbacks
        self.gui._on_start_btn = self._toggle_clicking
        self.gui._on_pick_location = self._open_picker
        self.gui._on_dry_run = self._run_dry_preview
        self.gui._on_set_hotkey = self._begin_hotkey_capture
        self.gui._on_close = self._on_close

        # Start hotkey listener
        logger.info("Starting hotkey listener...")
        self.hotkey.start()

        # Load saved settings
        self._load_settings()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        """Start the application."""
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _toggle_clicking(self):
        """Start or stop the clicker (called from hotkey or button)."""
        if self.engine.running:
            self.engine.stop()
        else:
            self.engine.start(
                locations=self.gui.get_locations(),
                interval_ms=self.gui.get_interval_ms(),
                repeat_count=self.gui.get_repeat_count(),
                mouse_button=self.gui.get_mouse_button(),
                click_type=self.gui.get_click_type(),
            )

    def _open_picker(self):
        """Open the floating location picker toolbar."""
        import traceback
        try:
            self.picker._on_undo_callback = self._on_picker_undo
            self.picker.show(existing_locations=self.gui._locations)
            print("[SlickClick] Picker opened successfully", flush=True)
        except Exception as e:
            print(f"[SlickClick] ERROR opening picker: {e}", flush=True)
            traceback.print_exc()

    def _run_dry_preview(self):
        """Run dry-run preview showing dots at all saved locations."""
        locations = self.gui._locations
        if not locations:
            return
        interval = self.gui.get_interval_ms()
        # Use the configured interval for staggering, capped between 200-1000ms for usability
        stagger = max(200, min(1000, interval))
        self.dry_run.show(locations, interval_ms=stagger, display_time_ms=4000)

    def _begin_hotkey_capture(self, dlg=None):
        """Enter hotkey capture mode."""
        if hasattr(self.gui, '_settings_hotkey_label') and self.gui._settings_hotkey_label.winfo_exists():
            self.gui._settings_hotkey_label.configure(text="Press a key...")
        if hasattr(self.gui, '_set_hotkey_btn') and self.gui._set_hotkey_btn.winfo_exists():
            self.gui._set_hotkey_btn.configure(state="disabled")
        self.hotkey.begin_capture(root=self.root, callback=self._on_hotkey_captured)

    # ------------------------------------------------------------------
    # Callbacks (may be called from background threads)
    # ------------------------------------------------------------------

    def _on_status_change(self, running: bool):
        """Thread-safe status update."""
        self.root.after(0, self._handle_status_change, running)

    def _handle_status_change(self, running: bool):
        """Update GUI, toast, and OSD on the main thread."""
        self.gui.update_status(running)
        # Toast notification
        if self.gui.show_toast.get():
            self.toast.show(running)
        # OSD indicator
        if self.gui.show_osd.get():
            if running:
                self.osd.show()
            else:
                self.osd.hide()
        elif not running:
            self.osd.hide()  # always hide when stopping

    def _on_click_count_update(self, count: int):
        """Thread-safe click count update (throttled)."""
        if count % 10 == 0 or count <= 10:
            self.root.after(0, self.gui.update_click_count, count)

    def _on_location_picked(self, x: int, y: int):
        """Called when user captures a position in the picker."""
        self.root.after(0, self.gui.add_location, x, y)

    def _on_picker_undo(self):
        """Called when user presses Ctrl+Z in the picker — remove last location."""
        if self.gui._locations:
            self.gui._locations.pop()
            self.gui._update_location_indicator()

    def _on_hotkey_captured(self, key_name: str):
        """Called when a new hotkey is captured."""
        self.root.after(0, self._apply_captured_hotkey, key_name)

    def _apply_captured_hotkey(self, key_name: str):
        self.gui.update_hotkey_display(key_name)
        self.hotkey.set_hotkey(key_name)
        if hasattr(self.gui, '_settings_hotkey_label'):
            try:
                self.gui._settings_hotkey_label.configure(text=key_name)
            except Exception:
                pass
        if hasattr(self.gui, '_set_hotkey_btn'):
            try:
                self.gui._set_hotkey_btn.configure(state="normal")
            except Exception:
                pass
        # Persist immediately
        self._save_settings()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _on_close(self):
        self._save_settings()
        self.engine.stop()
        self.hotkey.stop()
        self.root.destroy()
        sys.exit(0)

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------

    def _load_settings(self):
        """Load saved settings and apply to GUI + hotkey listener."""
        cfg = config.load()
        self.gui.hours_var.set(str(cfg.get("interval_hours", 0)))
        self.gui.mins_var.set(str(cfg.get("interval_mins", 0)))
        self.gui.secs_var.set(str(cfg.get("interval_secs", 0)))
        self.gui.ms_var.set(str(cfg.get("interval_ms", 100)))
        self.gui.button_var.set(cfg.get("mouse_button", "Left"))
        self.gui.type_var.set(cfg.get("click_type", "Single"))
        self.gui.repeat_mode.set(cfg.get("repeat_mode", "infinite"))
        self.gui.repeat_count_var.set(str(cfg.get("repeat_count", 50)))

        # Sync repeat display combo
        mode = cfg.get("repeat_mode", "infinite")
        if mode == "infinite":
            self.gui._repeat_display_var.set("Until Stopped")
        else:
            count = cfg.get("repeat_count", 50)
            preset = f"{count} times"
            presets = ["50 times", "100 times", "500 times"]
            if preset in presets:
                self.gui._repeat_display_var.set(preset)
            else:
                self.gui._repeat_display_var.set(f"{count} times")

        hotkey = cfg.get("hotkey", "F6")
        self.hotkey.set_hotkey(hotkey)
        self.gui.update_hotkey_display(hotkey)

        # Notification preferences
        self.gui.show_toast.set(cfg.get("show_toast", True))
        self.gui.show_osd.set(cfg.get("show_osd", True))

    def _save_settings(self):
        """Gather current state from GUI and save."""
        try:
            cfg = {
                "hotkey": self.gui._hotkey_name,
                "interval_hours": int(self.gui.hours_var.get() or 0),
                "interval_mins": int(self.gui.mins_var.get() or 0),
                "interval_secs": int(self.gui.secs_var.get() or 0),
                "interval_ms": int(self.gui.ms_var.get() or 0),
                "mouse_button": self.gui.button_var.get(),
                "click_type": self.gui.type_var.get(),
                "repeat_mode": self.gui.repeat_mode.get(),
                "repeat_count": int(self.gui.repeat_count_var.get() or 50),
                "show_toast": self.gui.show_toast.get(),
                "show_osd": self.gui.show_osd.get(),
            }
            config.save(cfg)
        except Exception:
            pass


def main():
    app = SlickClickApp()
    app.run()


if __name__ == "__main__":
    main()
