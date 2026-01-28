import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_root_redirect(client):
    # Depending on config, root might 404 or redirect. 
    # Current main.py doesn't show a root handler, so 404 is expected unless static files are mounted at root.
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_metrics_endpoint_not_exposed_publicly(client):
    # Ensure no unintended metrics exposure
    response = client.get("/metrics")
    assert response.status_code == 404
