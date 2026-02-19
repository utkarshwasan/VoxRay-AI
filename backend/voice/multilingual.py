from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class LanguageConfig:
    language: str  # ISO code
    tts_voice: str  # Edge TTS voice ID
    display_name: str  # UI display name


LANGS: Dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        language="en", tts_voice="en-US-ChristopherNeural", display_name="English"
    ),
    "es": LanguageConfig(
        language="es", tts_voice="es-ES-AlvaroNeural", display_name="Español"
    ),
    "fr": LanguageConfig(
        language="fr", tts_voice="fr-FR-DeniseNeural", display_name="Français"
    ),
    "de": LanguageConfig(
        language="de", tts_voice="de-DE-KatjaNeural", display_name="Deutsch"
    ),
    "zh": LanguageConfig(
        language="zh", tts_voice="zh-CN-XiaoxiaoNeural", display_name="中文"
    ),
    "hi": LanguageConfig(
        language="hi", tts_voice="hi-IN-SwaraNeural", display_name="हिन्दी"
    ),
}


def get_language_config(lang: Optional[str]) -> LanguageConfig:
    """Get language config with English fallback."""
    if not lang:
        return LANGS["en"]
    return LANGS.get(lang, LANGS["en"])


def get_all_languages() -> Dict[str, LanguageConfig]:
    """Return all supported languages for UI dropdowns."""
    return LANGS

# Script expected per language ISO code.
# Used for TTS pre-flight validation and STT post-validation.
# None = CJK/script-agnostic, skip check entirely.
LANG_SCRIPT_MAP: Dict[str, Optional[str]] = {
    'hi': 'devanagari',
    'mr': 'devanagari',
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

# Full Whisper language names for get_decoder_prompt_ids()
LANG_WHISPER_NAME: Dict[str, str] = {
    'hi': 'hindi',
    'ur': 'urdu',
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'pt': 'portuguese',
    'zh': 'chinese',
    'ja': 'japanese',
    'ko': 'korean',
    'mr': 'marathi',
    'ar': 'arabic',
}

# Scripts that Edge-TTS voices physically CANNOT render � causes NoAudioReceived.
# Runtime-verified: Latin text through hi-IN-SwaraNeural succeeds (27 chunks).
# Only Arabic/Nastaliq through Hindi voice fails. Do not over-block.
TTS_INCOMPATIBLE_SCRIPTS: Dict[str, set] = {
    'hi': {'arabic'},
    'ur': {'devanagari'},
    'zh': {'arabic', 'devanagari'},
    'ja': {'arabic', 'devanagari'},
    'ko': {'arabic', 'devanagari'},
}

