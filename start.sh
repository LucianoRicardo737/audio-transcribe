#!/bin/bash
# Script de inicio para Audio Transcription CLI
# Uso: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Audio Transcription CLI${NC}"
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

echo ""

# 4. Ejecutar
./venv/bin/python transcribe.py
