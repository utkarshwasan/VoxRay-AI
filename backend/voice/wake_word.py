from __future__ import annotations
from dataclasses import dataclass
# duplicate removed


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
        # Stub implementation always returning not supported/not detected
        return WakeWordResult(
            supported=False,
            detected=False,
            confidence=0.0,
            message="Wake word detection not implemented (no engine configured).",
        )
