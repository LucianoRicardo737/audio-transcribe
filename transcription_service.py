"""
Transcription services: Groq API (primary) + Whisper local (fallback).
"""
import httpx
from rich.console import Console

from config import (
    GROQ_API_KEY,
    GROQ_ENDPOINT,
    GROQ_MODEL,
    LANGUAGE,
    WHISPER_MODEL,
    WHISPER_DEVICE
)
from settings import get_settings

console = Console()


class TranscriptionService:
    """Handles audio transcription with Groq and Whisper fallback."""

    def __init__(self):
        self.whisper_model = None  # Lazy loaded
        self.language = LANGUAGE  # Can be changed at runtime

    def _get_api_key(self) -> str:
        """Get Groq API key from settings (priority) or env var fallback."""
        saved_key = get_settings().get("groq_api_key", "")
        return saved_key if saved_key else GROQ_API_KEY

    def transcribe_with_groq(self, audio_path: str) -> str:
        """
        Transcribe audio using Groq API.

        Args:
            audio_path: Path to WAV audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            api_key = self._get_api_key()
            if not api_key:
                console.print("[yellow]No Groq API key configured[/yellow]")
                return None

            with open(audio_path, 'rb') as audio_file:
                response = httpx.post(
                    GROQ_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {api_key}"
                    },
                    files={
                        "file": ("audio.wav", audio_file, "audio/wav")
                    },
                    data={
                        "model": GROQ_MODEL,
                        "language": self.language,
                        "response_format": "text"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    return response.text.strip()
                else:
                    console.print(
                        f"[yellow]Groq API error {response.status_code}: "
                        f"{response.text[:100]}[/yellow]"
                    )
                    return None

        except httpx.TimeoutException:
            console.print("[yellow]Groq API timeout[/yellow]")
            return None
        except Exception as e:
            console.print(f"[yellow]Groq error: {e}[/yellow]")
            return None

    def transcribe_with_whisper(self, audio_path: str) -> str:
        """
        Transcribe audio using local Whisper model (fallback).

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            # Lazy load whisper model
            if self.whisper_model is None:
                console.print(
                    f"[cyan]Cargando modelo Whisper '{WHISPER_MODEL}' "
                    f"(primera vez puede tardar)...[/cyan]"
                )
                import whisper
                self.whisper_model = whisper.load_model(
                    WHISPER_MODEL,
                    device=WHISPER_DEVICE
                )
                console.print("[green]Modelo Whisper cargado[/green]")

            result = self.whisper_model.transcribe(
                audio_path,
                language=self.language,
                task="transcribe"
            )

            return result["text"].strip()

        except ImportError:
            console.print(
                "[red]Whisper no instalado. Instalar con: "
                "pip install openai-whisper[/red]"
            )
            return None
        except Exception as e:
            console.print(f"[red]Whisper error: {e}[/red]")
            return None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file using Groq first, fallback to Whisper.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None if all methods failed
        """
        # Try Groq first (faster, free)
        console.print("[cyan]Transcribiendo con Groq...[/cyan]")
        text = self.transcribe_with_groq(audio_path)

        if text:
            console.print("[green]Groq OK[/green]")
            return text

        # Fallback to local Whisper
        console.print("[yellow]Groq fallo, usando Whisper local...[/yellow]")
        text = self.transcribe_with_whisper(audio_path)

        if text:
            console.print("[green]Whisper OK[/green]")
            return text

        console.print("[red]Todos los metodos de transcripcion fallaron[/red]")
        return None
