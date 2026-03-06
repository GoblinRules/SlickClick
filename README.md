# SlickClick ⚡

<p align="center">
  <strong>A lightweight, modern auto-clicker for Windows.</strong><br>
  Free, open source, and built for speed.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#download">Download</a> •
  <a href="#building">Building</a> •
  <a href="#license">License</a>
</p>

---

## Features

- ⏱️ **Configurable click interval** — hours, minutes, seconds, milliseconds
- 🖱️ **Mouse button selection** — left, right, or middle click
- 👆 **Click type** — single, double, or triple click
- 📍 **Click targeting** — click at cursor position or fixed screen locations
- 🎯 **Location picker** — floating toolbar with live coordinates to pick targets
- 🔁 **Repeat control** — set a specific click count or click until stopped
- ⌨️ **Global hotkey** — F6 (default), fully reassignable via native Windows API
- 🔔 **Toast notifications** — on-screen alerts when clicker starts/stops
- 🔴 **On-screen indicator** — persistent "CLICKING" pill while running (click-through)
- 🔄 **Check for updates** — one-click update check via GitHub Releases API
- 📖 **Built-in help guide** — scrollable guide accessible from the app menu
- 💾 **Persistent settings** — all settings saved automatically between sessions
- 📐 **Resolution-aware** — Per-Monitor DPI awareness for crisp rendering on high-DPI displays
- ↔️ **Resizable window** — freely resize the main window; default size scales to your screen resolution
- ⏳ **Start delay** — configurable delay (0–60 seconds) with visual countdown before clicking begins
- 🌙 **Dark theme** — modern interface with accent-colored dialog banners

## Quick Start

### Run from source
```bash
pip install -r requirements.txt
python -m slickclick.main
```

### Download

Pre-built binaries are available on the [Releases](https://github.com/GoblinRules/SlickClick/releases) page:

- **SlickClick_Setup_v1.3.2.exe** — Windows installer
- **SlickClick.exe** — Portable executable (no install needed)

## Usage

1. Set your desired click interval (HRS / MIN / SEC / MS)
2. Choose mouse button and click type from **⚙ → Click Options**
3. Set repeat count or "Until Stopped" from **⚙ → Repeat Options**
4. Optionally pick fixed screen locations via **⚙ → Pick Locations**
5. Press **F6** (or your custom hotkey) to start clicking
6. Press **F6** again to stop

> **Tip:** Your settings including the hotkey are automatically saved to `%APPDATA%\SlickClick\config.json` and restored on next launch.

### Notifications

- **Toast notifications** pop up in the bottom-right corner when the clicker starts or stops
- **On-screen indicator (OSD)** shows a small red "CLICKING" pill in the top-right while running
- Both can be toggled on/off in **⚙ → Settings**

### Getting Help

Click **⚙ → Help / Guide** for a scrollable guide covering all features, or check **⚙ → About → Check for Updates** to see if a newer version is available.

## Building

### Standalone .exe
```bash
pip install pyinstaller
python -m PyInstaller build.spec --noconfirm
# Output: dist/SlickClick.exe
```

### Windows Installer
1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the .exe first with PyInstaller (above)
3. Open `installer.iss` in Inno Setup Compiler
4. Click **Build → Compile**
5. Output: `installer_output/SlickClick_Setup_v1.3.2.exe`

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| GUI | tkinter + ttk |
| Mouse control | pyautogui |
| Global hotkeys | Windows RegisterHotKey API (ctypes) |
| Notifications | Tkinter Toplevel + ctypes WS_EX_TRANSPARENT |
| Update checker | GitHub Releases API (urllib) |
| Packaging | PyInstaller |
| Installer | Inno Setup |

## Project Structure

```
SlickClick/
├── slickclick/
│   ├── main.py              # App controller — wires all components
│   ├── gui.py               # Tkinter GUI with dark theme & styled dialogs
│   ├── clicker.py           # Click engine (pyautogui)
│   ├── hotkey.py            # Global hotkey (Windows RegisterHotKey API)
│   ├── notifications.py     # Toast notifications & OSD indicator
│   ├── updater.py           # GitHub update checker
│   ├── location_picker.py   # Floating toolbar for picking coordinates
│   ├── config.py            # JSON settings persistence
│   ├── logging_config.py    # File-based diagnostic logging
│   └── constants.py         # Colors, defaults, paths
├── assets/
│   └── icon.ico             # Application icon
├── Site/                    # Landing page (static HTML/CSS/JS)
├── build.spec               # PyInstaller build config
├── installer.iss            # Inno Setup installer config
├── requirements.txt         # Python dependencies
└── LICENSE                  # MIT License
```

## Disclaimer

SlickClick is provided "as is" without warranty of any kind. Use of auto-clicker software may violate the terms of service of certain applications, games, or websites. The developers are not responsible for any consequences resulting from misuse. This tool is intended for legitimate productivity and accessibility purposes only.

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/GoblinRules">GoblinRules</a>
</p>
