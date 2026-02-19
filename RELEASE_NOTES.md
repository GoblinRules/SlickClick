# SlickClick v1.1.0 🚀

**Reliability update — rebuilt hotkey system for guaranteed compatibility on all Windows machines.**

---

## 🔧 What's New

### Hotkey System Overhaul
- **Replaced pynput keyboard hooks** with the native **Windows `RegisterHotKey` API** via ctypes
- Hotkeys now work reliably on **all Windows machines**, including clean installs with no Python or extra dependencies
- Key capture for reassigning hotkeys now uses Tkinter native events — no third-party dependencies required

### Diagnostic Logging
- Added file-based logging to `%APPDATA%\SlickClick\slickclick.log`
- Logs hotkey registration, key presses, pyautogui initialization, and errors
- Makes troubleshooting on end-user machines much easier

### Settings Persistence
- All settings (hotkey, interval, mouse button, click type, repeat mode) are automatically saved to `%APPDATA%\SlickClick\config.json`
- Settings are restored on next launch — no more reconfiguring after every restart
- Hotkey changes persist immediately

### Landing Page Updates
- Added cookie consent banner with accept/decline
- Added software disclaimer in the footer
- Download links now point to GitHub Releases

### Other
- Added MIT License
- Updated README with comprehensive documentation and project structure
- Updated build configuration to use `python -m PyInstaller` for consistent builds

## 📦 Downloads

| File | Description |
|---|---|
| `SlickClick_Setup_v1.1.0.exe` | Windows installer |
| `SlickClick.exe` | Portable executable (no install needed) |

### System Requirements
- Windows 10 or 11
- No admin privileges required

## � Bug Fixes

- Fixed hotkeys not working on clean Windows machines (replaced pynput with native Windows API)
- Fixed PyInstaller build using wrong Python version (3.9 instead of 3.13)
- Fixed settings not persisting between sessions

---

**Full Changelog:** https://github.com/GoblinRules/SlickClick/compare/V1.0.0...V1.1.0
