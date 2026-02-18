import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from backend.core.feature_flags import (
    require_feature,
    FeatureFlag,
    check_flag,
)
from backend.serving.model_server import ModelServer
from backend.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()
model_server = ModelServer()


@router.post("/predict/image")
@require_feature(FeatureFlag.ENSEMBLE_MODEL)
async def predict_image_v2(
    file: UploadFile = File(...),
    enable_uncertainty: bool = Query(
        False, description="Run MC Dropout uncertainty (slower)"
    ),
    user: dict = Depends(get_current_user),
):
    """
    V2 prediction endpoint (ensemble + optional uncertainty).

    - Uses ModelServer (ensemble + MC Dropout).
    - Gated by FF_ENSEMBLE_MODEL.
    - Optional MC Dropout gated by FF_UNCERTAINTY_QUANTIFICATION.

    Does NOT change v1 behavior. v1 /predict/image remains as-is.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG or PNG is supported.",
        )

    if model_server.ensemble is None:
        logger.error("[v2] ModelServer ensemble not initialized.")
        raise HTTPException(
            status_code=503,
            detail="Ensemble model is not available.",
        )

    try:
        image_bytes = await file.read()

        run_uncertainty = bool(enable_uncertainty) and check_flag(
            FeatureFlag.UNCERTAINTY_QUANTIFICATION
        )

        result = model_server.predict(image_bytes, run_uncertainty=run_uncertainty)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "diagnosis": result["diagnosis"],
            "confidence": result["confidence"],
            "uncertainty": result.get("uncertainty"),
            "ensemble": result.get("ensemble"),
            "benchmark_comparison": result.get("benchmark_comparison"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v2] Error in /v2/predict/image: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal Server Error during prediction."
        )
