import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/actuator/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_metrics_endpoint():
    # This endpoint is created by Prometheus Instrumentator
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# help" in response.text.lower()
