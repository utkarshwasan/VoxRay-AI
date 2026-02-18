import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.api.main import app
from backend.core.feature_flags import FeatureFlag

client = TestClient(app)


@pytest.fixture
def mock_auth():
    from backend.api.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test_verification_user"
    }
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_model_v2():
    # Mock ModelServer.ensemble
    mock_ensemble = MagicMock()
    mock_ensemble.predict.return_value = {
        "mean_probability": [0.1, 0.8, 0.1],
        "variance": [0.01, 0.02, 0.01],
        "individual_predictions": [[0.1, 0.8, 0.1]],
        "model_count": 1,
    }

    with patch("backend.api.routes.v2_predict.model_server") as mock_server:
        mock_server.ensemble = mock_ensemble
        mock_server.predict.return_value = {
            "diagnosis": "06_PNEUMONIA",
            "confidence": 0.8,
            "probabilities": {"06_PNEUMONIA": 0.8},
            "ensemble": {
                "model_count": 1,
                "variance": [0.02],
                "individual_predictions": [[0.8]],
            },
        }
        yield mock_server


@pytest.fixture
def sample_image():
    # minimalist 1x1 png
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"


def test_v2_endpoint_disabled_by_default(mock_auth, sample_image):
    # Ensure flag is typically false or strictly mock it to false
    with patch(
        "backend.core.feature_flags.FeatureFlags.is_enabled", return_value=False
    ):
        files = {"file": ("test.png", sample_image, "image/png")}
        response = client.post("/v2/predict/image", files=files)
        assert response.status_code == 503
        assert response.json()["detail"]["error"] == "FEATURE_NOT_ENABLED"


def test_v2_endpoint_enabled_successfully(mock_auth, mock_model_v2, sample_image):
    # Mock flag to true
    with patch("backend.core.feature_flags.FeatureFlags.is_enabled", return_value=True):
        files = {"file": ("test.png", sample_image, "image/png")}
        response = client.post("/v2/predict/image", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "diagnosis" in data
        assert "ensemble" in data
        assert data["ensemble"]["model_count"] == 1
