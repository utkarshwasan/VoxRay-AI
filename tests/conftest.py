import pytest
from unittest.mock import MagicMock, patch
from backend.api.main import app
from backend.api.deps import get_current_user


# --- Mocks ---
@pytest.fixture
def mock_auth():
    """Mock authentication for successful tests"""
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user_123"}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_model():
    """Mock ML model to avoid loading real heavy model"""
    mock_pred = MagicMock()
    # Return [0.1, 0.8, 0.1] -> Max index 1 (Pneumonia in mocked list)
    mock_pred.predict.return_value = [[0.1, 0.8, 0.1]]

    with patch("backend.api.main.medical_model", mock_pred) as m_model:
        # Also patch class names in main module
        with patch(
            "backend.api.main.MEDICAL_CLASS_NAMES", ["Normal", "Pneumonia", "Other"]
        ):
            yield m_model
