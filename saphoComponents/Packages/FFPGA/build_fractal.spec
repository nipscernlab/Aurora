# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# Coletar todos os submódulos necessários
hiddenimports = []
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('numpy')

# Adicionar imports específicos que podem não ser detectados
hiddenimports += [
    'tkinter',
    'tkinter.ttk',
    'customtkinter.windows',
    'customtkinter.widgets',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageFilter',
    'numpy.core._methods',
    'numpy.lib.format',
]

a = Analysis(
    ['fractal_visualizer.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Incluir arquivos de dados do customtkinter
        (os.path.join(os.path.dirname(__import__('customtkinter').__file__), 'assets'), 'customtkinter/assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos desnecessários para reduzir tamanho
        'matplotlib',
        'scipy.spatial.cKDTree',
        'scipy.special.cython_special',
        'test',
        'unittest',
        'pdb',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fancyFractal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compressão UPX para reduzir tamanho
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem console para interface gráfica
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione caminho para ícone se tiver: icon='icon.ico'
)