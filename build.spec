# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for SlickClick."""

from PyInstaller.utils.hooks import collect_all

# Collect all submodules/data for packages that have platform-specific backends
pyautogui_datas, pyautogui_binaries, pyautogui_hiddenimports = collect_all('pyautogui')
pynput_datas, pynput_binaries, pynput_hiddenimports = collect_all('pynput')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=pyautogui_binaries + pynput_binaries,
    datas=[('assets/icon.ico', 'assets')] + pyautogui_datas + pynput_datas,
    hiddenimports=pyautogui_hiddenimports + pynput_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SlickClick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
