# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('torch')
datas += copy_metadata('torchvision')
datas += copy_metadata('PySide6-Essentials')
datas += copy_metadata('shiboken6')
datas += copy_metadata('Pillow')
datas += copy_metadata('PyInstaller')
datas += copy_metadata('numpy')


a = Analysis(
    ['../../scripts/checks/phase0_smoke.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['torchvision._C_stable', 'torchvision.image_stable'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='phase0_smoke',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='phase0_smoke',
)
