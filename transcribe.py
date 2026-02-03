#!/usr/bin/env python3
"""
Simple Audio Transcription CLI

Hotkey global para grabar y transcribir audio.
Usa Groq API (gratis) con fallback a Whisper local.

Usage:
    python transcribe.py
"""
import os
import sys
import signal
from pynput import keyboard
from rich.console import Console
from rich.panel import Panel

from config import HOTKEY, COPY_TO_CLIPBOARD, LANGUAGE, GROQ_MODEL
from audio_recorder import AudioRecorder
from transcription_service import TranscriptionService

console = Console()


class TranscriptionApp:
    """Main application for audio transcription with hotkey toggle."""

    def __init__(self):
        self.recorder = AudioRecorder()
        self.transcriber = TranscriptionService()
        self.is_recording = False
        self.running = True
        self.current_keys = set()

        # Parse hotkey
        self.hotkey_parts = self._parse_hotkey(HOTKEY)

    def _parse_hotkey(self, hotkey_str: str) -> set:
        """Parse hotkey string like '<ctrl>+<alt>+space' into key set."""
        parts = hotkey_str.lower().replace('<', '').replace('>', '').split('+')
        key_set = set()

        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                key_set.add(keyboard.Key.ctrl_l)
                key_set.add(keyboard.Key.ctrl_r)
            elif part == 'alt':
                key_set.add(keyboard.Key.alt_l)
                key_set.add(keyboard.Key.alt_r)
            elif part == 'shift':
                key_set.add(keyboard.Key.shift_l)
                key_set.add(keyboard.Key.shift_r)
            elif part == 'space':
                key_set.add(keyboard.Key.space)
            elif len(part) == 1:
                key_set.add(keyboard.KeyCode.from_char(part))
            else:
                # Try as special key
                try:
                    key_set.add(getattr(keyboard.Key, part))
                except AttributeError:
                    console.print(f"[yellow]Tecla desconocida: {part}[/yellow]")

        return key_set

    def _check_hotkey_pressed(self) -> bool:
        """Check if the hotkey combination is currently pressed."""
        # Need ctrl (left or right)
        has_ctrl = (keyboard.Key.ctrl_l in self.current_keys or
                    keyboard.Key.ctrl_r in self.current_keys)
        # Need alt (left or right)
        has_alt = (keyboard.Key.alt_l in self.current_keys or
                   keyboard.Key.alt_r in self.current_keys)
        # Need space
        has_space = keyboard.Key.space in self.current_keys

        return has_ctrl and has_alt and has_space

    def setup(self):
        """Initial setup: show banner and select microphone."""
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Audio Transcription CLI[/bold cyan]\n\n"
            f"Hotkey: [green]{HOTKEY}[/green]\n"
            f"Idioma: [yellow]{LANGUAGE}[/yellow]\n"
            f"Modelo: [dim]{GROQ_MODEL}[/dim]",
            title="Config",
            border_style="blue"
        ))

        console.print("\n[bold]Paso 1: Selecciona tu microfono[/bold]\n")
        self.recorder.select_device_interactive()

    def toggle_recording(self):
        """Toggle recording state."""
        if self.is_recording:
            # Stop recording and transcribe
            self.is_recording = False
            console.print("\n[yellow]Procesando...[/yellow]")

            audio_path = self.recorder.stop_recording()

            if audio_path:
                # Transcribe
                text = self.transcriber.transcribe(audio_path)

                if text:
                    # Show result
                    console.print()
                    console.print(Panel(
                        text,
                        title="Transcripcion",
                        border_style="green",
                        padding=(1, 2)
                    ))

                    # Copy to clipboard
                    if COPY_TO_CLIPBOARD:
                        try:
                            import pyperclip
                            pyperclip.copy(text)
                            console.print("[dim]Copiado al portapapeles[/dim]")
                        except ImportError:
                            console.print(
                                "[dim]pyperclip no instalado, "
                                "no se pudo copiar[/dim]"
                            )
                        except Exception as e:
                            console.print(f"[dim]No se pudo copiar: {e}[/dim]")

                # Cleanup temp file
                try:
                    os.unlink(audio_path)
                except Exception:
                    pass

            console.print(
                f"\n[dim]Presiona {HOTKEY} para grabar, Ctrl+C para salir[/dim]"
            )

        else:
            # Start recording
            self.is_recording = True
            console.print(
                f"\n[bold red]GRABANDO...[/bold red] "
                f"(presiona {HOTKEY} para detener)"
            )
            self.recorder.start_recording()

    def on_press(self, key):
        """Handle key press events."""
        self.current_keys.add(key)

        if self._check_hotkey_pressed():
            # Debounce: only toggle if we weren't already in hotkey state
            if not hasattr(self, '_hotkey_active') or not self._hotkey_active:
                self._hotkey_active = True
                self.toggle_recording()

    def on_release(self, key):
        """Handle key release events."""
        self.current_keys.discard(key)

        # Reset hotkey active state when any part of combo is released
        if not self._check_hotkey_pressed():
            self._hotkey_active = False

        # Check for Escape to exit
        if key == keyboard.Key.esc:
            console.print("\n[yellow]Saliendo...[/yellow]")
            return False  # Stop listener

    def run(self):
        """Main run loop."""
        self.setup()

        console.print(f"\n[bold green]Listo![/bold green]")
        console.print(
            f"Presiona [cyan]{HOTKEY}[/cyan] para iniciar/detener grabacion"
        )
        console.print("[dim]Presiona Ctrl+C o Esc para salir[/dim]\n")

        # Setup keyboard listener
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                console.print("\n[yellow]Saliendo...[/yellow]")


def main():
    """Entry point."""
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        console.print("\n[yellow]Saliendo...[/yellow]")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Run app
    app = TranscriptionApp()
    app.run()


if __name__ == "__main__":
    main()
