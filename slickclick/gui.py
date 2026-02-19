"""SlickClick GUI — Modern inline-controls layout matching the landing page design."""

import ctypes
import sys
import tkinter as tk
from tkinter import ttk

from .constants import (
    APP_NAME,
    APP_VERSION,
    COLORS,
    ICON_PATH,
    MOUSE_BUTTONS,
    CLICK_TYPES,
    DEFAULT_INTERVAL_MS,
    DEFAULT_HOTKEY,
)


class SlickClickGUI:
    """Modern main window with all controls visible inline."""

    def __init__(self, root: tk.Tk):
        self.root = root

        # Settings state (persisted across dialog opens)
        self.button_var = tk.StringVar(value="Left")
        self.type_var = tk.StringVar(value="Single")
        self.freeze_var = tk.BooleanVar(value=False)
        self.repeat_mode = tk.StringVar(value="infinite")
        self.repeat_count_var = tk.StringVar(value="50")
        self.hours_var = tk.StringVar(value="0")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        self.ms_var = tk.StringVar(value=str(DEFAULT_INTERVAL_MS))
        self.target_mode = tk.StringVar(value="cursor")
        self._locations: list[tuple[int, int]] = []
        self._hotkey_name = DEFAULT_HOTKEY

        # Display var for the inline repeat combo
        self._repeat_display_var = tk.StringVar(value="Until Stopped")
        self._repeat_display_var.trace_add("write", self._on_repeat_display_changed)

        self._setup_window()
        self._build_main_content()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self):
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("460x520")
        self.root.minsize(420, 490)
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_dark"])
        try:
            self.root.iconbitmap(ICON_PATH)
        except Exception:
            pass

        # ── Dark title bar (Windows 10 1809+ / Windows 11) ───
        self._apply_dark_title_bar()

        # ── ttk dark theme styling ───────────────────────────
        style = ttk.Style()
        style.theme_use("clam")  # clam allows full color customization

        # Combobox styling
        style.configure(
            "Dark.TCombobox",
            fieldbackground=COLORS["input_bg"],
            background=COLORS["button_bg"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_secondary"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            selectbackground=COLORS["bg_light"],
            selectforeground=COLORS["text_primary"],
            padding=(8, 6),
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", COLORS["input_bg"])],
            foreground=[("readonly", COLORS["text_primary"])],
            selectbackground=[("readonly", COLORS["input_bg"])],
            selectforeground=[("readonly", COLORS["text_primary"])],
            background=[("active", COLORS["button_hover"]),
                        ("pressed", COLORS["button_hover"])],
            bordercolor=[("focus", COLORS["accent_dim"])],
        )

        # Combobox dropdown listbox (requires option_add)
        self.root.option_add("*TCombobox*Listbox.background", COLORS["input_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", COLORS["text_primary"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", COLORS["bg_light"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", COLORS["text_primary"])
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 11))

    # ------------------------------------------------------------------
    # Dark title bar (Windows DWM API)
    # ------------------------------------------------------------------

    def _apply_dark_title_bar(self):
        """Use Windows DWM API to enable dark title bar and window border."""
        if sys.platform != "win32":
            return
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (Windows 10 20H1+)
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value), ctypes.sizeof(value),
            )
            # DWMWA_BORDER_COLOR = 34 (Windows 11)
            try:
                DWMWA_BORDER_COLOR = 34
                # Convert #1a1a2e → 0x002E1A1A (COLORREF = 0x00BBGGRR)
                border_colorref = ctypes.c_int(0x002E1A1A)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_BORDER_COLOR,
                    ctypes.byref(border_colorref), ctypes.sizeof(border_colorref),
                )
            except Exception:
                pass
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Context menu (replaces classic menu bar)
    # ------------------------------------------------------------------

    _MENU_OPTS = dict(
        tearoff=0, bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
        activebackground=COLORS["accent"], activeforeground="white",
        borderwidth=0, relief="flat",
        activeborderwidth=0, font=("Segoe UI", 9),
    )

    def _show_gear_menu(self, event):
        """Show context menu from the gear icon."""
        menu = tk.Menu(self.root, **self._MENU_OPTS)

        # Clicking options
        menu.add_command(label="  ⚡  Click Options...", command=self._open_clicking_options)
        menu.add_command(label="  🔁  Repeat Options...", command=self._open_repeat_options)
        menu.add_separator()
        menu.add_command(label="  📍  Pick Locations...", command=lambda: self._on_pick_location())
        menu.add_command(label="  👁  View Locations...", command=self._open_locations_viewer)
        menu.add_command(label="  ▶  Dry Run Preview", command=lambda: self._on_dry_run())
        menu.add_command(label="  🗑  Clear Locations", command=lambda: self._on_clear_locations())
        menu.add_separator()
        menu.add_command(label="  ⚙  Settings...", command=self._open_settings)
        menu.add_command(label="  ℹ  About", command=self._show_about)
        menu.add_separator()
        menu.add_command(label="  ✕  Exit", command=lambda: self._on_close())

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # ------------------------------------------------------------------
    # Main window content — inline controls matching landing page mockup
    # ------------------------------------------------------------------

    def _build_main_content(self):
        # Card container
        card = tk.Frame(self.root, bg=COLORS["bg_card"])
        card.pack(fill="both", expand=True, padx=14, pady=(10, 14))

        # ── Accent top line ──────────────────────────────────
        accent_line = tk.Frame(card, bg=COLORS["accent"], height=3)
        accent_line.pack(fill="x")

        # ── Header row: app name + gear icon ─────────────────
        header = tk.Frame(card, bg=COLORS["bg_card"])
        header.pack(fill="x", padx=20, pady=(12, 4))

        tk.Label(
            header, text=APP_NAME, font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
        ).pack(side="left")

        tk.Label(
            header, text=f"v{APP_VERSION}", font=("Segoe UI", 8),
            fg=COLORS["text_muted"], bg=COLORS["bg_card"],
        ).pack(side="left", padx=(6, 0), pady=(2, 0))

        # Quick-access icons (right-aligned, before hamburger)
        gear_btn = tk.Label(
            header, text="☰", font=("Segoe UI", 14),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            cursor="hand2",
        )
        gear_btn.pack(side="right")
        gear_btn.bind("<Button-1>", self._show_gear_menu)
        self._add_hover(gear_btn, COLORS["text_primary"], COLORS["text_secondary"])

        # Settings shortcut
        settings_btn = tk.Label(
            header, text="⚙", font=("Segoe UI", 13),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            cursor="hand2", padx=4,
        )
        settings_btn.pack(side="right")
        settings_btn.bind("<Button-1>", lambda e: self._open_settings())
        self._add_hover(settings_btn, COLORS["accent"], COLORS["text_secondary"])

        # Pick locations shortcut
        loc_btn = tk.Label(
            header, text="📍", font=("Segoe UI", 11),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            cursor="hand2", padx=4,
        )
        loc_btn.pack(side="right")
        loc_btn.bind("<Button-1>", lambda e: self._on_pick_location())
        self._add_hover(loc_btn, COLORS["accent"], COLORS["text_secondary"])

        pad_x = 20  # horizontal padding inside the card

        # Thin separator
        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", padx=pad_x, pady=(6, 0))

        # ── Click Interval ────────────────────────────────────
        self._make_section_label(card, "CLICK INTERVAL", pad_x, (16, 6))

        interval_frame = tk.Frame(card, bg=COLORS["bg_card"])
        interval_frame.pack(fill="x", padx=pad_x, pady=(0, 12))

        self._interval_entries: dict[str, tk.Entry] = {}
        for i, (var, label, is_accent) in enumerate([
            (self.hours_var, "HRS", False),
            (self.mins_var, "MIN", False),
            (self.secs_var, "SEC", False),
            (self.ms_var, "MS", True),
        ]):
            col = tk.Frame(interval_frame, bg=COLORS["bg_card"])
            col.pack(side="left", expand=True, fill="x", padx=(0 if i == 0 else 6, 0))

            border_color = COLORS["accent_dim"] if is_accent else COLORS["border"]
            text_color = COLORS["accent"] if is_accent else COLORS["text_primary"]

            entry_border = tk.Frame(col, bg=border_color, bd=0)
            entry_border.pack(fill="x")

            entry = tk.Entry(
                entry_border, textvariable=var, font=("Segoe UI", 18, "bold"),
                bg=COLORS["input_bg"], fg=text_color,
                insertbackground=text_color, justify="center",
                relief="flat", borderwidth=0, width=4,
            )
            entry.pack(padx=2, pady=2, fill="x", ipady=6)
            self._interval_entries[label] = entry

            tk.Label(
                col, text=label, font=("Segoe UI", 7, "bold"),
                fg=COLORS["text_muted"], bg=COLORS["bg_card"],
            ).pack(pady=(3, 0))

        # ── Mouse Button + Click Type ─────────────────────────
        row1 = tk.Frame(card, bg=COLORS["bg_card"])
        row1.pack(fill="x", padx=pad_x, pady=(0, 12))

        # Mouse Button
        btn_col = tk.Frame(row1, bg=COLORS["bg_card"])
        btn_col.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._make_section_label(btn_col, "MOUSE BUTTON", 0, (0, 4))
        self._make_styled_combo(btn_col, self.button_var, MOUSE_BUTTONS)

        # Click Type
        type_col = tk.Frame(row1, bg=COLORS["bg_card"])
        type_col.pack(side="left", expand=True, fill="x", padx=(6, 0))
        self._make_section_label(type_col, "CLICK TYPE", 0, (0, 4))
        self._make_styled_combo(type_col, self.type_var, CLICK_TYPES)

        # ── Repeat + Hotkey ───────────────────────────────────
        row2 = tk.Frame(card, bg=COLORS["bg_card"])
        row2.pack(fill="x", padx=pad_x, pady=(0, 14))

        # Repeat
        rep_col = tk.Frame(row2, bg=COLORS["bg_card"])
        rep_col.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self._make_section_label(rep_col, "REPEAT", 0, (0, 4))
        self._make_styled_combo(
            rep_col, self._repeat_display_var,
            ["Until Stopped", "50 times", "100 times", "500 times", "Custom..."],
        )

        # Hotkey badge
        hk_col = tk.Frame(row2, bg=COLORS["bg_card"])
        hk_col.pack(side="left", expand=True, fill="x", padx=(6, 0))
        self._make_section_label(hk_col, "HOTKEY", 0, (0, 4))

        hk_border = tk.Frame(hk_col, bg=COLORS["accent_dim"])
        hk_border.pack(fill="x")

        self.hotkey_badge = tk.Label(
            hk_border, text=self._hotkey_name, font=("Segoe UI", 13, "bold"),
            fg=COLORS["accent"], bg=COLORS["input_bg"],
            pady=6, cursor="hand2",
        )
        self.hotkey_badge.pack(fill="x", padx=1, pady=1)
        self.hotkey_badge.bind("<Button-1>", lambda e: self._on_set_hotkey())

        # ── Status bar ────────────────────────────────────────
        status_frame = tk.Frame(card, bg=COLORS["bg_medium"])
        status_frame.pack(fill="x", padx=pad_x, pady=(0, 14))

        status_inner = tk.Frame(status_frame, bg=COLORS["bg_medium"])
        status_inner.pack(fill="x", padx=12, pady=8)

        self.status_label = tk.Label(
            status_inner, text="● Stopped", font=("Segoe UI", 9),
            fg=COLORS["text_muted"], bg=COLORS["bg_medium"], anchor="w",
        )
        self.status_label.pack(side="left")

        self.count_label = tk.Label(
            status_inner, text="Clicks: 0", font=("Segoe UI", 9),
            fg=COLORS["text_muted"], bg=COLORS["bg_medium"], anchor="e",
        )
        self.count_label.pack(side="right")

        # ── Start Button ──────────────────────────────────────
        self.start_btn = tk.Button(
            card, text="▶ Start", font=("Segoe UI", 12, "bold"),
            bg=COLORS["accent"], fg="white",
            activebackground=COLORS["accent_hover"], activeforeground="white",
            relief="flat", borderwidth=0, cursor="hand2",
            pady=10, command=lambda: self._on_start_btn(),
        )
        self.start_btn.pack(fill="x", padx=pad_x, pady=(0, 20))

        # Location indicator (below the card)
        self.location_indicator = tk.Label(
            self.root, text="Target: Cursor position",
            font=("Segoe UI", 8), fg=COLORS["text_muted"],
            bg=COLORS["bg_dark"], anchor="center",
        )
        self.location_indicator.pack(fill="x", padx=16, pady=(2, 8))

        # Hidden label kept for API compat (update_hotkey_display references it)
        self.hotkey_display = self.hotkey_badge

    # ------------------------------------------------------------------
    # UI builder helpers
    # ------------------------------------------------------------------

    def _make_section_label(self, parent, text, padx, pady):
        """Small uppercase section label."""
        lbl = tk.Label(
            parent, text=text, font=("Segoe UI", 7, "bold"),
            fg=COLORS["text_muted"], bg=COLORS["bg_card"],
            anchor="w",
        )
        lbl.pack(fill="x", padx=padx, pady=pady)
        return lbl

    def _make_styled_combo(self, parent, var, values):
        """Styled dropdown matching the dark theme."""
        combo = ttk.Combobox(
            parent, textvariable=var, values=values,
            state="readonly", font=("Segoe UI", 11),
            style="Dark.TCombobox",
        )
        combo.pack(fill="x")
        return combo

    @staticmethod
    def _add_hover(widget, hover_fg, normal_fg):
        """Add hover color effect to a widget."""
        widget.bind("<Enter>", lambda e: widget.configure(fg=hover_fg))
        widget.bind("<Leave>", lambda e: widget.configure(fg=normal_fg))

    def _on_repeat_display_changed(self, *_args):
        """Sync the display combo to the internal repeat vars."""
        val = self._repeat_display_var.get()
        if val == "Until Stopped":
            self.repeat_mode.set("infinite")
        elif val == "Custom...":
            self._open_repeat_options()
        else:
            # Parse "50 times" → 50
            try:
                count = int(val.split()[0])
                self.repeat_mode.set("finite")
                self.repeat_count_var.set(str(count))
            except (ValueError, IndexError):
                self.repeat_mode.set("infinite")

    # ------------------------------------------------------------------
    # Dialog: Clicking Options (Mouse button, click type, freeze pointer)
    # ------------------------------------------------------------------

    def _open_clicking_options(self):
        dlg = self._make_dialog("Clicking options", 280, 200)

        body = tk.Frame(dlg, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Mouse button
        row1 = tk.Frame(body, bg=COLORS["bg_card"])
        row1.pack(fill="x", pady=(0, 8))
        tk.Label(row1, text="Mouse:", font=("Segoe UI", 10, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 10))
        btn_combo = ttk.Combobox(row1, textvariable=self.button_var, values=MOUSE_BUTTONS,
                                  state="readonly", width=10)
        btn_combo.pack(side="left")

        # Click type
        row2 = tk.Frame(body, bg=COLORS["bg_card"])
        row2.pack(fill="x", pady=(0, 8))
        tk.Label(row2, text="Click:", font=("Segoe UI", 10, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 16))
        type_combo = ttk.Combobox(row2, textvariable=self.type_var, values=CLICK_TYPES,
                                   state="readonly", width=10)
        type_combo.pack(side="left")

        # Freeze pointer checkbox
        freeze_cb = tk.Checkbutton(
            body, text="Freeze the pointer (only single click)",
            variable=self.freeze_var,
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            selectcolor=COLORS["input_bg"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_secondary"],
        )
        freeze_cb.pack(anchor="w", pady=(4, 10))

        # OK / Cancel buttons
        self._make_dialog_buttons(dlg, body, on_ok=lambda: dlg.destroy())

    # ------------------------------------------------------------------
    # Dialog: Repeat / Interval settings
    # ------------------------------------------------------------------

    def _open_repeat_options(self):
        dlg = self._make_dialog("Clicking repeat", 360, 230)

        body = tk.Frame(dlg, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Repeat N times
        r1_frame = tk.Frame(body, bg=COLORS["bg_card"])
        r1_frame.pack(fill="x", pady=(0, 4))

        tk.Radiobutton(
            r1_frame, text="Repeat", variable=self.repeat_mode, value="finite",
            font=("Segoe UI", 10, "bold"), fg=COLORS["text_primary"], bg=COLORS["bg_card"],
            selectcolor=COLORS["input_bg"], activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
        ).pack(side="left")

        repeat_spin = tk.Spinbox(
            r1_frame, from_=1, to=999999, width=6, textvariable=self.repeat_count_var,
            font=("Segoe UI", 10), bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            buttonbackground=COLORS["button_bg"], relief="solid", borderwidth=1,
            highlightthickness=0,
        )
        repeat_spin.pack(side="left", padx=6)

        tk.Label(r1_frame, text="times", font=("Segoe UI", 10),
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(side="left")

        # Repeat until stopped
        tk.Radiobutton(
            body, text="Repeat until stopped", variable=self.repeat_mode, value="infinite",
            font=("Segoe UI", 10), fg=COLORS["text_primary"], bg=COLORS["bg_card"],
            selectcolor=COLORS["input_bg"], activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 12))

        # Interval row
        interval_frame = tk.Frame(body, bg=COLORS["bg_card"])
        interval_frame.pack(fill="x", pady=(0, 10))

        tk.Label(interval_frame, text="Interval:", font=("Segoe UI", 10, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))

        for var, label, width in [
            (self.hours_var, "hours", 3),
            (self.mins_var, "mins", 3),
            (self.secs_var, "secs", 3),
            (self.ms_var, "milliseconds", 5),
        ]:
            spin = tk.Spinbox(
                interval_frame, from_=0, to=999 if label == "milliseconds" else 59,
                width=width, textvariable=var, font=("Segoe UI", 10),
                bg=COLORS["input_bg"], fg=COLORS["text_primary"],
                buttonbackground=COLORS["button_bg"], relief="solid", borderwidth=1,
                highlightthickness=0,
            )
            spin.pack(side="left", padx=(0, 2))
            tk.Label(interval_frame, text=label, font=("Segoe UI", 8),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 6))

        # OK / Cancel
        self._make_dialog_buttons(dlg, body, on_ok=lambda: dlg.destroy())

    # ------------------------------------------------------------------
    # Dialog: Settings (Hotkey configuration)
    # ------------------------------------------------------------------

    def _open_settings(self):
        dlg = self._make_dialog("Settings", 300, 160)

        body = tk.Frame(dlg, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Current hotkey
        row = tk.Frame(body, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=(0, 8))

        tk.Label(row, text="Hotkey:", font=("Segoe UI", 10, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 10))

        self._settings_hotkey_label = tk.Label(
            row, text=self._hotkey_name, font=("Segoe UI", 12, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg_card"],
        )
        self._settings_hotkey_label.pack(side="left", padx=(0, 10))

        self._set_hotkey_btn = tk.Button(
            row, text="Change...", command=lambda: self._on_set_hotkey(dlg),
            font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"], activeforeground=COLORS["text_primary"],
            relief="flat", borderwidth=0, padx=10, pady=3,
        )
        self._set_hotkey_btn.pack(side="left")

        # Target mode
        target_frame = tk.Frame(body, bg=COLORS["bg_card"])
        target_frame.pack(fill="x", pady=(4, 10))

        tk.Label(target_frame, text="Click at:", font=("Segoe UI", 10, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 10))

        tk.Radiobutton(
            target_frame, text="Cursor", variable=self.target_mode, value="cursor",
            font=("Segoe UI", 9), fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            selectcolor=COLORS["input_bg"], activebackground=COLORS["bg_card"],
        ).pack(side="left", padx=(0, 6))

        locs_text = f"Fixed ({len(self._locations)})"
        self._fixed_radio_text = tk.StringVar(value=locs_text)

        tk.Radiobutton(
            target_frame, textvariable=self._fixed_radio_text,
            variable=self.target_mode, value="fixed",
            font=("Segoe UI", 9), fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
            selectcolor=COLORS["input_bg"], activebackground=COLORS["bg_card"],
        ).pack(side="left")

        # OK / Cancel
        self._make_dialog_buttons(dlg, body, on_ok=lambda: dlg.destroy())

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    def _show_about(self):
        dlg = self._make_dialog("About SlickClick", 280, 150)

        body = tk.Frame(dlg, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(body, text=f"⚡ {APP_NAME}", font=("Segoe UI", 14, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg_card"]).pack(pady=(0, 4))
        tk.Label(body, text=f"Version {APP_VERSION}", font=("Segoe UI", 10),
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack()
        tk.Label(body, text="Automatic Mouse Clicker", font=("Segoe UI", 9),
                 fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(pady=(4, 0))

        tk.Button(
            body, text="OK", command=dlg.destroy,
            font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"], relief="flat", padx=20, pady=3,
        ).pack(pady=(10, 0))

    # ------------------------------------------------------------------
    # Dialog helpers
    # ------------------------------------------------------------------

    def _make_dialog(self, title: str, width: int, height: int) -> tk.Toplevel:
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry(f"{width}x{height}")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS["bg_card"])
        dlg.transient(self.root)
        dlg.grab_set()

        # Center on parent
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dlg.geometry(f"+{x}+{y}")

        try:
            dlg.iconbitmap(ICON_PATH)
        except Exception:
            pass

        return dlg

    def _make_dialog_buttons(self, dlg, parent, on_ok=None):
        btn_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=(6, 0))

        tk.Button(
            btn_frame, text="Ok", command=on_ok or dlg.destroy,
            font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"], activeforeground=COLORS["text_primary"],
            relief="flat", borderwidth=0, padx=16, pady=3,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame, text="Cancel", command=dlg.destroy,
            font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"], activeforeground=COLORS["text_primary"],
            relief="flat", borderwidth=0, padx=16, pady=3,
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Value getters (used by main.py)
    # ------------------------------------------------------------------

    def get_interval_ms(self) -> int:
        try:
            h = int(self.hours_var.get())
            m = int(self.mins_var.get())
            s = int(self.secs_var.get())
            ms = int(self.ms_var.get())
            return (h * 3600 + m * 60 + s) * 1000 + ms
        except ValueError:
            return DEFAULT_INTERVAL_MS

    def get_repeat_count(self) -> int:
        if self.repeat_mode.get() == "infinite":
            return 0
        try:
            return max(1, int(self.repeat_count_var.get()))
        except ValueError:
            return 10

    def get_locations(self) -> list[tuple[int, int]]:
        if self.target_mode.get() == "cursor":
            return []
        return list(self._locations)

    def get_mouse_button(self) -> str:
        return self.button_var.get()

    def get_click_type(self) -> str:
        return self.type_var.get()

    # ------------------------------------------------------------------
    # Location management
    # ------------------------------------------------------------------

    def add_location(self, x: int, y: int):
        self._locations.append((x, y))
        self.target_mode.set("fixed")
        self._update_location_indicator()

    def remove_location(self, index: int):
        """Remove a location by index."""
        if 0 <= index < len(self._locations):
            self._locations.pop(index)
            self._update_location_indicator()

    def _update_location_indicator(self):
        """Update the location count label in the main window."""
        count = len(self._locations)
        if count == 0 or self.target_mode.get() == "cursor":
            self.location_indicator.configure(
                text="Target: Cursor position",
                fg=COLORS["text_muted"],
            )
        else:
            self.location_indicator.configure(
                text=f"Target: {count} fixed location{'s' if count != 1 else ''}  ●",
                fg=COLORS["accent"],
            )

    # ------------------------------------------------------------------
    # Status updates (called thread-safe via root.after)
    # ------------------------------------------------------------------

    def update_status(self, running: bool):
        if running:
            self.status_label.configure(text="● Running", fg=COLORS["success"])
            self.start_btn.configure(
                text="■ Stop",
                bg=COLORS["success"],
                activebackground="#27ae60",
            )
        else:
            self.status_label.configure(text="● Stopped", fg=COLORS["text_muted"])
            self.start_btn.configure(
                text="▶ Start",
                bg=COLORS["accent"],
                activebackground=COLORS["accent_hover"],
            )

    def update_click_count(self, count: int):
        self.count_label.configure(text=f"Clicks: {count:,}")

    def update_hotkey_display(self, key_name: str):
        self._hotkey_name = key_name
        self.hotkey_badge.configure(text=key_name)

    # ------------------------------------------------------------------
    # Stub callbacks (overridden by main.py)
    # ------------------------------------------------------------------

    def _on_start_btn(self):
        pass

    def _on_pick_location(self):
        pass

    def _on_dry_run(self):
        pass

    def _on_clear_locations(self):
        self._locations.clear()
        self._update_location_indicator()

    def _on_set_hotkey(self, dlg=None):
        pass

    def _on_close(self):
        pass

    # ------------------------------------------------------------------
    # Dialog: View Locations list
    # ------------------------------------------------------------------

    def _open_locations_viewer(self):
        """Dialog showing all saved click locations with remove buttons."""
        count = len(self._locations)
        height = min(350, 120 + count * 24)
        dlg = self._make_dialog(f"Saved Locations ({count})", 320, max(160, height))

        body = tk.Frame(dlg, bg=COLORS["bg_card"])
        body.pack(fill="both", expand=True, padx=16, pady=12)

        if count == 0:
            tk.Label(
                body, text="No locations saved.\n\nUse Options → Recording → Pick Locations\nto add click targets.",
                font=("Segoe UI", 10), fg=COLORS["text_muted"], bg=COLORS["bg_card"],
                justify="center",
            ).pack(expand=True)
        else:
            # Scrollable list
            list_frame = tk.Frame(body, bg=COLORS["bg_card"])
            list_frame.pack(fill="both", expand=True)

            listbox = tk.Listbox(
                list_frame, height=min(10, count),
                bg=COLORS["listbox_bg"], fg=COLORS["text_primary"],
                selectbackground=COLORS["listbox_select"],
                selectforeground=COLORS["text_primary"],
                font=("Consolas", 10), borderwidth=1, relief="solid",
                highlightthickness=0,
            )
            listbox.pack(side="left", fill="both", expand=True)

            scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)

            for i, (x, y) in enumerate(self._locations):
                listbox.insert("end", f"  #{i + 1}:  ({x}, {y})")

            # Remove button
            btn_frame = tk.Frame(body, bg=COLORS["bg_card"])
            btn_frame.pack(fill="x", pady=(8, 0))

            def remove_selected():
                sel = listbox.curselection()
                if sel:
                    idx = sel[0]
                    self.remove_location(idx)
                    listbox.delete(idx)
                    dlg.title(f"Saved Locations ({len(self._locations)})")

            tk.Button(
                btn_frame, text="Remove Selected", command=remove_selected,
                font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
                activebackground=COLORS["button_hover"], relief="flat", padx=10, pady=3,
            ).pack(side="left", padx=(0, 8))

            tk.Button(
                btn_frame, text="Dry Run Preview", command=lambda: (dlg.destroy(), self._on_dry_run()),
                font=("Segoe UI", 9), bg=COLORS["accent_dim"], fg="white",
                activebackground=COLORS["accent"], relief="flat", padx=10, pady=3,
            ).pack(side="left")

        tk.Button(
            body, text="Close", command=dlg.destroy,
            font=("Segoe UI", 9), bg=COLORS["button_bg"], fg=COLORS["text_primary"],
            activebackground=COLORS["button_hover"], relief="flat", padx=16, pady=3,
        ).pack(pady=(8, 0))
