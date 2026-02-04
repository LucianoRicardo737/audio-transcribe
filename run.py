#!/usr/bin/env python3
"""
Launcher que activa venv automáticamente.

Uso:
    ./run.py         # GUI (botón flotante con Qt)
    ./run.py --cli   # Modo CLI con hotkey
"""
import os
import sys
import platform

def get_venv_python():
    """Get path to venv python, cross-platform."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        return os.path.join(script_dir, "venv", "Scripts", "python.exe")
    else:
        return os.path.join(script_dir, "venv", "bin", "python")

def main():
    venv_python = get_venv_python()

    # Check if running from venv already
    if os.path.realpath(sys.executable) == os.path.realpath(venv_python):
        # Already in venv, run the actual script
        if "--cli" in sys.argv or "-c" in sys.argv:
            from transcribe import main as cli_main
            cli_main()
        else:
            from floating_button_qt import main as gui_main
            sys.exit(gui_main())
        return

    # Not in venv, re-exec with venv python
    if os.path.exists(venv_python):
        if platform.system() == "Windows":
            import subprocess
            sys.exit(subprocess.call([venv_python, __file__] + sys.argv[1:]))
        else:
            os.execv(venv_python, [venv_python, __file__] + sys.argv[1:])
    else:
        print("Error: venv no existe.")
        print("Ejecuta './start.sh' primero para crear el entorno virtual.")
        sys.exit(1)


if __name__ == "__main__":
    main()
