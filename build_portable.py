#!/usr/bin/env python3
"""
Build a portable executable of Audio Transcribe using PyInstaller.

Cross-platform script that:
1. Creates a temporary build venv
2. Installs minimal dependencies + PyInstaller
3. Runs PyInstaller with the .spec file
4. Shows resulting file size
5. Cleans up build venv

Usage:
    python build_portable.py
    python build_portable.py --keep-venv    # Don't delete build venv after
    python build_portable.py --no-clean     # Keep build artifacts (build/, dist/)

Output:
    dist/AudioTranscribe        (Linux/macOS)
    dist/AudioTranscribe.exe    (Windows)
"""
import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PLAT = platform.system().lower()
BUILD_VENV = SCRIPT_DIR / ".build_venv"


def supports_color():
    if PLAT == "windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


if supports_color():
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    DIM = '\033[2m'
    NC = '\033[0m'
else:
    GREEN = YELLOW = CYAN = RED = DIM = NC = ''


def get_venv_python():
    if PLAT == "windows":
        return BUILD_VENV / "Scripts" / "python.exe"
    return BUILD_VENV / "bin" / "python"


def get_venv_pip():
    if PLAT == "windows":
        return BUILD_VENV / "Scripts" / "pip.exe"
    return BUILD_VENV / "bin" / "pip"


def parse_args():
    parser = argparse.ArgumentParser(description="Build portable Audio Transcribe executable")
    parser.add_argument('--keep-venv', action='store_true', help="Don't delete build venv after build")
    parser.add_argument('--no-clean', action='store_true', help="Keep build artifacts (build/ directory)")
    return parser.parse_args()


def print_banner():
    plat_name = {"linux": "Linux", "darwin": "macOS", "windows": "Windows"}.get(PLAT, PLAT)
    print(f"{CYAN}========================================{NC}")
    print(f"{CYAN}   Audio Transcribe - Build Portable{NC}")
    print(f"{CYAN}   {DIM}{plat_name} - Python {sys.version.split()[0]}{NC}")
    print(f"{CYAN}========================================{NC}")
    print()


def create_build_venv():
    if BUILD_VENV.exists():
        print(f"{DIM}Eliminando build venv anterior...{NC}")
        shutil.rmtree(BUILD_VENV)

    print(f"{YELLOW}Creando build venv...{NC}")
    subprocess.check_call(
        [sys.executable, "-m", "venv", str(BUILD_VENV)],
        stdout=subprocess.DEVNULL
    )
    print(f"{GREEN}Build venv creado{NC}")


def install_build_deps():
    pip = get_venv_pip()

    print(f"{YELLOW}Instalando dependencias de build...{NC}")

    # Upgrade pip
    subprocess.check_call(
        [str(pip), "install", "--upgrade", "pip", "-q"],
        stdout=subprocess.DEVNULL
    )

    # Install app dependencies (without Whisper)
    req = SCRIPT_DIR / "requirements.txt"
    subprocess.check_call([str(pip), "install", "-r", str(req), "-q"])

    # Install PyInstaller
    subprocess.check_call([str(pip), "install", "pyinstaller", "-q"])

    print(f"{GREEN}Dependencias de build instaladas{NC}")


def run_pyinstaller():
    venv_py = get_venv_python()
    spec_file = SCRIPT_DIR / "AudioTranscribe.spec"

    print(f"{YELLOW}Ejecutando PyInstaller...{NC}")
    print(f"{DIM}Esto puede tardar unos minutos...{NC}")
    print()

    result = subprocess.run(
        [str(venv_py), "-m", "PyInstaller", str(spec_file), "--noconfirm"],
        cwd=str(SCRIPT_DIR)
    )

    if result.returncode != 0:
        print(f"{RED}PyInstaller fallo con codigo {result.returncode}{NC}")
        sys.exit(1)

    print()
    print(f"{GREEN}Build completado exitosamente{NC}")


def show_result():
    if PLAT == "windows":
        exe_path = SCRIPT_DIR / "dist" / "AudioTranscribe.exe"
    else:
        exe_path = SCRIPT_DIR / "dist" / "AudioTranscribe"

    if not exe_path.exists():
        print(f"{RED}Ejecutable no encontrado en {exe_path}{NC}")
        return

    size_mb = exe_path.stat().st_size / (1024 * 1024)

    print()
    print(f"{CYAN}========================================{NC}")
    print(f"{GREEN}Ejecutable generado:{NC}")
    print(f"  {exe_path}")
    print(f"  Tamano: {size_mb:.1f} MB")
    print(f"{CYAN}========================================{NC}")
    print()
    print(f"{DIM}Para ejecutar:{NC}")
    if PLAT == "windows":
        print(f"  dist\\AudioTranscribe.exe")
    else:
        print(f"  ./dist/AudioTranscribe")
    print()
    print(f"{YELLOW}Nota: Este ejecutable solo funciona en {platform.system()}.{NC}")
    print(f"{YELLOW}Para otros OS, ejecutar build_portable.py en ese sistema.{NC}")


def cleanup(keep_venv=False, no_clean=False):
    if not keep_venv and BUILD_VENV.exists():
        print(f"{DIM}Eliminando build venv...{NC}")
        shutil.rmtree(BUILD_VENV)

    if not no_clean:
        build_dir = SCRIPT_DIR / "build"
        if build_dir.exists():
            print(f"{DIM}Eliminando directorio build/...{NC}")
            shutil.rmtree(build_dir)


def main():
    args = parse_args()
    print_banner()

    # Check Python version
    if sys.version_info < (3, 10):
        print(f"{RED}Se requiere Python 3.10+{NC}")
        sys.exit(1)

    try:
        create_build_venv()
        install_build_deps()
        run_pyinstaller()
        show_result()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error durante el build: {e}{NC}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Build cancelado{NC}")
        sys.exit(1)
    finally:
        cleanup(keep_venv=args.keep_venv, no_clean=args.no_clean)


if __name__ == "__main__":
    main()
