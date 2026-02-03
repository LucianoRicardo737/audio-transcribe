# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Voice-to-text transcription tool with two interfaces:
- **GUI**: Floating button (always-on-top) for mouse control
- **CLI**: Global hotkey support

Uses **Groq API** (free, fast) as primary service and **local Whisper** as fallback.

## Commands

```bash
# Run GUI (floating button) - default
./start.sh

# Run CLI (hotkey mode)
./start.sh --cli

# Manual run
source venv/bin/activate
python floating_button_qt.py  # GUI
python transcribe.py          # CLI

# Install dependencies manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │     TranscriptionController         │
                    │   (transcription_controller.py)     │
                    │  - Thread-safe callbacks            │
                    │  - State management (IDLE/REC/PROC) │
                    └─────────────┬───────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   FloatingButton    │ │ TranscribeApp   │ │  AudioRecorder  │
│(floating_button_qt) │ │ (transcribe.py) │ │(audio_recorder) │
│  - PySide6 GUI      │ │  - CLI/hotkey   │ │  - sounddevice  │
│  - Qt Signals/Slots │ │  - pynput       │ │  - scipy WAV    │
│  - QtAwesome icons  │ │                 │ │                 │
└─────────────────────┘ └─────────────────┘ └─────────────────┘
              │                   │
              └───────────────────┴───────────────────┐
                                                      ▼
                                        ┌─────────────────────┐
                                        │TranscriptionService │
                                        │ - Groq API (primary)│
                                        │ - Whisper (fallback)│
                                        └─────────────────────┘
```

**GUI Flow**: Click → Start recording → Click → Stop → Process → Copy to clipboard
**CLI Flow**: Hotkey → Start recording → Hotkey → Stop → Process → Copy to clipboard

## Configuration (config.py)

All settings via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (required) | API key from console.groq.com |
| `TRANSCRIBE_HOTKEY` | `<ctrl>+<alt>+space` | Global hotkey (CLI mode) |
| `TRANSCRIBE_LANGUAGE` | `es` | Language code |
| `WHISPER_MODEL` | `small` | Local fallback model |
| `WHISPER_DEVICE` | `cuda` | `cuda` or `cpu` |
| `BUTTON_POSITION` | `bottom-right` | GUI button position |
| `BUTTON_SIZE` | `50` | Button size in pixels |
| `BUTTON_OPACITY` | `0.9` | Button transparency (0-1) |

## Key Implementation Details

- **Controller pattern**: `TranscriptionController` separates logic from UI
- **Thread-safe callbacks**: Qt Signals/Slots for GUI updates from worker threads
- **Hotkey handling**: pynput keyboard listener with manual key combination tracking
- **Audio**: Records at device's native sample rate, resamples to 16000Hz for API
- **Clipboard**: Uses pyperclip (requires `xclip` system package)
- **Whisper**: Lazy-loaded only when Groq fails (saves memory/startup time)

## GUI Button States

| State | Color | Icon | Animation |
|-------|-------|------|-----------|
| IDLE | Green `#4CAF50` | Microphone | Static |
| RECORDING | Red `#f44336` | Stop | Pulse (scale) |
| PROCESSING | Yellow `#FFC107` | Loading | Spin |
| SUCCESS | Green `#4CAF50` | Check | Flash |
| ERROR | Gray `#78909C` | X | None |

## Files

- `floating_button_qt.py` - GUI application (PySide6) with floating button
- `transcribe.py` - CLI application with hotkey (pynput)
- `transcription_controller.py` - Shared orchestration logic
- `audio_recorder.py` - Audio capture (sounddevice)
- `transcription_service.py` - Groq/Whisper transcription
- `config.py` - Configuration
- `run.py` - Launcher with auto-venv activation
- `start.sh` - Shell script for setup and execution
