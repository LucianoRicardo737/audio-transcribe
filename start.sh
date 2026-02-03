#!/bin/bash
# Script de inicio para Audio Transcription
# Uso:
#   ./start.sh        # GUI (botón flotante) por defecto
#   ./start.sh --cli  # Modo CLI con hotkey

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Determinar modo
MODE="gui"
if [ "$1" == "--cli" ] || [ "$1" == "-c" ]; then
    MODE="cli"
fi

echo -e "${CYAN}========================================${NC}"
if [ "$MODE" == "cli" ]; then
    echo -e "${CYAN}   Audio Transcription CLI${NC}"
else
    echo -e "${CYAN}   Audio Transcription GUI${NC}"
fi
echo -e "${CYAN}========================================${NC}"
echo ""

# 1. Crear venv si no existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# 2. Activar venv
source venv/bin/activate

# 3. Instalar dependencias si es necesario
if [ ! -f ".deps_installed" ]; then
    echo -e "${YELLOW}Instalando dependencias (primera vez)...${NC}"
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt
    touch .deps_installed
    echo -e "${GREEN}Dependencias instaladas${NC}"
fi

# 4. Verificar y reiniciar audio si es necesario
echo -e "${CYAN}Verificando dispositivos de audio...${NC}"

# Reiniciar PipeWire para asegurar que detecte dispositivos USB
if command -v systemctl &> /dev/null; then
    systemctl --user restart pipewire pipewire-pulse 2>/dev/null || true
    sleep 1
fi

# Mostrar dispositivos detectados
DEVICES=$(./venv/bin/python -c "
import sounddevice as sd
devices = sd.query_devices()
inputs = [d for d in devices if d['max_input_channels'] > 0]
for d in inputs:
    idx = devices.index(d) if isinstance(devices, list) else list(devices).index(d)
    default = ' (default)' if d.get('name') == sd.query_devices(kind='input').get('name') else ''
    print(f\"  - [{idx}] {d['name'][:50]}{default}\")
" 2>/dev/null)

if [ -z "$DEVICES" ]; then
    echo -e "${YELLOW}No se detectaron microfonos. Intentando reiniciar audio...${NC}"
    systemctl --user restart pipewire pipewire-pulse 2>/dev/null || pulseaudio -k 2>/dev/null && pulseaudio --start 2>/dev/null
    sleep 2
fi

echo -e "${GREEN}Dispositivos disponibles:${NC}"
./venv/bin/python -c "
import sounddevice as sd
devices = sd.query_devices()
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f\"  [{i}] {d['name'][:50]}\")
" 2>/dev/null || echo -e "${YELLOW}  No se pudieron listar dispositivos${NC}"

echo ""

# 5. Ejecutar
if [ "$MODE" == "cli" ]; then
    ./venv/bin/python transcribe.py
else
    ./venv/bin/python floating_button_qt.py
fi
