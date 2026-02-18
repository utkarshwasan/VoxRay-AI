from fastapi import APIRouter
from backend.core.feature_flags import require_feature, FeatureFlag

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


# Include Sub-Routers
# 1. Clinical (AG-03)
from backend.api.routes import v2_clinical

router.include_router(v2_clinical.router, tags=["clinical"])

# 2. Predict (AG-01)
from backend.api.routes import v2_predict

router.include_router(v2_predict.router, tags=["predict"])

# 3. Voice (AG-04)
from backend.api.routes import v2_voice

router.include_router(v2_voice.router)

# 4. Chat (Multilingual)
from backend.api.routes import v2_chat

router.include_router(v2_chat.router, tags=["chat-v2"])
