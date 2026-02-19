"""Core auto-clicker engine — runs clicks in a background thread."""

import threading
import time
import pyautogui

from .constants import MOUSE_BUTTON_MAP


class ClickerEngine:
    """Threaded auto-clicker that cycles through target locations."""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._click_count = 0
        self._running = False
        self._on_status_change = None
        self._on_click_count_update = None

        # Disable pyautogui fail-safe (mouse-to-corner abort)
        # Users control via hotkey instead
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_callbacks(self, on_status_change=None, on_click_count_update=None):
        """Register UI callbacks."""
        self._on_status_change = on_status_change
        self._on_click_count_update = on_click_count_update

    @property
    def running(self) -> bool:
        return self._running

    @property
    def click_count(self) -> int:
        return self._click_count

    def start(
        self,
        locations: list[tuple[int, int]],
        interval_ms: int,
        repeat_count: int,
        mouse_button: str,
        click_type: str,
    ):
        """
        Start clicking.

        Args:
            locations: List of (x, y) targets. Empty = click at current cursor.
            interval_ms: Delay between clicks in milliseconds.
            repeat_count: Number of clicks (0 = infinite).
            mouse_button: 'Left', 'Right', or 'Middle'.
            click_type: 'Single' or 'Double'.
        """
        if self._running:
            return

        self._stop_event.clear()
        self._click_count = 0
        self._running = True
        self._notify_status(True)

        self._thread = threading.Thread(
            target=self._click_loop,
            args=(locations, interval_ms, repeat_count, mouse_button, click_type),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        """Stop clicking."""
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        self._notify_status(False)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _click_loop(self, locations, interval_ms, repeat_count, mouse_button, click_type):
        button = MOUSE_BUTTON_MAP.get(mouse_button, "left")
        clicks = 2 if click_type == "Double" else 1
        interval_s = interval_ms / 1000.0
        use_locations = len(locations) > 0
        loc_index = 0

        while not self._stop_event.is_set():
            # Move to target location if configured
            if use_locations:
                x, y = locations[loc_index % len(locations)]
                pyautogui.moveTo(x, y)
                loc_index += 1

            # Perform click
            pyautogui.click(clicks=clicks, button=button)
            self._click_count += 1
            self._notify_click_count()

            # Check repeat limit
            if repeat_count > 0 and self._click_count >= repeat_count:
                break

            # Wait for the interval, but check stop event frequently
            # so we can respond quickly to stop requests
            if interval_s > 0:
                wait_end = time.perf_counter() + interval_s
                while time.perf_counter() < wait_end:
                    if self._stop_event.is_set():
                        break
                    time.sleep(min(0.01, interval_s))

        self._running = False
        self._notify_status(False)

    def _notify_status(self, running: bool):
        if self._on_status_change:
            try:
                self._on_status_change(running)
            except Exception:
                pass

    def _notify_click_count(self):
        if self._on_click_count_update:
            try:
                self._on_click_count_update(self._click_count)
            except Exception:
                pass
