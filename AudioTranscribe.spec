# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Audio Transcribe portable build.

Generates a single executable (~120-150MB) with GUI mode.
Excludes Whisper/torch to keep size manageable.

Usage: pyinstaller AudioTranscribe.spec
"""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['floating_button_qt.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'sounddevice',
        'scipy',
        'scipy.io',
        'scipy.io.wavfile',
        'scipy.signal',
        'numpy',
        'httpx',
        'httpx._transports',
        'httpx._transports.default',
        'pyperclip',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'qtawesome',
        'rich',
        'rich.console',
        'dotenv',
        # App modules
        'transcription_controller',
        'transcription_service',
        'audio_recorder',
        'config',
        'settings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude Whisper and its heavy dependencies
        'whisper',
        'openai-whisper',
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'tokenizers',
        # Exclude test/dev modules
        'numpy.testing',
        'scipy.testing',
        'pytest',
        'unittest',
        'tkinter',
        '_tkinter',
        # Exclude unused PySide6 modules
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtBluetooth',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNetworkAuth',
        'PySide6.QtPositioning',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtRemoteObjects',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
        'PySide6.QtXml',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AudioTranscribe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=sys.platform != 'win32',  # Strip on Linux/macOS, not Windows
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=sys.platform == 'darwin',  # macOS argv emulation
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if desired
)
