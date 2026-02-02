"""
Audio recording with microphone selection using sounddevice.
"""
import sounddevice as sd
import numpy as np
import tempfile
import threading
from scipy.io import wavfile
from rich.console import Console
from rich.table import Table

from config import SAMPLE_RATE, CHANNELS

console = Console()


class AudioRecorder:
    """Records audio from a selected microphone."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS):
        self.target_sample_rate = sample_rate  # Para output final
        self.sample_rate = sample_rate  # Puede cambiar segun dispositivo
        self.channels = channels
        self.device_id = None
        self.recording_data = []
        self.is_recording = False
        self.stream = None
        self._lock = threading.Lock()

    def list_devices(self) -> list:
        """List available input devices."""
        devices = sd.query_devices()
        input_devices = []

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': int(device['default_samplerate']),
                    'is_default': i == sd.default.device[0]
                })

        return input_devices

    def select_device_interactive(self) -> int:
        """Show interactive device selection and return selected device ID."""
        devices = self.list_devices()

        if not devices:
            console.print("[red]No se encontraron dispositivos de entrada![/red]")
            return None

        # Build table
        table = Table(title="Microfonos Disponibles")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Nombre", style="green")
        table.add_column("Canales", style="yellow", justify="center")
        table.add_column("Default", style="magenta", justify="center")

        default_id = None
        for device in devices:
            is_default = "*" if device['is_default'] else ""
            if device['is_default']:
                default_id = device['id']
            table.add_row(
                str(device['id']),
                device['name'][:50],  # Truncate long names
                str(device['channels']),
                is_default
            )

        console.print(table)

        # Get user selection
        while True:
            prompt = f"\n[bold]Selecciona ID del microfono[/bold] (Enter para default [{default_id}]): "
            choice = console.input(prompt).strip()

            if choice == "":
                self.device_id = default_id
                selected = next((d for d in devices if d['id'] == default_id), None)
                if selected:
                    self.sample_rate = selected['sample_rate']
                    console.print(f"[green]Seleccionado: {selected['name']}[/green]")
                    console.print(f"[dim]Sample rate: {self.sample_rate}Hz[/dim]")
                break

            try:
                device_id = int(choice)
                if any(d['id'] == device_id for d in devices):
                    self.device_id = device_id
                    selected = next(d for d in devices if d['id'] == device_id)
                    # Usar sample rate nativo del dispositivo
                    self.sample_rate = selected['sample_rate']
                    console.print(f"[green]Seleccionado: {selected['name']}[/green]")
                    console.print(f"[dim]Sample rate: {self.sample_rate}Hz[/dim]")
                    break
                else:
                    console.print("[red]ID invalido, intenta de nuevo[/red]")
            except ValueError:
                console.print("[red]Ingresa un numero[/red]")

        return self.device_id

    def start_recording(self):
        """Start recording audio."""
        with self._lock:
            if self.is_recording:
                console.print("[yellow]Ya esta grabando[/yellow]")
                return

            self.recording_data = []
            self.is_recording = True

        def audio_callback(indata, frames, time, status):
            if status:
                console.print(f"[yellow]Audio status: {status}[/yellow]")
            if self.is_recording:
                self.recording_data.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
                dtype=np.float32
            )
            self.stream.start()
        except Exception as e:
            self.is_recording = False
            console.print(f"[red]Error iniciando grabacion: {e}[/red]")
            raise

    def stop_recording(self) -> str:
        """Stop recording and return path to temporary WAV file."""
        with self._lock:
            if not self.is_recording:
                return None
            self.is_recording = False

        # Stop stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.recording_data:
            console.print("[yellow]No se grabo audio[/yellow]")
            return None

        # Combine all chunks
        audio_data = np.concatenate(self.recording_data, axis=0)

        # If stereo, take first channel
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        # Calculate duration
        duration = len(audio_data) / self.sample_rate
        console.print(f"[dim]Duracion: {duration:.1f}s[/dim]")

        # Resample to target rate (16000Hz) if needed for Groq/Whisper
        if self.sample_rate != self.target_sample_rate:
            from scipy import signal
            num_samples = int(len(audio_data) * self.target_sample_rate / self.sample_rate)
            audio_data = signal.resample(audio_data, num_samples)
            console.print(f"[dim]Resampled: {self.sample_rate}Hz -> {self.target_sample_rate}Hz[/dim]")

        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

        # Convert float32 [-1, 1] to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)

        wavfile.write(temp_file.name, self.target_sample_rate, audio_int16)

        return temp_file.name

    def get_recording_status(self) -> bool:
        """Check if currently recording."""
        return self.is_recording
