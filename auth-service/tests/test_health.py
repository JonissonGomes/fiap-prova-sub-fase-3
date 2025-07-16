import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestHealth:
    def setup_method(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 