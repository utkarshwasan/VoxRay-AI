from __future__ import annotations
import numpy as np


class NoiseEstimator:
    def estimate_rms(self, audio: np.ndarray) -> float:
        if audio.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio**2)))

    def adaptive_threshold(self, noise_floor: float, multiplier: float = 2.5) -> float:
        return float(noise_floor * multiplier)
