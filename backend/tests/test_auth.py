from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.deps import get_current_user

def test_public_endpoint_access(client):
    """Ensure health endpoint is public"""
    response = client.get("/health")
    assert response.status_code == 200

def test_protected_route_no_token(client):
    """Ensure protected routes reject requests without token"""
    # Assuming /predict/image is protected
    # sending empty files just to trigger auth check first
    response = client.post("/predict/image")
    assert response.status_code == 401
    assert "Missing authentication token" in response.json()["detail"]

def test_protected_route_valid_token():
    """Test access with valid mocked token"""
    # Mock the dependency
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test_user",
        "aud": "test_project"
    }
    
    with TestClient(app) as client:
        # We need to send a valid request structure even if auth passes
        # But for now, we just want to see if we bypass the 401
        # Sending no file might cause 422 validation error, which means auth passed
        response = client.post("/predict/image")
        
        # 422 means: Auth passed, but request body invalid (missing file)
        # 401 means: Auth failed
        assert response.status_code == 422 
    
    # Clean up
    app.dependency_overrides = {}
