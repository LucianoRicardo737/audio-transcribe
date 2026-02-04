#!/usr/bin/env python3
"""
Cross-platform launcher for Audio Transcription.
Handles venv creation, dependency installation, audio checks, and app execution.

Works on Linux, macOS, and Windows using only Python standard library.

Usage:
    python launcher.py          # GUI mode (default)
    python launcher.py --cli    # CLI mode with hotkey
    python launcher.py --fix-audio  # Attempt audio system restart (Linux)
"""
import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# --- Color support ---

def _supports_color():
    """Check if terminal supports ANSI color codes."""
    if platform.system() == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable ANSI escape sequences on Windows 10+
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

if _supports_color():
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    DIM = '\033[2m'
    NC = '\033[0m'
else:
    GREEN = YELLOW = CYAN = RED = DIM = NC = ''

SCRIPT_DIR = Path(__file__).parent.resolve()
PLAT = platform.system().lower()  # "linux", "darwin", "windows"

# --- Path helpers ---

def get_venv_python():
    if PLAT == "windows":
        return SCRIPT_DIR / "venv" / "Scripts" / "python.exe"
    return SCRIPT_DIR / "venv" / "bin" / "python"

def get_venv_pip():
    if PLAT == "windows":
        return SCRIPT_DIR / "venv" / "Scripts" / "pip.exe"
    return SCRIPT_DIR / "venv" / "bin" / "pip"

# --- Parse arguments ---

def parse_args():
    parser = argparse.ArgumentParser(
        description="Audio Transcription - Cross-platform launcher"
    )
    parser.add_argument(
        '--cli', '-c', action='store_true',
        help='CLI mode with global hotkey (default: GUI)'
    )
    parser.add_argument(
        '--skip-audio-check', action='store_true',
        help='Skip audio device verification'
    )
    parser.add_argument(
        '--fix-audio', action='store_true',
        help='Attempt to restart audio subsystem if no devices found (Linux only)'
    )
    return parser.parse_args()

# --- Banner ---

def print_banner(mode):
    plat_name = {"linux": "Linux", "darwin": "macOS", "windows": "Windows"}.get(PLAT, PLAT)
    label = "CLI" if mode == "cli" else "GUI"
    print(f"{CYAN}========================================{NC}")
    print(f"{CYAN}   Audio Transcription {label}{NC}")
    print(f"{CYAN}   {DIM}{plat_name} - Python {sys.version.split()[0]}{NC}")
    print(f"{CYAN}========================================{NC}")
    print()

# --- Python version check ---

def check_python_version():
    if sys.version_info < (3, 10):
        print(f"{RED}Error: Se requiere Python 3.10 o superior.{NC}")
        print(f"{DIM}Version actual: {sys.version}{NC}")
        if PLAT == "linux":
            print(f"  Instalar: sudo apt install python3 (Debian/Ubuntu)")
        elif PLAT == "darwin":
            print(f"  Instalar: brew install python@3.12")
        elif PLAT == "windows":
            print(f"  Descargar: https://www.python.org/downloads/")
        sys.exit(1)

# --- System dependency checks ---

def check_system_dependencies():
    """Check platform-specific system dependencies. Non-blocking (warnings only)."""
    print(f"{CYAN}Verificando dependencias del sistema...{NC}")

    if PLAT == "linux":
        _check_linux_deps()
    elif PLAT == "darwin":
        _check_macos_deps()
    elif PLAT == "windows":
        _check_windows_deps()

    print()

def _check_linux_deps():
    # PortAudio
    try:
        result = subprocess.run(
            ["ldconfig", "-p"], capture_output=True, text=True, timeout=5
        )
        if "portaudio" in result.stdout.lower():
            print(f"  {GREEN}[OK]{NC} PortAudio")
        else:
            print(f"  {YELLOW}[!!]{NC} PortAudio no encontrado")
            print(f"       -> sudo apt install libportaudio2 {DIM}(Debian/Ubuntu){NC}")
            print(f"       -> sudo dnf install portaudio {DIM}(Fedora){NC}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"  {DIM}[--] PortAudio: no se pudo verificar{NC}")

    # Clipboard (xclip or xsel)
    if shutil.which("xclip") or shutil.which("xsel"):
        print(f"  {GREEN}[OK]{NC} Clipboard (xclip/xsel)")
    else:
        print(f"  {YELLOW}[!!]{NC} xclip/xsel no encontrado")
        print(f"       -> sudo apt install xclip")
        print(f"       -> El portapapeles no funcionara sin esto")

    # python3-venv
    try:
        import venv  # noqa: F401
        print(f"  {GREEN}[OK]{NC} python3-venv")
    except ImportError:
        print(f"  {RED}[!!]{NC} python3-venv no disponible")
        print(f"       -> sudo apt install python3-venv python3-full")

    # Wayland warning for CLI mode
    session_type = os.environ.get("XDG_SESSION_TYPE", "")
    if session_type == "wayland":
        print(f"  {YELLOW}[!!]{NC} Sesion Wayland detectada")
        print(f"       -> Las hotkeys globales (modo CLI) pueden no funcionar")
        print(f"       -> Se recomienda usar modo GUI")

def _check_macos_deps():
    # PortAudio via Homebrew
    if shutil.which("brew"):
        try:
            result = subprocess.run(
                ["brew", "list", "portaudio"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"  {GREEN}[OK]{NC} PortAudio (Homebrew)")
            else:
                print(f"  {YELLOW}[!!]{NC} PortAudio no instalado")
                print(f"       -> brew install portaudio")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"  {DIM}[--] PortAudio: no se pudo verificar{NC}")
    else:
        # Check if portaudio lib exists in common locations
        portaudio_paths = [
            Path("/opt/homebrew/lib/libportaudio.dylib"),
            Path("/usr/local/lib/libportaudio.dylib"),
        ]
        if any(p.exists() for p in portaudio_paths):
            print(f"  {GREEN}[OK]{NC} PortAudio")
        else:
            print(f"  {YELLOW}[!!]{NC} PortAudio no encontrado")
            print(f"       -> Instalar Homebrew: https://brew.sh/")
            print(f"       -> Luego: brew install portaudio")

    # Clipboard - pbcopy is always available on macOS
    print(f"  {GREEN}[OK]{NC} Clipboard (pbcopy nativo)")

    # Accessibility note for CLI mode
    print(f"  {DIM}[i]{NC}  Modo CLI requiere permiso de Accesibilidad")
    print(f"       -> System Settings > Privacy & Security > Accessibility")

def _check_windows_deps():
    # PortAudio is bundled with sounddevice on Windows
    print(f"  {GREEN}[OK]{NC} PortAudio (incluido con sounddevice)")

    # Clipboard - native on Windows
    print(f"  {GREEN}[OK]{NC} Clipboard (nativo)")

    # Microphone privacy note
    print(f"  {DIM}[i]{NC}  Asegurar acceso al microfono:")
    print(f"       -> Settings > Privacy & Security > Microphone")

# --- Virtual environment ---

def ensure_venv():
    venv_dir = SCRIPT_DIR / "venv"
    venv_py = get_venv_python()

    if venv_dir.exists() and venv_py.exists():
        return

    if venv_dir.exists() and not venv_py.exists():
        print(f"{YELLOW}Venv corrupto, recreando...{NC}")
        shutil.rmtree(venv_dir)

    print(f"{YELLOW}Creando entorno virtual...{NC}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "venv", str(venv_dir)],
            stdout=subprocess.DEVNULL
        )
        print(f"{GREEN}Entorno virtual creado{NC}")
    except subprocess.CalledProcessError:
        print(f"{RED}Error creando venv.{NC}")
        if PLAT == "linux":
            print(f"  Instalar: sudo apt install python3-venv python3-full")
        elif PLAT == "darwin":
            print(f"  Verificar instalacion de Python: python3 --version")
        elif PLAT == "windows":
            print(f"  Reinstalar Python desde https://www.python.org/downloads/")
            print(f"  Marcar 'Add Python to PATH' durante la instalacion")
        sys.exit(1)

# --- Dependencies ---

def ensure_dependencies():
    marker = SCRIPT_DIR / ".deps_installed"
    if marker.exists():
        return

    print(f"{YELLOW}Instalando dependencias (primera vez)...{NC}")
    pip = get_venv_pip()
    req = SCRIPT_DIR / "requirements.txt"

    try:
        subprocess.check_call(
            [str(pip), "install", "--upgrade", "pip", "-q"],
            stdout=subprocess.DEVNULL
        )
        subprocess.check_call([str(pip), "install", "-r", str(req)])
        marker.touch()
        print(f"{GREEN}Dependencias instaladas{NC}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error instalando dependencias: {e}{NC}")
        print(f"  Intentar manualmente:")
        print(f"  {str(pip)} install -r {str(req)}")
        sys.exit(1)

# --- Audio device verification ---

def verify_audio_devices(fix_audio=False):
    """Check for available input devices using venv python + sounddevice."""
    print(f"{CYAN}Verificando dispositivos de audio...{NC}")

    venv_py = get_venv_python()
    check_script = (
        "import sounddevice as sd\n"
        "devices = sd.query_devices()\n"
        "inputs = [d for d in devices if d['max_input_channels'] > 0]\n"
        "for d in inputs:\n"
        "    idx = list(devices).index(d)\n"
        "    print(f'  [{idx}] {d[\"name\"][:50]}')\n"
    )

    devices_output = _run_audio_check(venv_py, check_script)

    if devices_output:
        print(f"{GREEN}Dispositivos disponibles:{NC}")
        print(devices_output)
        return True

    # No devices found
    print(f"{YELLOW}No se detectaron microfonos.{NC}")

    if fix_audio and PLAT == "linux":
        _try_linux_audio_restart()
        devices_output = _run_audio_check(venv_py, check_script)
        if devices_output:
            print(f"{GREEN}Dispositivos encontrados tras reinicio:{NC}")
            print(devices_output)
            return True

    _print_audio_troubleshooting()
    return False

def _run_audio_check(venv_py, script):
    """Run audio device check script and return stdout or empty string."""
    try:
        result = subprocess.run(
            [str(venv_py), "-c", script],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""

def _try_linux_audio_restart():
    """Attempt to restart the Linux audio subsystem (PipeWire or PulseAudio)."""
    import time

    if shutil.which("pipewire"):
        print(f"{YELLOW}Reiniciando PipeWire...{NC}")
        subprocess.run(
            ["systemctl", "--user", "restart", "pipewire", "pipewire-pulse"],
            capture_output=True
        )
    elif shutil.which("pulseaudio"):
        print(f"{YELLOW}Reiniciando PulseAudio...{NC}")
        subprocess.run(["pulseaudio", "-k"], capture_output=True)
        subprocess.run(["pulseaudio", "--start"], capture_output=True)
    else:
        print(f"{YELLOW}No se detecto PipeWire ni PulseAudio (ALSA directo).{NC}")
        print(f"  Verificar manualmente: arecord -l")
        return

    time.sleep(3)

def _print_audio_troubleshooting():
    """Print platform-specific audio troubleshooting guide."""
    if PLAT == "linux":
        print(f"""
{YELLOW}Troubleshooting de audio (Linux):{NC}
  - Verificar microfonos: arecord -l
  - Verificar audio: pactl list sources short
  - Reiniciar audio: ejecutar con --fix-audio
  - USB/Bluetooth: desconectar y reconectar el dispositivo
  - PortAudio faltante: sudo apt install libportaudio2
""")
    elif PLAT == "darwin":
        print(f"""
{YELLOW}Troubleshooting de audio (macOS):{NC}
  - Verificar: System Settings > Sound > Input
  - PortAudio: brew install portaudio
  - Permisos: permitir acceso al microfono cuando macOS lo solicite
  - USB: desconectar y reconectar
""")
    elif PLAT == "windows":
        print(f"""
{YELLOW}Troubleshooting de audio (Windows):{NC}
  - Verificar: Settings > System > Sound > Input
  - Privacidad: Settings > Privacy & Security > Microphone
  - USB: desconectar y reconectar
""")

# --- Run application ---

def run_application(mode):
    """Launch the actual application using venv python."""
    venv_py = get_venv_python()

    if mode == "cli":
        target = SCRIPT_DIR / "transcribe.py"
    else:
        target = SCRIPT_DIR / "floating_button_qt.py"

    label = "CLI" if mode == "cli" else "GUI"
    print(f"Iniciando modo {label}...")
    print()

    if PLAT == "windows":
        sys.exit(subprocess.call([str(venv_py), str(target)]))
    else:
        os.execv(str(venv_py), [str(venv_py), str(target)])

# --- Main ---

def main():
    args = parse_args()
    mode = "cli" if args.cli else "gui"

    print_banner(mode)
    check_python_version()
    check_system_dependencies()
    ensure_venv()
    ensure_dependencies()

    if not args.skip_audio_check:
        verify_audio_devices(fix_audio=args.fix_audio)
        print()

    run_application(mode)

if __name__ == "__main__":
    main()
