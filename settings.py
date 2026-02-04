"""
Persistent settings and translations for the transcription app.
"""
import json
import os

# Settings file path (same directory as the script)
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "app_settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "language": "es",
    "device_id": None,
    "groq_api_key": "",
    "button_size": "normal",    # small, normal, large, xlarge
    "orientation": "vertical",  # vertical, horizontal
}

# Translations
TRANSLATIONS = {
    "es": {
        "help_title": "Ayuda",
        "help_app_title": "Audio Transcription",
        "help_current_lang": "Idioma actual",
        "help_record": "Grabar",
        "help_record_desc": "Inicia la grabacion de voz",
        "help_stop": "Stop",
        "help_stop_desc": "Detiene y transcribe. Se copia al portapapeles",
        "help_pause": "Pausa",
        "help_pause_desc": "Pausa temporalmente (no graba)",
        "help_resume": "Reanudar",
        "help_resume_desc": "Continua grabando",
        "help_cancel": "Cancelar",
        "help_cancel_desc": "Descarta sin transcribir",
        "help_buttons": "Botones inferiores",
        "help_tip": "Tip: Podes arrastrar el panel.",
        "help_ok": "OK",
        "settings_title": "Opciones",
        "settings_microphone": "Microfono",
        "settings_language": "Idioma",
        "settings_cancel": "Cancelar",
        "settings_save": "Guardar",
        "settings_saved": "Guardado",
        "settings_saved_msg": "Configuracion guardada.",
        "device_title": "Audio Transcription",
        "device_select": "Selecciona tu microfono:",
        "device_cancel": "Cancelar",
        "device_start": "Iniciar",
        "device_select_btn": "Seleccionar",
        "tooltip_help": "Ayuda",
        "tooltip_settings": "Opciones",
        "tooltip_exit": "Salir",
        "settings_api_key": "Clave API Groq",
        "settings_api_key_hint": "Obtener gratis en console.groq.com",
        "settings_appearance": "Apariencia",
        "settings_button_size": "Tamano de botones",
        "settings_orientation": "Orientacion del panel",
        "size_mini": "Mini",
        "size_small": "Chico",
        "size_normal": "Normal",
        "size_large": "Grande",
        "size_xlarge": "Muy grande",
        "orientation_vertical": "Vertical",
        "orientation_horizontal": "Horizontal",
    },
    "en": {
        "help_title": "Help",
        "help_app_title": "Audio Transcription",
        "help_current_lang": "Current language",
        "help_record": "Record",
        "help_record_desc": "Start voice recording",
        "help_stop": "Stop",
        "help_stop_desc": "Stop and transcribe. Copied to clipboard",
        "help_pause": "Pause",
        "help_pause_desc": "Pause temporarily (not recording)",
        "help_resume": "Resume",
        "help_resume_desc": "Continue recording",
        "help_cancel": "Cancel",
        "help_cancel_desc": "Discard without transcribing",
        "help_buttons": "Bottom buttons",
        "help_tip": "Tip: You can drag the panel.",
        "help_ok": "OK",
        "settings_title": "Settings",
        "settings_microphone": "Microphone",
        "settings_language": "Language",
        "settings_cancel": "Cancel",
        "settings_save": "Save",
        "settings_saved": "Saved",
        "settings_saved_msg": "Settings saved.",
        "device_title": "Audio Transcription",
        "device_select": "Select your microphone:",
        "device_cancel": "Cancel",
        "device_start": "Start",
        "device_select_btn": "Select",
        "tooltip_help": "Help",
        "tooltip_settings": "Settings",
        "tooltip_exit": "Exit",
        "settings_api_key": "Groq API Key",
        "settings_api_key_hint": "Get free at console.groq.com",
        "settings_appearance": "Appearance",
        "settings_button_size": "Button size",
        "settings_orientation": "Panel orientation",
        "size_mini": "Mini",
        "size_small": "Small",
        "size_normal": "Normal",
        "size_large": "Large",
        "size_xlarge": "Extra large",
        "orientation_vertical": "Vertical",
        "orientation_horizontal": "Horizontal",
    }
}


def load_settings() -> dict:
    """Load settings from file or return defaults."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults for any missing keys
                return {**DEFAULT_SETTINGS, **settings}
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """Save settings to file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


def get_text(key: str, lang: str = None) -> str:
    """Get translated text for the given key."""
    if lang is None:
        lang = load_settings().get("language", "es")

    translations = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
    return translations.get(key, key)


# Global settings instance
_current_settings = None


def get_settings() -> dict:
    """Get current settings (cached)."""
    global _current_settings
    if _current_settings is None:
        _current_settings = load_settings()
    return _current_settings


def update_settings(**kwargs):
    """Update and save settings."""
    global _current_settings
    settings = get_settings()
    settings.update(kwargs)
    save_settings(settings)
    _current_settings = settings
    return settings
