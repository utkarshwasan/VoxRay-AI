import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import os


# Mock the entire load_models function to prevent startup download
@pytest.fixture(autouse=True)
def mock_startup_models():
    """Prevent heavy ML models from loading during tests"""
    with patch("backend.api.main.load_models") as mock_load:
        # Also mock the global variables in main so endpoints don't crash
        with (
            patch("backend.api.main.medical_model", MagicMock()),
            patch("backend.api.main.stt_model", MagicMock()),
            patch("backend.api.main.stt_processor", MagicMock()),
        ):
            yield mock_load


@pytest.fixture
def client(mock_startup_models):
    """synchronous client for basic API tests"""
    from backend.api.main import app

    return TestClient(app)


@pytest.fixture
def valid_auth_headers():
    """Mock valid auth headers for testing"""
    return {"x-stack-access-token": "test_token"}


@pytest.fixture
def mock_user_payload():
    return {
        "sub": "user_test_123",
        "email": "test@example.com",
        "aud": os.environ.get("STACK_PROJECT_ID", "test_project"),
    }
