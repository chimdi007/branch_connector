# app.spec
# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

project_path = os.path.abspath('.')

# Include templates folder and files individually
datas = [
    ('requirements.txt', '.'),        # include requirements.txt
    ('config.txt', '.'),              # include config.txt
    ('templates/index.html', 'templates')  # include template file(s)
]

a = Analysis(
    ['app.py'],
    pathex=[project_path],
    binaries=[],
    datas=datas,
    hiddenimports=[
        '_socket',
        '_ssl',
        '_hashlib',
        '_multiprocessing',  # multiprocessing runtime
        'selectors',
        'errno',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[]
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='branch_connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    onefile=True
)
