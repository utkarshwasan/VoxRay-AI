import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
import os

@pytest.fixture
def client():
    """synchronous client for basic API tests"""
    return TestClient(app)

@pytest.fixture
def valid_auth_headers():
    """Mock valid auth headers for testing"""
    # In integration tests we'd need a real token, but for unit tests
    # we might need to mock get_current_user dependency injection.
    # For now, we'll assume we mock the dependency in the test.
    return {"x-stack-access-token": "test_token"}

@pytest.fixture
def mock_user_payload():
    return {
        "sub": "user_test_123",
        "email": "test@example.com",
        "aud": os.environ.get("STACK_PROJECT_ID", "test_project")
    }
