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

# 4. Verificar tkinter para GUI
if [ "$MODE" == "gui" ]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${YELLOW}tkinter no instalado. Instalando...${NC}"
        echo -e "${YELLOW}Puede requerir: sudo apt install python3-tk${NC}"
    fi
fi

echo ""

# 5. Ejecutar
if [ "$MODE" == "cli" ]; then
    ./venv/bin/python transcribe.py
else
    ./venv/bin/python floating_button_qt.py
fi
