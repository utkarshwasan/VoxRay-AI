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


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_auth_required_for_protected_endpoints():
    """
    /predict/image and /chat MUST require auth token.
    """
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files)  # no header
    assert r.status_code in (401, 403)


@pytest.mark.skipif(not SAMPLE_XRAY.exists(), reason="sample_xray.png missing")
def test_invalid_token_rejected():
    headers = {"x-stack-access-token": "invalid-token"}
    with SAMPLE_XRAY.open("rb") as f:
        files = {"image_file": ("test.png", f, "image/png")}
        r = client.post("/predict/image", files=files, headers=headers)
    assert r.status_code in (401, 403)
