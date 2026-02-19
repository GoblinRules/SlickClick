# SlickClick v1.2.2 🚀

**Feature update — toast notifications, on-screen indicator, built-in help, styled dialogs, and update checking.**

---

## 🔔 New Features

### Toast Notifications
- Dark, translucent slide-in popup in the bottom-right corner
- Shows "● Clicker Started" (green) or "● Clicker Stopped" (red)
- Auto-dismisses after 2 seconds with a smooth fade-out
- Can be toggled on/off in Settings

### On-Screen Indicator (OSD)
- Persistent red "● CLICKING" pill in the top-right corner while the clicker is running
- Click-through — never interferes with clicking targets
- Pulsing dot animation to indicate activity
- Can be toggled on/off in Settings

### Check for Updates
- **⚙ → About → Check for Updates** queries the GitHub Releases API
- Shows "✓ You're up to date!" or a clickable link to download the new version
- Uses only Python stdlib (urllib, json) — no extra dependencies

### Help / User Guide
- Built-in scrollable guide accessible from **⚙ → Help / Guide**
- Covers all features: hotkeys, interval, click options, repeat modes, location targeting, notifications, settings persistence, and update checking

### Styled Dialog Banners
- All dialog windows (Settings, Click Options, Repeat Options, Saved Locations, About, Help) now use a styled accent banner bar matching the Pick Locations toolbar
- Custom title bar with drag support and close button
- Consistent look across the entire application

## 🐛 Fixes

- Fixed installer file version showing 0.0.0.0 (added `VersionInfoVersion` to ISS)
- Fixed GitHub URL in installer metadata

## 📦 Downloads

| File | Description |
|---|---|
| `SlickClick_Setup_v1.2.2.exe` | Windows installer |
| `SlickClick.exe` | Portable executable (no install needed) |

### System Requirements
- Windows 10 or 11
- No admin privileges required

---

**Full Changelog:** https://github.com/GoblinRules/SlickClick/compare/V1.1.0...V1.2.2
