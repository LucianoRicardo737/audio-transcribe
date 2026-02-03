# Audio Transcribe

Herramienta de transcripcion de voz a texto con **boton flotante** (GUI) o **hotkey global** (CLI). Usa **Groq API** (gratis y rapido) como servicio principal y **Whisper local** como fallback.

## Modos de Uso

### GUI (Por defecto) - Boton Flotante
- Boton circular transparente siempre visible
- Click para grabar/detener
- Arrastrable a cualquier posicion
- Click derecho para menu de opciones

### CLI - Hotkey Global
- `Ctrl+Alt+Space` funciona en cualquier ventana
- Interfaz de terminal con Rich

## Caracteristicas

- **Boton Flotante**: Circular, transparente, always-on-top (PySide6)
- **Iconos Modernos**: Material Design via QtAwesome
- **Groq API**: Transcripcion rapida y gratuita en la nube
- **Whisper Local**: Fallback automatico si Groq falla
- **Seleccion de Microfono**: Elige tu dispositivo de entrada
- **Clipboard Automatico**: El texto transcrito se copia automaticamente
- **Multi-idioma**: Configurable (default: Espanol)
- **Cross-platform**: Linux, Windows, macOS

## Requisitos

- Python 3.10+
- Cuenta gratuita en [Groq](https://console.groq.com/) para API key

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
git clone https://gitea.softrock.com.ar/corpy/audio-transcribe.git
cd audio-transcribe

# Dar permisos
chmod +x start.sh run.py

# Ejecutar (instala dependencias automaticamente)
./start.sh
```

## Configuracion

### API Key de Groq (Requerido)

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
| `GROQ_API_KEY` | (requerido) | API key de Groq |
| `TRANSCRIBE_LANGUAGE` | `es` | Idioma (es, en, pt, etc.) |
| `BUTTON_POSITION` | `bottom-right` | Posicion: top-left, top-right, bottom-left, bottom-right, center |
| `BUTTON_SIZE` | `50` | Tamano del boton en pixeles |
| `BUTTON_OPACITY` | `0.9` | Transparencia (0.0 - 1.0) |
| `TRANSCRIBE_HOTKEY` | `<ctrl>+<alt>+space` | Hotkey (solo modo CLI) |
| `WHISPER_MODEL` | `small` | Modelo local: tiny, base, small, medium, large |
| `WHISPER_DEVICE` | `cuda` | Dispositivo: cuda o cpu |

## Uso

### Modo GUI (Boton Flotante)

```bash
./start.sh
# o
./run.py
```

1. Seleccionar microfono en el dialogo inicial
2. **Click** en el boton verde para iniciar grabacion
3. Hablar...
4. **Click** en el boton rojo para detener y transcribir
5. El texto se copia automaticamente al portapapeles
6. **Click derecho** para cambiar microfono o salir
7. **Arrastrar** el boton para moverlo

### Modo CLI (Hotkey)

```bash
./start.sh --cli
```

1. Seleccionar microfono de la lista
2. Presionar `Ctrl+Alt+Space` para iniciar grabacion
3. Hablar...
4. Presionar `Ctrl+Alt+Space` para detener y transcribir
5. El texto aparece en terminal y se copia al portapapeles

## Estructura del Proyecto

```
audio-transcribe/
├── start.sh                  # Script de inicio
├── run.py                    # Launcher con auto-venv
├── floating_button_qt.py     # GUI (PySide6)
├── transcribe.py             # CLI (pynput)
├── transcription_controller.py # Logica compartida
├── audio_recorder.py         # Captura de audio
├── transcription_service.py  # Groq + Whisper
├── config.py                 # Configuracion
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
└── CLAUDE.md                 # Guia para Claude Code
```

## Estados del Boton

| Estado | Color | Icono | Descripcion |
|--------|-------|-------|-------------|
| Listo | Verde | Microfono | Esperando para grabar |
| Grabando | Rojo (pulsa) | Stop | Grabando audio |
| Procesando | Amarillo (gira) | Loading | Transcribiendo |
| Exito | Verde | Check | Transcripcion completada |
| Error | Gris | X | Error en transcripcion |

## Modelos Whisper (Fallback)

| Modelo | VRAM | Velocidad | Precision |
|--------|------|-----------|-----------a|
| tiny | ~1GB | Muy rapido | Baja |
| base | ~1GB | Rapido | Media |
| **small** | ~2GB | Medio | Buena (default) |
| medium | ~5GB | Lento | Muy buena |
| large | ~10GB | Muy lento | Excelente |

## Troubleshooting

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

### Error: CUDA not available

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

Pull requests son bienvenidos. Para cambios importantes, abre un issue primero.
