import pytest
from fastapi.testclient import TestClient
from app.adapters.api.main import app

client = TestClient(app)

class TestHealth:
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "core-service" 