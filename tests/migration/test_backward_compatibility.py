import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Check for TensorFlow/numpy DLL issues - must actually USE TensorFlow to detect DLL problems
try:
    import numpy as np
    # Actually use numpy to detect DLL issues
    _test = np.array([1, 2, 3])
    # Try to import TensorFlow which triggers the DLL loading
    import tensorflow as tf
    # Actually use TensorFlow to ensure DLLs work
    _ = tf.constant([1, 2, 3])
    from backend.api.main import app
    HAS_DEPS = True
except (ImportError, OSError) as e:
    HAS_DEPS = False
    SKIP_REASON = f"Skipping due to TensorFlow/numpy DLL error: {e}"
    # Create a dummy app for collection
    from fastapi import FastAPI
    app = FastAPI()

client = TestClient(app) if HAS_DEPS else None

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_XRAY = FIXTURES_DIR / "sample_xray.png"
SAMPLE_AUDIO = FIXTURES_DIR / "sample_audio.wav"

TEST_TOKEN = os.getenv("TEST_AUTH_TOKEN", "test_token_placeholder")

from unittest.mock import MagicMock, patch
from backend.api.deps import get_current_user

# Skip all tests in this module if dependencies are missing
pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="TensorFlow/numpy DLL import issues")


@pytest.fixture
def mock_auth():
    """Mock authentication for successful tests"""
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user"}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def no_auth():
    """Ensure no auth override is active for failure tests"""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_model():
    """Mock ML model for successful tests"""
    mock_pred = MagicMock()
    # Mock return value: list of lists (batch size 1) with probabilities
    # Assuming 3 classes to match mocked class names
    mock_pred.predict.return_value = [[0.1, 0.8, 0.1]]

    # Patch the global variable in backend.api.main
    with (
        patch("backend.api.main.medical_model", mock_pred),
        patch("backend.api.main.MEDICAL_CLASS_NAMES", ["Normal", "Pneumonia", "Covid"]),
    ):
        yield mock_pred


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_v1_predict_image_structure(mock_auth, mock_model):
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
def test_v1_predict_image_alias_v1_prefix(mock_auth, mock_model):
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


def test_v1_chat_structure(mock_auth):
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


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_auth_required_for_protected_endpoints(no_auth):
    """
    /predict/image and /chat MUST require auth token.
    """
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files)  # no header
    assert r.status_code in (401, 403)


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_invalid_token_rejected(no_auth):
    headers = {"x-stack-access-token": "invalid-token"}
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files, headers=headers)
    assert r.status_code in (401, 403)
