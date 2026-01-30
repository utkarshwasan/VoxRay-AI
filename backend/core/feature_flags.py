import os
import logging
from enum import Enum
from functools import wraps
from typing import Dict, Optional, Callable

logger = logging.getLogger(__name__)


class FeatureFlag(Enum):
    """
    All feature flags for VoxRay AI v2.0.
    Values map to env vars FF_<VALUE.upper()>.
    """

    # ML Core
    ENSEMBLE_MODEL = "ensemble_model"
    UNCERTAINTY_QUANTIFICATION = "uncertainty_quantification"
    CROSS_VALIDATION = "cross_validation"
    BENCHMARKING = "benchmarking"

    # Clinical
    DICOM_SUPPORT = "dicom_support"
    FHIR_INTEGRATION = "fhir_integration"
    AUDIT_LOGGING = "audit_logging"
    DATA_ANONYMIZATION = "data_anonymization"

    # Voice
    WAKE_WORD_DETECTION = "wake_word_detection"
    MULTILINGUAL_VOICE = "multilingual_voice"
    MEDICAL_VOCABULARY = "medical_vocabulary"
    NOISE_HANDLING = "noise_handling"

    # Frontend / UX
    ADVANCED_HEATMAP = "advanced_heatmap"
    WORKLIST_MANAGEMENT = "worklist_management"
    BATCH_PROCESSING = "batch_processing"
    MOBILE_PWA = "mobile_pwa"


class FeatureFlags:
    """
    Manages application-wide feature toggles.
    Flags are loaded from Environment Variables (FF_<NAME>).
    """

    def __init__(self):
        self._flags: Dict[FeatureFlag, bool] = {}
        self.reload()

    def reload(self) -> None:
        """
        Reloads flags from current environment variables.
        Example var: FF_ENSEMBLE_MODEL=true
        """
        self._flags.clear()
        for flag in FeatureFlag:
            env_key = f"FF_{flag.value.upper()}"
            raw = os.getenv(env_key, "false").strip().lower()
            enabled = raw in ("true", "1", "yes", "on", "enabled")
            self._flags[flag] = enabled
            logger.info(f"[FeatureFlags] {flag.value} = {enabled}")

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """
        Check if a specific feature flag is enabled.
        """
        return self._flags.get(flag, False)

    def get_all_flags(self) -> Dict[str, bool]:
        return {flag.value: enabled for flag, enabled in self._flags.items()}


# Singleton instance
_feature_flags_instance = FeatureFlags()


def get_feature_flags() -> FeatureFlags:
    return _feature_flags_instance


def check_flag(flag: FeatureFlag) -> bool:
    return _feature_flags_instance.is_enabled(flag)


def require_feature(flag: FeatureFlag):
    """
    Decorator to gate endpoints behind a feature flag.
    If disabled, returns 503 with FEATURE_NOT_ENABLED.
    """
    from fastapi import HTTPException

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not check_flag(flag):
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "FEATURE_NOT_ENABLED",
                        "message": f"Feature '{flag.value}' is not enabled. "
                        f"Set FF_{flag.value.upper()}=true to enable.",
                        "feature_flag": flag.value,
                    },
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
