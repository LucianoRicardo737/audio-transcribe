"""
Transcription Controller - Reusable orchestration logic.

Extracts transcription logic from TranscriptionApp for use by different UIs
(CLI, GUI, etc.) with thread-safe callbacks.
"""
import os
import threading
from typing import Callable, Optional, List, Dict, Any
from enum import Enum, auto

from audio_recorder import AudioRecorder
from transcription_service import TranscriptionService
from config import COPY_TO_CLIPBOARD


class TranscriptionState(Enum):
    """States for the transcription process."""
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()
    ERROR = auto()


class TranscriptionController:
    """
    Controller for audio transcription with callback-based UI updates.

    Thread-safe for use with GUI frameworks.
    """

    def __init__(
        self,
        on_state_change: Optional[Callable[[TranscriptionState], None]] = None,
        on_recording_start: Optional[Callable[[], None]] = None,
        on_recording_stop: Optional[Callable[[], None]] = None,
        on_transcription_complete: Optional[Callable[[str], None]] = None,
        on_transcription_error: Optional[Callable[[str], None]] = None,
        on_status_message: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the controller with optional callbacks.

        Args:
            on_state_change: Called when state changes (IDLE, RECORDING, PROCESSING)
            on_recording_start: Called when recording starts
            on_recording_stop: Called when recording stops (before processing)
            on_transcription_complete: Called with transcribed text
            on_transcription_error: Called with error message
            on_status_message: Called with status messages for display
        """
        self.recorder = AudioRecorder()
        self.transcriber = TranscriptionService()

        self._state = TranscriptionState.IDLE
        self._lock = threading.Lock()

        # Callbacks
        self.on_state_change = on_state_change
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.on_transcription_complete = on_transcription_complete
        self.on_transcription_error = on_transcription_error
        self.on_status_message = on_status_message

    @property
    def state(self) -> TranscriptionState:
        """Get current state."""
        return self._state

    @state.setter
    def state(self, new_state: TranscriptionState):
        """Set state and trigger callback."""
        self._state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)

    def _emit_status(self, message: str):
        """Emit a status message."""
        if self.on_status_message:
            self.on_status_message(message)

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available audio input devices.

        Returns:
            List of device dicts with id, name, channels, sample_rate, is_default
        """
        return self.recorder.list_devices()

    def select_device(self, device_id: int) -> bool:
        """
        Select an audio input device by ID.

        Args:
            device_id: Device ID from get_available_devices()

        Returns:
            True if device was selected successfully
        """
        devices = self.get_available_devices()
        device = next((d for d in devices if d['id'] == device_id), None)

        if device:
            self.recorder.device_id = device_id
            self.recorder.sample_rate = device['sample_rate']
            self._emit_status(f"Dispositivo: {device['name']}")
            return True
        return False

    def get_selected_device(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected device info."""
        if self.recorder.device_id is None:
            return None
        devices = self.get_available_devices()
        return next((d for d in devices if d['id'] == self.recorder.device_id), None)

    def start_recording(self) -> bool:
        """
        Start audio recording.

        Returns:
            True if recording started successfully
        """
        with self._lock:
            if self._state != TranscriptionState.IDLE:
                return False

            try:
                self.recorder.start_recording()
                self.state = TranscriptionState.RECORDING

                if self.on_recording_start:
                    self.on_recording_start()

                self._emit_status("Grabando...")
                return True

            except Exception as e:
                self.state = TranscriptionState.ERROR
                if self.on_transcription_error:
                    self.on_transcription_error(f"Error al iniciar grabación: {e}")
                return False

    def stop_recording(self) -> bool:
        """
        Stop recording and start transcription in background.

        Returns:
            True if stop was initiated successfully
        """
        with self._lock:
            if self._state != TranscriptionState.RECORDING:
                return False

            self.state = TranscriptionState.PROCESSING

            if self.on_recording_stop:
                self.on_recording_stop()

        # Run transcription in background thread
        thread = threading.Thread(target=self._process_recording, daemon=True)
        thread.start()
        return True

    def _process_recording(self):
        """Process recording in background thread."""
        try:
            self._emit_status("Procesando audio...")
            audio_path = self.recorder.stop_recording()

            if not audio_path:
                self._emit_status("No se grabó audio")
                self.state = TranscriptionState.IDLE
                if self.on_transcription_error:
                    self.on_transcription_error("No se grabó audio")
                return

            self._emit_status("Transcribiendo...")
            text = self.transcriber.transcribe(audio_path)

            # Cleanup temp file
            try:
                os.unlink(audio_path)
            except Exception:
                pass

            if text:
                # Copy to clipboard if enabled
                if COPY_TO_CLIPBOARD:
                    try:
                        import pyperclip
                        pyperclip.copy(text)
                        self._emit_status("Copiado al portapapeles")
                    except Exception:
                        pass

                self.state = TranscriptionState.IDLE
                if self.on_transcription_complete:
                    self.on_transcription_complete(text)
            else:
                self.state = TranscriptionState.IDLE
                if self.on_transcription_error:
                    self.on_transcription_error("Error en transcripción")

        except Exception as e:
            self.state = TranscriptionState.IDLE
            if self.on_transcription_error:
                self.on_transcription_error(f"Error: {e}")

    def toggle_recording(self) -> bool:
        """
        Toggle between recording and idle/processing states.

        Returns:
            True if action was taken
        """
        if self._state == TranscriptionState.IDLE:
            return self.start_recording()
        elif self._state == TranscriptionState.RECORDING:
            return self.stop_recording()
        else:
            # Already processing, ignore
            return False

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._state == TranscriptionState.RECORDING

    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self._state == TranscriptionState.PROCESSING

    def is_idle(self) -> bool:
        """Check if idle and ready."""
        return self._state == TranscriptionState.IDLE
