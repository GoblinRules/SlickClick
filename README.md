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
- 👆 **Click type** — single or double click
- 📍 **Click targeting** — click at cursor position or fixed screen locations
- 🎯 **Location picker** — fullscreen crosshair overlay to pick coordinates
- 🔁 **Repeat control** — set a specific click count or click until stopped
- ⌨️ **Global hotkey** — F6 (default), fully reassignable
- 💾 **Persistent settings** — all settings saved automatically between sessions
- 🌙 **Dark theme** — modern, sleek interface with accent styling

## Quick Start

### Run from source
```bash
pip install -r requirements.txt
python -m slickclick.main
```

### Download

Pre-built binaries are available on the [Releases](https://github.com/GoblinRules/SlickClick/releases) page:

- **SlickClick_Setup_v1.1.0.exe** — Windows installer
- **SlickClick.exe** — Portable executable (no install needed)

## Usage

1. Set your desired click interval (HRS / MIN / SEC / MS)
2. Choose mouse button and click type from the dropdowns
3. Optionally pick fixed screen locations via 📍 or the ☰ menu
4. Set repeat count or "Until Stopped"
5. Press **F6** (or your custom hotkey) to start clicking
6. Press **F6** again to stop

> **Tip:** Your settings including the hotkey are automatically saved to `%APPDATA%\SlickClick\config.json` and restored on next launch.

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
5. Output: `installer_output/SlickClick_Setup_v1.1.0.exe`

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.x |
| GUI | tkinter + ttk |
| Mouse control | pyautogui |
| Global hotkeys | pynput |
| Packaging | PyInstaller |
| Installer | Inno Setup |

## Project Structure

```
SlickClick/
├── slickclick/
│   ├── main.py              # App controller — wires all components
│   ├── gui.py               # Tkinter GUI with dark theme
│   ├── clicker.py           # Click engine (pyautogui)
│   ├── hotkey.py            # Global hotkey listener (pynput)
│   ├── location_picker.py   # Fullscreen crosshair overlay
│   ├── config.py            # JSON settings persistence
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
