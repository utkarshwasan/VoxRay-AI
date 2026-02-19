"""
VoxRay AI — Multilingual Configuration
Handles language-specific settings for TTS voices and display names.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class LanguageConfig:
    """Configuration for a supported language."""
    language: str  # ISO 639-1 code
    tts_voice: str  # Edge TTS voice identifier
    display_name: str  # Native language name for UI


# Supported language configurations
# Hindi disabled: whisper-base cannot distinguish spoken Hindi from Urdu (phonetically
# identical). Re-enable by upgrading STT to faster-whisper medium and uncommenting
# all lines marked '# hi-disabled' across multilingual.py, main.py, VoiceSection.jsx.
LANGS: Dict[str, LanguageConfig] = {
    # "hi": LanguageConfig(  # hi-disabled
    #     language="hi", tts_voice="hi-IN-SwaraNeural", display_name="हिन्दी"  # hi-disabled
    # ),  # hi-disabled
    "ur": LanguageConfig(
        language="ur", tts_voice="ur-PK-UzmaNeural", display_name="اردو"
    ),
    "en": LanguageConfig(
        language="en", tts_voice="en-US-ChristopherNeural", display_name="English"
    ),
    "es": LanguageConfig(
        language="es", tts_voice="es-ES-AlvaroNeural", display_name="Español"
    ),
    "fr": LanguageConfig(
        language="fr", tts_voice="fr-FR-HenriNeural", display_name="Français"
    ),
    "de": LanguageConfig(
        language="de", tts_voice="de-DE-ConradNeural", display_name="Deutsch"
    ),
    "zh": LanguageConfig(
        language="zh", tts_voice="zh-CN-XiaoxiaoNeural", display_name="中文"
    ),
}


def get_language_config(language_code: str) -> LanguageConfig:
    """Get language configuration by ISO code."""
    return LANGS.get(language_code)


def get_supported_languages() -> Dict[str, str]:
    """Get mapping of language codes to display names."""
    return {code: config.display_name for code, config in LANGS.items()}


def validate_language_code(language_code: str) -> bool:
    """Validate if a language code is supported."""
    return language_code in LANGS


# Script detection helpers — used by TTS pre-flight validation and STT post-validation.
# Maps ISO language code → expected Unicode script name.
# None = script-agnostic (e.g. CJK), skip script check entirely.
LANG_SCRIPT_MAP: Dict[str, "str | None"] = {
    # 'hi': 'devanagari',  # hi-disabled — whisper-base cannot distinguish Hindi/Urdu
    'ur': 'arabic',
    'ar': 'arabic',
    'en': 'latin',
    'es': 'latin',
    'fr': 'latin',
    'de': 'latin',
    'pt': 'latin',
    'zh': None,
    'ja': None,
    'ko': None,
}

# Full Whisper language names for forced_decoder_ids / language parameter.
LANG_WHISPER_NAME: Dict[str, str] = {
    # 'hi': 'hindi',  # hi-disabled
    'ur': 'urdu',
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'pt': 'portuguese',
    'zh': 'chinese',
    'ja': 'japanese',
    'ko': 'korean',
    'ar': 'arabic',
}

# Scripts that Edge-TTS voices physically CANNOT render (causes NoAudioReceived crash).
# Runtime-verified: Latin text through hi-IN-SwaraNeural succeeds (27 chunks).
# Only Arabic/Nastaliq through Hindi voice fails. Do NOT over-block.
# Key = ISO language code, Value = set of script names that are incompatible.
TTS_INCOMPATIBLE_SCRIPTS: Dict[str, set] = {
    # 'hi': {'arabic'},  # hi-disabled
    'ur': {'devanagari', 'latin'},
    'zh': {'arabic', 'devanagari'},
    'ja': {'arabic', 'devanagari'},
    'ko': {'arabic', 'devanagari'},
}