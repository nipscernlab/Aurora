# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules
block_cipher = None

# Collect all scipy submodules to ensure Cython extensions are included
scipy_hidden = collect_submodules('scipy')

# Prepare datas
my_datas = []
if os.path.exists('assets'):
    my_datas.append(('assets', 'assets'))

# Prepare icon
app_icon = 'icon.ico' if os.path.exists('icon.ico') else None

# Analysis
a = Analysis(
    ['fractal_visualizer.py'],
    pathex=[],
    binaries=[],
    datas=my_datas,
    hiddenimports=[
        *scipy_hidden,
        'customtkinter',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Enhanced_Fractal_Visualizer',
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
    icon=app_icon,
)
