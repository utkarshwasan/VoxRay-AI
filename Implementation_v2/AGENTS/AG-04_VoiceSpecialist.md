## File 15: `Implementation_v2/AGENTS/AG-04_VoiceSpecialist.md`

````markdown
# AG-04: Voice Specialist (Wake Word / Medical Vocab / Spanish / Noise)

**Role:** Voice AI & Multilingual  
**Phase:** 3  
**Duration:** Days 10–16  
**Dependencies:** AG-00 complete  
**Blocking:** NO (voice enhancements can ship disabled behind flags)

---

## Mission

Enhance the voice system WITHOUT breaking existing:

- v1 voice flow: browser recording -> `/transcribe/audio` -> `/chat` -> `/generate/speech`
- Sterile mode VAD in frontend (already exists)

Add new features behind flags:

- Wake word detection (optional; if no library/key, implement stub + disable flag)
- Medical vocabulary post-processing
- Spanish language support (prompt + TTS voice)
- Noise robustness guidance (adaptive thresholds)

---

## Required Reading

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/06_FEATURE_FLAGS.md`
- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `shared_context/CTX_SYNC.md`

---

## Constraints

- DO NOT change existing `/transcribe/audio` response shape
- DO NOT change existing `/generate/speech` streaming behavior
- Add new endpoints only under `/v2/voice/*`
- If wake-word library isn't available, return `503 FEATURE_NOT_ENABLED` or mark feature as not supported
- Never store raw audio unless explicitly required; avoid PHI risk

---

## Outputs

- `backend/voice/medical_vocabulary.py`
- `backend/voice/multilingual.py`
- `backend/voice/noise_handler.py`
- `backend/voice/wake_word.py` (interface + optional integration)
- Update `backend/api/v2.py`:
  - POST `/v2/voice/enhance-transcription`
  - POST `/v2/voice/wake-word-detect` (optional)

---

## Task 4.1 — Create Directories

```bash
mkdir -p backend/voice tests/voice docs/voice
Task 4.2 — Medical Vocabulary Post-Processor
Create backend/voice/medical_vocabulary.py

Python

from __future__ import annotations
from typing import Dict

DEFAULT_CORRECTIONS: Dict[str, str] = {
    "plural effusion": "pleural effusion",
    "consultation": "consolidation",
    "ammonia": "pneumonia",
}

class MedicalVocabulary:
    def __init__(self, corrections: Dict[str, str] | None = None):
        self.corrections = corrections or DEFAULT_CORRECTIONS

    def post_process(self, text: str) -> str:
        if not text:
            return text
        out = text
        for wrong, right in self.corrections.items():
            out = out.replace(wrong, right)
        return out
Task 4.3 — Multilingual Support Helper (Spanish)
Create backend/voice/multilingual.py

Rule: keep minimal; do not assume availability of language detection.
Provide a simple “forced language” option.

Python

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class LanguageConfig:
    language: str  # "en" | "es"
    tts_voice: str

LANGS = {
    "en": LanguageConfig(language="en", tts_voice="en-US-ChristopherNeural"),
    "es": LanguageConfig(language="es", tts_voice="es-ES-AlvaroNeural"),
}

def get_language_config(lang: Optional[str]) -> LanguageConfig:
    if not lang:
        return LANGS["en"]
    return LANGS.get(lang, LANGS["en"])
Task 4.4 — Noise Handling (Guidance + adaptive threshold helper)
Create backend/voice/noise_handler.py

Python

from __future__ import annotations
import numpy as np

class NoiseEstimator:
    def estimate_rms(self, audio: np.ndarray) -> float:
        if audio.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio ** 2)))

    def adaptive_threshold(self, noise_floor: float, multiplier: float = 2.5) -> float:
        return float(noise_floor * multiplier)
Task 4.5 — Wake Word (Interface-first, optional implementation)
Create backend/voice/wake_word.py

Important: do not force Porcupine dependency. Provide an interface and a clean “not supported” path.

Python

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class WakeWordResult:
    supported: bool
    detected: bool
    confidence: float
    message: str

class WakeWordDetector:
    """
    Wake-word detection stub.
    If you later add Porcupine or another engine, implement detect().
    """
    def __init__(self, wake_word: str = "hey voxray"):
        self.wake_word = wake_word

    def detect(self, audio_bytes: bytes) -> WakeWordResult:
        return WakeWordResult(
            supported=False,
            detected=False,
            confidence=0.0,
            message="Wake word detection not implemented (no engine configured)."
        )
Task 4.6 — Wire v2 Voice Endpoints (Feature-Gated)
Modify backend/api/v2.py to add endpoints:

/v2/voice/enhance-transcription (requires FF_MEDICAL_VOCABULARY)
/v2/voice/wake-word-detect (requires FF_WAKE_WORD_DETECTION)
Implementation must:

accept text for enhancement endpoint (do not require audio)
return safe JSON
Task 4.7 — Tests
Create tests/voice/test_medical_vocabulary.py:

validate that corrections happen
validate empty input safe
Wake word tests should pass even if unsupported (assert supported==false).

Handoff
Create shared_context/AG-04_handoff.md:

what flags are needed to enable new endpoints
how frontend can request Spanish voice (via lang=es field and/or prompt)
```
````
