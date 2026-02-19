import logging
from fastapi import APIRouter
from backend.core.feature_flags import require_feature, FeatureFlag

logger = logging.getLogger(__name__)
router = APIRouter()


# Health Check
@router.get("/health")
async def health_v2():
    """
    V2 health check endpoint.
    Returns enhanced health information including feature flag status.
    """
    from backend.core.feature_flags import get_feature_flags

    flags = get_feature_flags()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features_enabled": flags.get_all_flags(),
    }


# Include Sub-Routers with graceful error handling for missing dependencies
# 1. Clinical (AG-03) - requires TensorFlow
try:
    from backend.api.routes import v2_clinical
    router.include_router(v2_clinical.router, tags=["clinical"])
except ImportError as e:
    logger.warning(f"v2_clinical router not loaded: {e}")

# 2. Predict (AG-01) - requires TensorFlow
try:
    from backend.api.routes import v2_predict
    router.include_router(v2_predict.router, tags=["predict"])
except ImportError as e:
    logger.warning(f"v2_predict router not loaded: {e}")

# 3. Voice (AG-04) - lightweight, no TensorFlow dependency
from backend.api.routes import v2_voice
router.include_router(v2_voice.router)

# 4. Chat (Multilingual) - lightweight, no TensorFlow dependency
from backend.api.routes import v2_chat
router.include_router(v2_chat.router, tags=["chat-v2"])
