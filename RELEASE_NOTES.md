# SlickClick v1.2.3 🚀

**Patch release — fixes dialog freeze from v1.2.2.**

---

## 🐛 Fix

- **Fixed dialogs freezing the app** — Opening Click Options, Repeat Options, Settings, About, or any other dialog would freeze the entire application, requiring a force-close from Task Manager. Root cause: `grab_set()` on `overrideredirect(True)` windows creates a modal input lock on borderless windows that the OS can't properly deliver focus to, resulting in a deadlock. Replaced with `focus_force()` + `lift()`.

## 🔔 Features (from v1.2.2)

### Toast Notifications
- Dark, translucent slide-in popup in the bottom-right corner
- Shows "● Clicker Started" / "● Clicker Stopped"
- Auto-dismisses after 2 seconds with smooth fade-out
- Toggleable in Settings

### On-Screen Indicator (OSD)
- Persistent red "● CLICKING" pill in the top-right corner while running
- Click-through — never blocks clicking targets
- Pulsing dot animation
- Toggleable in Settings

### Check for Updates
- **⚙ → About → Check for Updates** queries GitHub Releases API
- Shows update status or a clickable download link

### Help / User Guide
- Built-in scrollable guide from **⚙ → Help / Guide**

### Styled Dialog Banners
- All dialogs now use the accent-colored banner bar matching Pick Locations
- Custom draggable title bar with close button

### Installer Version Info
- File properties now correctly show the app version (was 0.0.0.0)

## 📦 Downloads

| File | Description |
|---|---|
| `SlickClick_Setup_v1.2.3.exe` | Windows installer |
| `SlickClick.exe` | Portable executable (no install needed) |

### System Requirements
- Windows 10 or 11
- No admin privileges required

---

**Full Changelog:** https://github.com/GoblinRules/SlickClick/compare/V1.1.0...V1.2.3
