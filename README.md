# Audio Transcribe

Voice-to-text transcription tool with **floating panel** (GUI) or **global hotkey** (CLI). Uses **Groq API** (free and fast) as primary service and **local Whisper** as fallback.

---

Herramienta de transcripcion de voz a texto con **panel flotante** (GUI) o **hotkey global** (CLI). Usa **Groq API** (gratis y rapido) como servicio principal y **Whisper local** como fallback.

## Features / Caracteristicas

- **Floating Panel**: Vertical panel with Record, Pause, Cancel buttons (PySide6)
- **Modern Icons**: Material Design via QtAwesome
- **Bilingual Interface**: Spanish / English with persistent settings
- **Pause/Resume**: Pause recording and continue later
- **Cancel Recording**: Discard without transcribing
- **Groq API**: Fast, free cloud transcription (Whisper Large V3)
- **Whisper Fallback**: Automatic local fallback if Groq fails
- **Microphone Selection**: Choose your input device
- **Auto Clipboard**: Transcribed text copied automatically
- **Draggable**: Move panel anywhere on screen
- **Cross-platform**: Linux, Windows, macOS

## Panel Layout

```
┌──────────────┐
│      🎤      │  Record/Stop (green/red)
├──────────────┤
│      ⏸️      │  Pause/Resume (orange/green)
├──────────────┤
│      ✕       │  Cancel (gray/red)
├──────────────┤
│   ?  ⚙️  ⏻   │  Help | Settings | Exit
└──────────────┘
    Dark transparent background
```

## Button States / Estados

| State | Button | Color | Description |
|-------|--------|-------|-------------|
| Ready | Record | Green | Waiting to record |
| Recording | Stop | Red (pulse) | Recording audio |
| Paused | Resume | Green (pulse) | Recording paused |
| Processing | Spinner | Yellow (spin) | Transcribing |
| Success | Check | Green | Done, copied to clipboard |
| Error | Alert | Gray | Transcription failed |

## Requirements / Requisitos

- Python 3.10+
- Free account at [Groq](https://console.groq.com/) for API key

### System Dependencies

```bash
# Debian/Ubuntu
sudo apt install python3-venv python3-full libportaudio2 xclip

# For GUI on some systems
sudo apt install libxcb-cursor0
```

## Installation / Instalacion

```bash
# Clone
git clone https://github.com/luckberonne/audio-transcribe.git
cd audio-transcribe

# Give permissions
chmod +x start.sh run.py

# Run (installs dependencies automatically)
./start.sh
```

## Configuration / Configuracion

### Groq API Key (Required)

1. Create free account at [https://console.groq.com/](https://console.groq.com/)
2. Generate API Key
3. Configure:

```bash
# Option 1: Environment variable
export GROQ_API_KEY="your-api-key-here"

# Option 2: Add to ~/.bashrc (permanent)
echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (required) | Groq API key |
| `BUTTON_POSITION` | `bottom-right` | Position: top-left, top-right, bottom-left, bottom-right, center |
| `BUTTON_SIZE` | `50` | Button size in pixels |
| `TRANSCRIBE_HOTKEY` | `<ctrl>+<alt>+space` | Hotkey (CLI mode only) |
| `WHISPER_MODEL` | `small` | Local model: tiny, base, small, medium, large |
| `WHISPER_DEVICE` | `cuda` | Device: cuda or cpu |

### Persistent Settings

Language and microphone preferences are saved in `app_settings.json` (created automatically).

Change language via Settings button (gear icon) - changes apply immediately and persist across restarts.

## Usage / Uso

### GUI Mode (Floating Panel)

```bash
./start.sh
# or
./run.py
```

1. Select microphone in initial dialog
2. **Click** green button to start recording
3. Speak...
4. (Optional) **Click** orange button to pause/resume
5. **Click** red stop button to transcribe
6. Text is copied automatically to clipboard
7. **Drag** panel to move it
8. **Click** gear icon for settings (microphone, language)
9. **Click** ? icon for help
10. **Click** exit icon to quit

### CLI Mode (Hotkey)

```bash
./start.sh --cli
```

1. Select microphone from list
2. Press `Ctrl+Alt+Space` to start recording
3. Speak...
4. Press `Ctrl+Alt+Space` to stop and transcribe
5. Text appears in terminal and is copied to clipboard

## Project Structure / Estructura

```
audio-transcribe/
├── start.sh                    # Startup script
├── run.py                      # Launcher with auto-venv
├── floating_button_qt.py       # GUI (PySide6)
├── transcribe.py               # CLI (pynput)
├── transcription_controller.py # Shared logic
├── audio_recorder.py           # Audio capture
├── transcription_service.py    # Groq + Whisper
├── config.py                   # Configuration
├── settings.py                 # Persistent settings & translations
├── app_settings.json           # Saved preferences (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── CLAUDE.md                   # Guide for Claude Code
```

## Whisper Models (Fallback)

| Model | VRAM | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~1GB | Very fast | Low |
| base | ~1GB | Fast | Medium |
| **small** | ~2GB | Medium | Good (default) |
| medium | ~5GB | Slow | Very good |
| large | ~10GB | Very slow | Excellent |

## Troubleshooting

### Error: PortAudio library not found

```bash
sudo apt install libportaudio2
```

### Error: No microphones found

```bash
# Check PulseAudio/PipeWire
pactl list sources short

# Restart PipeWire
systemctl --user restart pipewire pipewire-pulse
```

### Error: xcb plugin not found (GUI)

```bash
sudo apt install libxcb-cursor0
```

### Error: CUDA not available

```bash
export WHISPER_DEVICE="cpu"
```

### Error: pyperclip not working

```bash
sudo apt install xclip
```

### USB/Bluetooth microphone not appearing

```bash
# Restart audio
systemctl --user restart pipewire pipewire-pulse

# Or disconnect/reconnect USB and verify
arecord -l
```

## License / Licencia

MIT License

## Contributing / Contribuciones

Pull requests are welcome. For major changes, please open an issue first.
