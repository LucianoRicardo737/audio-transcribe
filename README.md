# Audio Transcribe

Herramienta de transcripcion de voz a texto con **panel flotante** (GUI) o **hotkey global** (CLI). Usa **Groq API** (gratis y rapido) como servicio principal y **Whisper local** como fallback.

---

# Espanol

## Caracteristicas

- **Panel Flotante**: Panel vertical con botones Grabar, Pausar, Cancelar (PySide6)
- **Iconos Modernos**: Material Design via QtAwesome
- **Interfaz Bilingue**: Espanol / Ingles con configuracion persistente
- **Pausar/Reanudar**: Pausa la grabacion y continua despues
- **Cancelar Grabacion**: Descarta sin transcribir
- **Groq API**: Transcripcion rapida y gratuita en la nube (Whisper Large V3)
- **Whisper Fallback**: Fallback local automatico si Groq falla
- **Seleccion de Microfono**: Elige tu dispositivo de entrada
- **Portapapeles Automatico**: El texto transcrito se copia automaticamente
- **Arrastrable**: Mueve el panel a cualquier lugar de la pantalla
- **Multiplataforma**: Linux, Windows, macOS

## Diseno del Panel

```
┌──────────────┐
│      🎤      │  Grabar/Detener (verde/rojo)
├──────────────┤
│      ⏸️      │  Pausar/Reanudar (naranja/verde)
├──────────────┤
│      ✕       │  Cancelar (gris/rojo)
├──────────────┤
│   ?  ⚙️  ⏻   │  Ayuda | Opciones | Salir
└──────────────┘
    Fondo oscuro transparente
```

## Estados de los Botones

| Estado | Boton | Color | Descripcion |
|--------|-------|-------|-------------|
| Listo | Grabar | Verde | Esperando para grabar |
| Grabando | Detener | Rojo (pulso) | Grabando audio |
| Pausado | Reanudar | Verde (pulso) | Grabacion pausada |
| Procesando | Spinner | Amarillo (gira) | Transcribiendo |
| Exito | Check | Verde | Listo, copiado al portapapeles |
| Error | Alerta | Gris | Fallo la transcripcion |

## Requisitos

- Python 3.10+
- Cuenta gratuita en [Groq](https://console.groq.com/) para la API key

### Dependencias del Sistema

```bash
# Debian/Ubuntu
sudo apt install python3-venv python3-full libportaudio2 xclip

# Para GUI en algunos sistemas
sudo apt install libxcb-cursor0
```

## Instalacion

```bash
# Clonar
git clone https://github.com/luckberonne/audio-transcribe.git
cd audio-transcribe

# Dar permisos
chmod +x start.sh run.py

# Ejecutar (instala dependencias automaticamente)
./start.sh
```

## Configuracion

### Groq API Key (Requerida)

1. Crear cuenta gratuita en [https://console.groq.com/](https://console.groq.com/)
2. Generar API Key
3. Configurar:

```bash
# Opcion 1: Variable de entorno
export GROQ_API_KEY="tu-api-key-aqui"

# Opcion 2: Agregar a ~/.bashrc (permanente)
echo 'export GROQ_API_KEY="tu-api-key-aqui"' >> ~/.bashrc
source ~/.bashrc
```

### Variables de Entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `GROQ_API_KEY` | (requerida) | API key de Groq |
| `BUTTON_POSITION` | `bottom-right` | Posicion: top-left, top-right, bottom-left, bottom-right, center |
| `BUTTON_SIZE` | `50` | Tamano del boton en pixeles |
| `TRANSCRIBE_HOTKEY` | `<ctrl>+<alt>+space` | Hotkey (solo modo CLI) |
| `WHISPER_MODEL` | `small` | Modelo local: tiny, base, small, medium, large |
| `WHISPER_DEVICE` | `cuda` | Dispositivo: cuda o cpu |

### Configuracion Persistente

Las preferencias de idioma y microfono se guardan en `app_settings.json` (creado automaticamente).

Cambia el idioma via el boton de Opciones (icono de engranaje) - los cambios se aplican inmediatamente y persisten entre reinicios.

## Uso

### Modo GUI (Panel Flotante)

```bash
./start.sh
# o
./run.py
```

1. Selecciona el microfono en el dialogo inicial
2. **Click** en el boton verde para empezar a grabar
3. Habla...
4. (Opcional) **Click** en el boton naranja para pausar/reanudar
5. **Click** en el boton rojo de detener para transcribir
6. El texto se copia automaticamente al portapapeles
7. **Arrastra** el panel para moverlo
8. **Click** en el icono de engranaje para opciones (microfono, idioma)
9. **Click** en el icono ? para ayuda
10. **Click** en el icono de salir para cerrar

### Modo CLI (Hotkey)

```bash
./start.sh --cli
```

1. Selecciona el microfono de la lista
2. Presiona `Ctrl+Alt+Space` para empezar a grabar
3. Habla...
4. Presiona `Ctrl+Alt+Space` para detener y transcribir
5. El texto aparece en la terminal y se copia al portapapeles

## Estructura del Proyecto

```
audio-transcribe/
├── start.sh                    # Script de inicio
├── run.py                      # Lanzador con auto-venv
├── floating_button_qt.py       # GUI (PySide6)
├── transcribe.py               # CLI (pynput)
├── transcription_controller.py # Logica compartida
├── audio_recorder.py           # Captura de audio
├── transcription_service.py    # Groq + Whisper
├── config.py                   # Configuracion
├── settings.py                 # Configuracion persistente y traducciones
├── app_settings.json           # Preferencias guardadas (auto-creado)
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
└── CLAUDE.md                   # Guia para Claude Code
```

## Modelos Whisper (Fallback)

| Modelo | VRAM | Velocidad | Precision |
|--------|------|-----------|-----------|
| tiny | ~1GB | Muy rapido | Baja |
| base | ~1GB | Rapido | Media |
| **small** | ~2GB | Medio | Buena (default) |
| medium | ~5GB | Lento | Muy buena |
| large | ~10GB | Muy lento | Excelente |

## Solucion de Problemas

### Error: PortAudio library not found

```bash
sudo apt install libportaudio2
```

### Error: No se encontraron microfonos

```bash
# Verificar PulseAudio/PipeWire
pactl list sources short

# Reiniciar PipeWire
systemctl --user restart pipewire pipewire-pulse
```

### Error: xcb plugin not found (GUI)

```bash
sudo apt install libxcb-cursor0
```

### Error: CUDA no disponible

```bash
export WHISPER_DEVICE="cpu"
```

### Error: pyperclip no funciona

```bash
sudo apt install xclip
```

### Microfono USB/Bluetooth no aparece

```bash
# Reiniciar audio
systemctl --user restart pipewire pipewire-pulse

# O desconectar/reconectar USB y verificar
arecord -l
```

## Licencia

MIT License

## Contribuciones

Los pull requests son bienvenidos. Para cambios mayores, por favor abre un issue primero.

---

# English

Voice-to-text transcription tool with **floating panel** (GUI) or **global hotkey** (CLI). Uses **Groq API** (free and fast) as primary service and **local Whisper** as fallback.

## Features

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

## Button States

| State | Button | Color | Description |
|-------|--------|-------|-------------|
| Ready | Record | Green | Waiting to record |
| Recording | Stop | Red (pulse) | Recording audio |
| Paused | Resume | Green (pulse) | Recording paused |
| Processing | Spinner | Yellow (spin) | Transcribing |
| Success | Check | Green | Done, copied to clipboard |
| Error | Alert | Gray | Transcription failed |

## Requirements

- Python 3.10+
- Free account at [Groq](https://console.groq.com/) for API key

### System Dependencies

```bash
# Debian/Ubuntu
sudo apt install python3-venv python3-full libportaudio2 xclip

# For GUI on some systems
sudo apt install libxcb-cursor0
```

## Installation

```bash
# Clone
git clone https://github.com/luckberonne/audio-transcribe.git
cd audio-transcribe

# Give permissions
chmod +x start.sh run.py

# Run (installs dependencies automatically)
./start.sh
```

## Configuration

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

## Usage

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

## Project Structure

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

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first.
