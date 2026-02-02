# Audio Transcribe CLI

Herramienta de transcripcion de voz a texto con hotkey global. Usa **Groq API** (gratis y rapido) como servicio principal y **Whisper local** como fallback.

## Caracteristicas

- **Hotkey Global**: `Ctrl+Alt+Space` funciona en cualquier ventana (no requiere focus)
- **Groq API**: Transcripcion rapida y gratuita en la nube
- **Whisper Local**: Fallback automatico si Groq falla
- **Seleccion de Microfono**: Elige tu dispositivo de entrada al iniciar
- **Clipboard Automatico**: El texto transcrito se copia automaticamente
- **Multi-idioma**: Configurable (default: Espanol)

## Requisitos

- Python 3.10+
- Linux con PulseAudio o PipeWire
- Cuenta gratuita en [Groq](https://console.groq.com/) para API key

### Dependencias del Sistema

```bash
# Debian/Ubuntu
sudo apt install python3-venv python3-full libportaudio2

# Para clipboard
sudo apt install xclip
```

## Instalacion

### Opcion 1: Script automatico

```bash
git clone http://git.corpy.ai/Corpy/audio-transcribe.git
cd audio-transcribe
chmod +x start.sh
./start.sh
```

### Opcion 2: Manual

```bash
git clone http://git.corpy.ai/Corpy/audio-transcribe.git
cd audio-transcribe

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python transcribe.py
```

## Configuracion

### API Key de Groq (Requerido)

1. Crear cuenta gratuita en [https://console.groq.com/](https://console.groq.com/)
2. Generar API Key
3. Configurar variable de entorno:

```bash
export GROQ_API_KEY="tu-api-key-aqui"
```

O agregar a `~/.bashrc`:

```bash
echo 'export GROQ_API_KEY="tu-api-key-aqui"' >> ~/.bashrc
source ~/.bashrc
```

### Variables de Entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `GROQ_API_KEY` | (requerido) | API key de Groq |
| `TRANSCRIBE_HOTKEY` | `<ctrl>+<alt>+space` | Combinacion de teclas |
| `TRANSCRIBE_LANGUAGE` | `es` | Idioma (es, en, pt, etc.) |
| `WHISPER_MODEL` | `small` | Modelo local: tiny, base, small, medium, large |
| `WHISPER_DEVICE` | `cuda` | Dispositivo: cuda o cpu |

### Ejemplos de Hotkeys

```bash
# Ctrl+Alt+Space (default)
export TRANSCRIBE_HOTKEY="<ctrl>+<alt>+space"

# Ctrl+Shift+R
export TRANSCRIBE_HOTKEY="<ctrl>+<shift>+r"

# F9
export TRANSCRIBE_HOTKEY="<f9>"
```

## Uso

1. Ejecutar el script:
   ```bash
   ./start.sh
   ```

2. Seleccionar microfono de la lista

3. Presionar `Ctrl+Alt+Space` para **iniciar** grabacion

4. Hablar...

5. Presionar `Ctrl+Alt+Space` para **detener** y transcribir

6. El texto aparece en pantalla y se copia al portapapeles

7. Repetir desde paso 3

## Estructura del Proyecto

```
audio-transcribe/
├── start.sh                 # Script de inicio automatico
├── transcribe.py            # Aplicacion principal
├── config.py                # Configuracion
├── audio_recorder.py        # Captura de audio
├── transcription_service.py # Groq + Whisper
├── requirements.txt         # Dependencias Python
└── README.md                # Este archivo
```

## Modelos Whisper (Fallback)

| Modelo | VRAM | Velocidad | Precision |
|--------|------|-----------|-----------|
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
# Verificar que PulseAudio esta corriendo
pulseaudio --start

# O instalar PulseAudio
sudo apt install pulseaudio
```

### Error: CUDA not available

Si no tienes GPU, usa CPU:

```bash
export WHISPER_DEVICE="cpu"
```

### Error: pyperclip no funciona

```bash
sudo apt install xclip
# o
sudo apt install xsel
```

### Microfono USB/Bluetooth no aparece

```bash
# Instalar y reiniciar PulseAudio
sudo apt install pulseaudio pulseaudio-module-bluetooth
pulseaudio -k
pulseaudio --start
```

## Licencia

MIT License

## Contribuciones

Pull requests son bienvenidos. Para cambios importantes, abre un issue primero.
