import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.deps import get_current_user

@pytest.fixture
def mock_auth():
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user"}
    yield
    app.dependency_overrides = {}

@patch("backend.api.main.OpenAI")
def test_chat_endpoint_success(mock_openai_class, mock_auth, client):
    # Mock the client instance and its method chain
    mock_instance = mock_openai_class.return_value
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "This is a mocked response from Gemini."
    mock_instance.chat.completions.create.return_value = mock_completion

    payload = {
        "message": "What does this X-ray show?",
        "context": "Diagnosis: PNEUMONIA (85%)",
        "history": []
    }
    
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "This is a mocked response from Gemini."
    
    # Verify OpenAI was initialized (checking if api_key was passed is good practice)
    # But since api_key comes from env, we might need to mock env if not set.
    # The endpoint checks expected env var. In test env it might differ.
    
def test_chat_missing_api_key(client, monkeypatch):
    """Test 500 if API key is missing (simulated by empty env)"""
    # Force override get_current_user to bypass auth
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user"}
    
    # Remove API key from env
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    
    payload = {"message": "Hello"}
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 500
    assert "OpenRouter API Key not found" in response.json()["detail"]
    
    app.dependency_overrides = {}
