"""
Configuration for the simple transcription CLI.
Can be overridden with environment variables.
"""
import os

# Groq API Configuration
# Obtener key gratis en: https://console.groq.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3-turbo"

# Language for transcription
LANGUAGE = os.getenv("TRANSCRIBE_LANGUAGE", "es")  # Spanish

# Hotkey configuration
# Format for pynput: <ctrl>+<alt>+<space>
HOTKEY = os.getenv("TRANSCRIBE_HOTKEY", "<ctrl>+<alt>+space")

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1

# Whisper fallback settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # tiny, base, small, medium, large
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")  # cuda or cpu

# Output settings
COPY_TO_CLIPBOARD = True

# GUI settings (for floating_button_qt.py)
# Position: top-left, top-right, bottom-left, bottom-right, center
BUTTON_POSITION = os.getenv("BUTTON_POSITION", "bottom-right")
BUTTON_SIZE = int(os.getenv("BUTTON_SIZE", "50"))
BUTTON_OPACITY = float(os.getenv("BUTTON_OPACITY", "0.9"))
