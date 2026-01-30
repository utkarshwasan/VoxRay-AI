"""
VoxRay AI v2.0 Enhanced Endpoints

This module contains the v2 API endpoints with enhanced features:
- Ensemble model predictions
- Uncertainty quantification
- DICOM support
- FHIR integration
- Enhanced voice features

All endpoints are feature-gated and will return 503 if the required
feature flag is not enabled.
"""

from fastapi import APIRouter, HTTPException
from backend.core.feature_flags import require_feature, FeatureFlag

router = APIRouter()


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


# Placeholder for future v2 endpoints
# AG-01 will implement:
# - POST /predict/ensemble
# - POST /predict/uncertainty
#
# AG-03 will implement:
# - POST /predict/dicom
# - GET /fhir/diagnostic-report/{patient_id}
#
# AG-04 will implement:
# - POST /voice/wake-word-detect
# - POST /transcribe/enhanced
