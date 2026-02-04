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
- **Configuracion de API Key desde GUI**: Configura tu clave Groq directamente desde la app (sin variables de entorno)
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

#### Linux (Debian/Ubuntu)
```bash
sudo apt install python3-venv python3-full libportaudio2 xclip

# Para GUI en algunos sistemas
sudo apt install libxcb-cursor0
```

#### macOS
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar PortAudio
brew install portaudio
```

#### Windows
- Descargar Python desde [python.org](https://www.python.org/downloads/)
- **Importante**: Marcar la opción "Add Python to PATH" durante la instalación
- Las demás dependencias se instalan automáticamente

## Instalacion

```bash
# Clonar
git clone https://github.com/luckberonne/audio-transcribe.git
cd audio-transcribe

# Dar permisos (solo en Linux/macOS)
chmod +x start.sh launcher.py

# Ejecutar (instala dependencias automaticamente)
./start.sh                    # Linux/macOS (GUI)
./start.sh --cli             # Linux/macOS (CLI con hotkey)
start.bat                    # Windows (GUI)
python launcher.py           # Alternativa cross-platform
python launcher.py --cli     # Alternativa cross-platform (CLI)
```

## Configuracion

### Groq API Key (Requerida)

1. Crear cuenta gratuita en [https://console.groq.com/](https://console.groq.com/)
2. Generar API Key
3. Configurar con uno de estos metodos:

#### Desde la app (recomendado)

En la primera ejecucion, la app pide automaticamente la clave API. Tambien se puede ver y cambiar en cualquier momento desde **Opciones** (icono de engranaje).

La clave se guarda en `app_settings.json` y persiste entre reinicios. Funciona en todos los sistemas operativos.

#### Variable de entorno (alternativa)

<details>
<summary>Linux/macOS</summary>

```bash
# Opcion 1: Variable de entorno temporal
export GROQ_API_KEY="tu-api-key-aqui"
python launcher.py

# Opcion 2: Permanente en ~/.bashrc o ~/.zshrc
echo 'export GROQ_API_KEY="tu-api-key-aqui"' >> ~/.bashrc
source ~/.bashrc
```

</details>

<details>
<summary>Windows (PowerShell)</summary>

```powershell
# Opcion 1: Temporal
$env:GROQ_API_KEY="tu-api-key-aqui"
python launcher.py

# Opcion 2: Permanente (requiere reiniciar PowerShell)
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "tu-api-key-aqui", "User")
```

</details>

<details>
<summary>Windows (CMD)</summary>

```batch
REM Temporal
set GROQ_API_KEY=tu-api-key-aqui
start.bat

REM Permanente: usar interfaz de Windows
REM Settings > System > Advanced System Settings > Environment Variables
```

</details>

> **Nota**: Si la clave esta configurada tanto en la app como en variable de entorno, la de la app tiene prioridad.

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

Las preferencias de idioma, microfono y clave API Groq se guardan en `app_settings.json` (creado automaticamente).

Desde el boton de Opciones (icono de engranaje) podes cambiar idioma, microfono y clave API. Los cambios se aplican inmediatamente y persisten entre reinicios.

## Uso

### Modo GUI (Panel Flotante)

#### Linux/macOS
```bash
./start.sh
```

#### Windows
```batch
start.bat
```

#### Cross-platform
```bash
python launcher.py
```

**Pasos**:
1. Selecciona el microfono en el dialogo inicial
2. **Click** en el boton verde para empezar a grabar
3. Habla...
4. (Opcional) **Click** en el boton naranja para pausar/reanudar
5. **Click** en el boton rojo de detener para transcribir
6. El texto se copia automaticamente al portapapeles
7. **Arrastra** el panel para moverlo
8. **Click** en el icono de engranaje para opciones (clave API, microfono, idioma)
9. **Click** en el icono ? para ayuda
10. **Click** en el icono de salir para cerrar

### Modo CLI (Hotkey Global)

#### Linux/macOS
```bash
./start.sh --cli
```

#### Windows
```batch
start.bat --cli
```

#### Cross-platform
```bash
python launcher.py --cli
```

**Pasos**:
1. Selecciona el microfono de la lista
2. Presiona `Ctrl+Alt+Space` para empezar a grabar
3. Habla...
4. Presiona `Ctrl+Alt+Space` para detener y transcribir
5. El texto aparece en la terminal y se copia al portapapeles

### Argumentos disponibles

```bash
# Mostrar ayuda
python launcher.py --help

# GUI (default)
python launcher.py

# CLI con hotkey
python launcher.py --cli

# Saltar verificacion de audio
python launcher.py --skip-audio-check

# Reintentar audio (Linux)
python launcher.py --fix-audio
```

## Estructura del Proyecto

```
audio-transcribe/
├── launcher.py                 # Launcher cross-platform (punto de entrada principal)
├── start.sh                    # Wrapper Unix/Linux/macOS (delega a launcher.py)
├── start.bat                   # Wrapper Windows (delega a launcher.py)
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

### PortAudio no encontrado

**Linux (Debian/Ubuntu)**:
```bash
sudo apt install libportaudio2
```

**Linux (Fedora)**:
```bash
sudo dnf install portaudio
```

**macOS**:
```bash
brew install portaudio
```

**Windows**: Se incluye automáticamente con sounddevice

### No se detectan microfonos

**Linux**:
```bash
# Verificar PulseAudio/PipeWire
pactl list sources short

# Listar dispositivos ALSA
arecord -l

# Reiniciar audio (automático con --fix-audio)
python launcher.py --fix-audio
```

**macOS**:
- Verificar: System Settings > Sound > Input
- Conectar micrófono USB y esperar 2-3 segundos
- Permitir acceso cuando macOS lo solicite

**Windows**:
- Verificar: Settings > System > Sound > Input
- Verificar privacidad: Settings > Privacy & Security > Microphone
- Desconectar y reconectar dispositivo USB

### Error: xcb plugin not found (GUI en Linux)

```bash
sudo apt install libxcb-cursor0
```

### Error: CUDA no disponible

```bash
export WHISPER_DEVICE="cpu"
python launcher.py
```

### Portapapeles no funciona

**Linux**:
```bash
sudo apt install xclip
```

**macOS**: Debería funcionar automáticamente (pbcopy)

**Windows**: Debería funcionar automáticamente (Win32 API)

### Hotkeys globales no funcionan (CLI mode)

**Linux con Wayland**:
```bash
# Wayland no soporta hotkeys globales con pynput
# Se recomienda usar modo GUI: python launcher.py
# O cambiar a X11
```

**macOS**:
- Ir a: System Settings > Privacy & Security > Accessibility
- Agregar Terminal (o iTerm) a la lista permitida

**Windows**: Debería funcionar automáticamente

### Python no encontrado

**Linux**:
```bash
sudo apt install python3
```

**macOS**:
```bash
brew install python@3.12
# o descargar desde python.org
```

**Windows**:
- Descargar desde [python.org](https://www.python.org/downloads/)
- **Importante**: Marcar "Add Python to PATH" durante instalación

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
- **GUI API Key Setup**: Configure your Groq key directly from the app (no environment variables needed)
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

#### Linux (Debian/Ubuntu)
```bash
sudo apt install python3-venv python3-full libportaudio2 xclip

# For GUI on some systems
sudo apt install libxcb-cursor0
```

#### macOS
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PortAudio
brew install portaudio
```

#### Windows
- Download Python from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation
- Other dependencies are installed automatically

## Installation

```bash
# Clone
git clone https://github.com/luckberonne/audio-transcribe.git
cd audio-transcribe

# Give permissions (Linux/macOS only)
chmod +x start.sh launcher.py

# Run (installs dependencies automatically)
./start.sh                    # Linux/macOS (GUI)
./start.sh --cli             # Linux/macOS (CLI with hotkey)
start.bat                    # Windows (GUI)
python launcher.py           # Cross-platform alternative
python launcher.py --cli     # Cross-platform alternative (CLI)
```

## Configuration

### Groq API Key (Required)

1. Create free account at [https://console.groq.com/](https://console.groq.com/)
2. Generate API Key
3. Configure using one of these methods:

#### From the app (recommended)

On first run, the app automatically prompts for the API key. You can also view and change it anytime from **Settings** (gear icon).

The key is saved to `app_settings.json` and persists across restarts. Works on all operating systems.

#### Environment variable (alternative)

<details>
<summary>Linux/macOS</summary>

```bash
# Option 1: Temporary environment variable
export GROQ_API_KEY="your-api-key-here"
python launcher.py

# Option 2: Permanent in ~/.bashrc or ~/.zshrc
echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

</details>

<details>
<summary>Windows (PowerShell)</summary>

```powershell
# Option 1: Temporary
$env:GROQ_API_KEY="your-api-key-here"
python launcher.py

# Option 2: Permanent (requires PowerShell restart)
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your-api-key-here", "User")
```

</details>

<details>
<summary>Windows (CMD)</summary>

```batch
REM Temporary
set GROQ_API_KEY=your-api-key-here
start.bat

REM Permanent: use Windows GUI
REM Settings > System > Advanced System Settings > Environment Variables
```

</details>

> **Note**: If the key is configured both in the app and as an environment variable, the app setting takes priority.

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

Language, microphone and Groq API key preferences are saved in `app_settings.json` (created automatically).

From the Settings button (gear icon) you can change language, microphone and API key. Changes apply immediately and persist across restarts.

## Usage

### GUI Mode (Floating Panel)

#### Linux/macOS
```bash
./start.sh
```

#### Windows
```batch
start.bat
```

#### Cross-platform
```bash
python launcher.py
```

**Steps**:
1. Select microphone in initial dialog
2. **Click** green button to start recording
3. Speak...
4. (Optional) **Click** orange button to pause/resume
5. **Click** red stop button to transcribe
6. Text is copied automatically to clipboard
7. **Drag** panel to move it
8. **Click** gear icon for settings (API key, microphone, language)
9. **Click** ? icon for help
10. **Click** exit icon to quit

### CLI Mode (Global Hotkey)

#### Linux/macOS
```bash
./start.sh --cli
```

#### Windows
```batch
start.bat --cli
```

#### Cross-platform
```bash
python launcher.py --cli
```

**Steps**:
1. Select microphone from list
2. Press `Ctrl+Alt+Space` to start recording
3. Speak...
4. Press `Ctrl+Alt+Space` to stop and transcribe
5. Text appears in terminal and is copied to clipboard

### Available arguments

```bash
# Show help
python launcher.py --help

# GUI (default)
python launcher.py

# CLI with global hotkey
python launcher.py --cli

# Skip audio device verification
python launcher.py --skip-audio-check

# Attempt audio system restart (Linux)
python launcher.py --fix-audio
```

## Project Structure

```
audio-transcribe/
├── launcher.py                 # Cross-platform launcher (main entry point)
├── start.sh                    # Unix/Linux/macOS wrapper (delegates to launcher.py)
├── start.bat                   # Windows wrapper (delegates to launcher.py)
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

### PortAudio not found

**Linux (Debian/Ubuntu)**:
```bash
sudo apt install libportaudio2
```

**Linux (Fedora)**:
```bash
sudo dnf install portaudio
```

**macOS**:
```bash
brew install portaudio
```

**Windows**: Automatically included with sounddevice

### No microphones detected

**Linux**:
```bash
# Check PulseAudio/PipeWire
pactl list sources short

# List ALSA devices
arecord -l

# Restart audio (automatic with --fix-audio)
python launcher.py --fix-audio
```

**macOS**:
- Check: System Settings > Sound > Input
- Connect USB microphone and wait 2-3 seconds
- Allow access when prompted

**Windows**:
- Check: Settings > System > Sound > Input
- Check privacy: Settings > Privacy & Security > Microphone
- Disconnect and reconnect USB device

### Error: xcb plugin not found (GUI on Linux)

```bash
sudo apt install libxcb-cursor0
```

### Error: CUDA not available

```bash
export WHISPER_DEVICE="cpu"
python launcher.py
```

### Clipboard not working

**Linux**:
```bash
sudo apt install xclip
```

**macOS**: Should work automatically (pbcopy)

**Windows**: Should work automatically (Win32 API)

### Global hotkeys not working (CLI mode)

**Linux with Wayland**:
```bash
# Wayland doesn't support global hotkeys with pynput
# Recommended: use GUI mode: python launcher.py
# Or switch to X11
```

**macOS**:
- Go to: System Settings > Privacy & Security > Accessibility
- Add Terminal (or iTerm) to the allowed list

**Windows**: Should work automatically

### Python not found

**Linux**:
```bash
sudo apt install python3
```

**macOS**:
```bash
brew install python@3.12
# or download from python.org
```

**Windows**:
- Download from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first.
