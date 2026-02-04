#!/bin/bash
# Audio Transcription - Unix Launcher
# Delegates to launcher.py for cross-platform setup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find Python 3
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3 no encontrado."
    echo "  Linux: sudo apt install python3"
    echo "  macOS: brew install python@3.12"
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/launcher.py" "$@"
