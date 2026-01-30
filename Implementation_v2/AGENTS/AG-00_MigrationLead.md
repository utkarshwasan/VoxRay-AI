# Agent: AG-00 (Migration Lead)

## Role: System Stability & Transition Manager

## Status: Implementation Ready

This document contains the **concrete Python code and docs** required to safely introduce VoxRay AI v2.0 (ensemble, DICOM, etc.) while **preserving 100% of the current V1 behavior**.

You MUST:

- Keep all V1 endpoints working exactly as now:
  - `POST /predict/image` → `{ diagnosis, confidence }`
  - `POST /transcribe/audio` → `{ transcription }`
  - `POST /generate/speech` → streaming audio
  - `POST /chat` → `{ response }`
  - `GET /health`
- Add:
  - A feature-flag system (for VoxRay-specific features).
  - API versioning with `/v1/*` aliases and `/v2/*` endpoints.
  - Backward compatibility tests.
  - Rollback procedures.

---

## 0. Prerequisites and Context

Read these first:

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 0)
- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `Implementation_v2/SHARED/06_FEATURE_FLAGS.md`
- `shared_context/CTX_SYNC.md` (initialize from template if not done)

Initialize directories (if not present):

````bash
mkdir -p shared_context docs/migration tests/migration tests/fixtures
Copy context sync template:

Bash

cp Implementation_v2/SHARED/00_CTX_SYNC_TEMPLATE.md shared_context/CTX_SYNC.md
Update shared_context/CTX_SYNC.md:

AG-00 status → 🔄 In Progress
current_task → "Phase 0: Migration Foundation"
1. backend/core/feature_flags.py
Goal: Feature flags for VoxRay v2.0 features.

We will NOT use generic ENABLE_V2_API / USE_ENSEMBLE_MODEL flags.
Instead, we use VoxRay-specific flags:

FF_ENSEMBLE_MODEL
FF_UNCERTAINTY_QUANTIFICATION
FF_DICOM_SUPPORT
FF_FHIR_INTEGRATION
FF_AUDIT_LOGGING
FF_DATA_ANONYMIZATION
FF_WAKE_WORD_DETECTION
FF_MULTILINGUAL_VOICE
FF_MEDICAL_VOCABULARY
FF_NOISE_HANDLING
FF_ADVANCED_HEATMAP
FF_WORKLIST_MANAGEMENT
FF_BATCH_PROCESSING
FF_MOBILE_PWA
File: backend/core/feature_flags.py

Python

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
2. backend/api/versioning.py
Goal: Attach API version headers and support /v1 + /v2 routes without changing current root behavior.

We will:

Add an APIVersionMiddleware that:
Adds deprecation headers for /v1/*
Adds version headers for /v2/*
Provide a setup_versioning(app) that:
Creates /v1/* aliases for existing v1 endpoints
Includes the /v2 router
File: backend/api/versioning.py

Python

import logging
from fastapi import FastAPI, APIRouter
from typing import Callable, Any

logger = logging.getLogger(__name__)


class APIVersionMiddleware:
    """
    Middleware to attach version headers and deprecation warnings.
    Does not change routing behavior, only headers.
    """

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")

        async def send_wrapper(message: dict):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])

                # Add version headers
                if path.startswith("/v1/"):
                    headers.append((b"x-api-version", b"1.0"))
                    headers.append((b"x-api-deprecation-date", b"2025-12-31"))
                    headers.append(
                        (
                            b"warning",
                            b"299 - 'V1 API is deprecated. Please migrate to /v2 endpoints.'",
                        )
                    )
                elif path.startswith("/v2/"):
                    headers.append((b"x-api-version", b"2.0"))
            await send(message)

        await self.app(scope, receive, send_wrapper)


def setup_versioning(app: FastAPI) -> None:
    """
    Configure versioned routing:

    - Root endpoints (/predict/image, /chat, etc.) remain V1 (backward compat).
    - /v1/* provides explicit stable aliases.
    - /v2/* hosts the new enhanced endpoints.

    This function MUST be called after all V1 endpoints are defined in main.py.
    """
    from backend.api import v2  # your v2 router module
    from backend.api.main import (
        predict_image,
        transcribe_audio,
        generate_speech,
        chat_endpoint,
        health,
    )

    # 1. /v1 aliases pointing to existing handlers (no logic duplication)
    v1_router = APIRouter(prefix="/v1", tags=["v1-stable"])
    v1_router.add_api_route("/predict/image", predict_image, methods=["POST"])
    v1_router.add_api_route("/transcribe/audio", transcribe_audio, methods=["POST"])
    v1_router.add_api_route("/generate/speech", generate_speech, methods=["POST"])
    v1_router.add_api_route("/chat", chat_endpoint, methods=["POST"])
    v1_router.add_api_route("/health", health, methods=["GET"])

    app.include_router(v1_router)

    # 2. /v2 enhanced router
    v2_router = APIRouter(prefix="/v2", tags=["v2"])
    v2_router.include_router(v2.router)
    app.include_router(v2_router)

    logger.info("✅ API versioning configured: /v1/*, /v2/*, and root-level V1 endpoints")
Integration in backend/api/main.py:

At the bottom of main.py (after all V1 endpoints are defined), add:

Python

from fastapi import FastAPI
from backend.api.versioning import APIVersionMiddleware, setup_versioning

# existing code...
app = FastAPI(title="VoxRay AI API")
# ... existing middlewares (CORS, etc.) ...

# Define all V1 endpoints here (predict_image, transcribe_audio, generate_speech, chat_endpoint, health, etc.)

# Attach API versioning
setup_versioning(app)

# Attach version middleware
app.add_middleware(APIVersionMiddleware)
3. tests/migration/test_backward_compatibility.py
Goal: Ensure existing V1 behavior remains unchanged.

We will:

Use TestClient on your backend/api/main.py (or main app import).
Test:
/health
/predict/image
/transcribe/audio
/chat
/v1/health
Ensure no v2 fields appear in v1 responses.
File: tests/migration/test_backward_compatibility.py

Python

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app  # adjust import if your main app entry is different

client = TestClient(app)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_XRAY = FIXTURES_DIR / "sample_xray.png"
SAMPLE_AUDIO = FIXTURES_DIR / "sample_audio.wav"

TEST_TOKEN = os.getenv("TEST_AUTH_TOKEN", "test_token_placeholder")


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_v1_predict_image_structure():
    """
    /predict/image MUST still return:
    {
        "diagnosis": str,
        "confidence": float in [0,1]
    }
    and MUST NOT contain v2 fields like 'uncertainty' or 'ensemble'.
    """
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        headers = {"x-stack-access-token": TEST_TOKEN}
        r = client.post("/predict/image", files=files, headers=headers)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()

    assert "diagnosis" in data
    assert "confidence" in data
    assert isinstance(data["diagnosis"], str)
    assert isinstance(data["confidence"], (int, float))
    assert 0.0 <= data["confidence"] <= 1.0

    # No v2 fields allowed in v1
    assert "uncertainty" not in data
    assert "ensemble" not in data
    assert "benchmark_comparison" not in data


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_v1_predict_image_alias_v1_prefix():
    """
    /v1/predict/image alias MUST behave identically to /predict/image.
    """
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        headers = {"x-stack-access-token": TEST_TOKEN}
        r = client.post("/v1/predict/image", files=files, headers=headers)

    assert r.status_code == 200
    data = r.json()
    assert "diagnosis" in data
    assert "confidence" in data


@pytest.mark.skipif(not SAMPLE_AUDIO.exists(), reason="sample_audio.wav missing")
def test_v1_transcribe_audio_structure():
    """
    /transcribe/audio MUST still return:
    {
        "transcription": str
    }
    """
    with SAMPLE_AUDIO.open("rb") as f:
        files = {"audio_file": ("test.wav", f, "audio/wav")}
        r = client.post("/transcribe/audio", files=files)

    assert r.status_code == 200
    data = r.json()
    assert "transcription" in data
    assert isinstance(data["transcription"], str)


def test_v1_chat_structure():
    """
    /chat MUST still return:
    {
        "response": str
    }
    """
    headers = {"x-stack-access-token": TEST_TOKEN}
    r = client.post(
        "/chat",
        json={"message": "Test", "context": "", "history": []},
        headers=headers,
    )

    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert isinstance(data["response"], str)


def test_v1_health_structure():
    """
    /health MUST still work and /v1/health alias MUST also work.
    """
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

    r_v1 = client.get("/v1/health")
    assert r_v1.status_code == 200
    data_v1 = r_v1.json()
    assert "status" in data_v1


def test_auth_required_for_protected_endpoints():
    """
    /predict/image and /chat MUST require auth token.
    """
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files)  # no header
    assert r.status_code in (401, 403)


def test_invalid_token_rejected():
    headers = {"x-stack-access-token": "invalid-token"}
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files, headers=headers)
    assert r.status_code in (401, 403)
Put sample fixtures here (non-PHI dummy files):

tests/fixtures/sample_xray.png
tests/fixtures/sample_audio.wav
4. docs/migration/rollback_procedures.md
Goal: Roll back VoxRay v2.0 features to a safe v1 baseline.

File: docs/migration/rollback_procedures.md

Markdown

# Migration Rollback Procedures (VoxRay AI v2.0)

**Severity:** CRITICAL
**Last Updated:** 2025-10-27

---

## Overview

This document describes how to quickly revert VoxRay AI from the v2.0 feature set
back to safe v1.0 behavior, or how to disable specific v2 features via feature flags.

Current architecture:

- Frontend: Netlify (`https://taupe-baklava-2d4afd.netlify.app`)
- Backend: Hugging Face Spaces (FastAPI on Uvicorn)
- Auth: Stack Auth (JWT → `x-stack-access-token`)

---

## Scenario A: Feature Malfunction (Non-Destructive)

**Examples:**
- Ensemble model is slow or returns odd results.
- DICOM endpoint unstable.
- Voice enhancements misbehaving.

**Action: Disable v2 features via Feature Flags**

1. Open the backend environment configuration (Hugging Face Space → Settings → Variables and secrets).
2. Find feature flag variables (examples):

   ```bash
   FF_ENSEMBLE_MODEL=true
   FF_UNCERTAINTY_QUANTIFICATION=true
   FF_DICOM_SUPPORT=true
   FF_MULTILINGUAL_VOICE=true
   # ...
Set critical flags to false:

Bash

FF_ENSEMBLE_MODEL=false
FF_UNCERTAINTY_QUANTIFICATION=false
FF_DICOM_SUPPORT=false
FF_FHIR_INTEGRATION=false
FF_WAKE_WORD_DETECTION=false
FF_MULTILINGUAL_VOICE=false
FF_MEDICAL_VOCABULARY=false
FF_NOISE_HANDLING=false
FF_ADVANCED_HEATMAP=false
FF_WORKLIST_MANAGEMENT=false
FF_BATCH_PROCESSING=false
FF_MOBILE_PWA=false
Restart the backend (Hugging Face will restart on config change).

Verify:

Bash

curl https://<your-hf-space-url>/health
pytest tests/migration/test_backward_compatibility.py -v
Expected: v1 behavior restored, no v2 features active.

Scenario B: Critical Backend Failure
Examples:

/predict/image returns 500 for all requests.
Backend does not start (crash loop).
Authentication route broken.
Step 1: Revert Code to Last Known Good Commit
If you keep your backend code in GitHub/GitLab:

Bash

git log --oneline  # find last stable commit
git checkout <stable-commit>
git push origin main
# Redeploy Space from stable commit
Step 2: Confirm Health
Bash

curl https://<your-hf-space-url>/health
pytest tests/migration/test_backward_compatibility.py -v
Scenario C: Frontend Regression (Netlify)
Examples:

After deploying a new frontend build, the app shows a white screen.
React error #426 visible in browser console.
Step 1: Roll Back Netlify Deploy
Go to Netlify dashboard → taupe-baklava-2d4afd.
Go to “Deploys”.
Select previous successful deploy (green check).
Click “Rollback to this deploy”.
Step 2: Clear Browser Cache
Ask users to:

Hard refresh: Ctrl+Shift+R (Windows/Linux), Cmd+Shift+R (macOS).
Post-Rollback Checklist
After any rollback:

 /predict/image returns 200 with {diagnosis, confidence}.
 /transcribe/audio returns 200 with {transcription}.
 /chat returns 200 with {response}.
 /health returns 200 and "status" appropriate.
 Protected endpoints return 401/403 without a valid token.
 Frontend at Netlify loads and can complete an X-ray analysis workflow without crashing.
 pytest tests/migration/test_backward_compatibility.py -v passes.
Recording the Incident
Create a new file under docs/incidents/ named YYYY-MM-DD-<short-name>.md.
Include:
Summary of the incident.
Timeline.
Root cause (if known).
Actions taken (rollback steps).
Preventive actions for future.
Owner: AG-00 (Migration Lead)
Co-Owners: AG-05 (DevOps), Human Coordinator

text


---

## 5. Quality Gate 0 Steps

To pass **Quality Gate 0**:

1. Ensure:

   - `backend/core/feature_flags.py` exists and imports correctly.
   - `backend/api/versioning.py` exists and `setup_versioning(app)` is called in `main.py`.
   - `tests/migration/test_backward_compatibility.py` passes.
   - `docs/migration/rollback_procedures.md` exists.

2. Run:

```bash
pytest tests/migration/test_feature_flags.py -v  # if you added that too
pytest tests/migration/test_backward_compatibility.py -v
Update shared_context/CTX_SYNC.md:
AG-00 status → ✅ Complete
Gate 0 status → ✅ Passed
````
