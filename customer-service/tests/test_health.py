import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestHealth:
    """Testes básicos de saúde para o Customer Service"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "customer-service"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 