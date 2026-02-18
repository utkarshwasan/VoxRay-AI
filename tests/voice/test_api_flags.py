from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.feature_flags import FeatureFlag
from unittest.mock import patch

from unittest.mock import patch, AsyncMock

# Mock startup event to prevent model download
with patch("backend.api.main.load_models", new_callable=AsyncMock) as mock_load:
    client = TestClient(app)

ENHANCE_URL = "/v2/voice/enhance-transcription"
WAKE_WORD_URL = "/v2/voice/wake-word-detect"


def test_endpoints_disabled_by_default():
    """Ensure endpoints return 503 when flags are disabled (default)"""
    # Force flags disabled
    # Patch check_flag to always return False
    with patch("backend.core.feature_flags.check_flag", return_value=False):
        resp = client.post(ENHANCE_URL, json={"text": "ammonia"})
        assert resp.status_code == 503

        # For file upload
        resp = client.post(
            WAKE_WORD_URL, files={"file": ("audio.wav", b"dummy data", "audio/wav")}
        )
        assert resp.status_code == 503


def test_enhance_transcription_enabled():
    """Test enhancement endpoint functionality when enabled"""
    with patch("backend.core.feature_flags.check_flag") as mock_check:
        # Mock only specific flag to true
        def side_effect(flag):
            return flag == FeatureFlag.MEDICAL_VOCABULARY

        mock_check.side_effect = side_effect

        resp = client.post(ENHANCE_URL, json={"text": "patient has ammonia"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["enhanced"] == "patient has pneumonia"


def test_wake_word_enabled():
    """Test wake word detection endpoint when enabled"""
    with patch("backend.core.feature_flags.check_flag") as mock_check:

        def side_effect(flag):
            return flag == FeatureFlag.WAKE_WORD_DETECTION

        mock_check.side_effect = side_effect

        # Test file upload
        files = {"file": ("test.wav", b"zeros", "audio/wav")}
        resp = client.post(WAKE_WORD_URL, files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["supported"] is False
        assert "not implemented" in data["message"]
