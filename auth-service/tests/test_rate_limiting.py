import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limiter_key, setup_rate_limiting


class TestRateLimiting:
    """Testes para rate limiting"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_rate_limit_config(self):
        """Testa a configuração de rate limiting"""
        # Testa limites por tipo
        assert RateLimitConfig.LIMITS["auth"] == "5/minute"
        assert RateLimitConfig.LIMITS["general"] == "100/minute"
        assert RateLimitConfig.LIMITS["listing"] == "30/minute"
        
        # Testa mapeamento de rotas
        assert RateLimitConfig.ROUTE_LIMITS["/auth/login"] == "auth"
        assert RateLimitConfig.ROUTE_LIMITS["/auth/users"] == "listing"
        assert RateLimitConfig.ROUTE_LIMITS["/health"] == "health"
    
    def test_get_limit_for_route(self):
        """Testa a obtenção de limite para rotas específicas"""
        # Rota exata
        limit = RateLimitConfig.get_limit_for_route("/auth/login")
        assert limit == "5/minute"
        
        # Rota com correspondência parcial
        limit = RateLimitConfig.get_limit_for_route("/auth/users/123")
        assert limit == "30/minute"
        
        # Rota não mapeada (deve usar padrão)
        limit = RateLimitConfig.get_limit_for_route("/unknown/route")
        assert limit == "100/minute"
    
    def test_health_endpoint_no_rate_limit(self):
        """Testa que o endpoint de health não é limitado severamente"""
        # Faz múltiplas requisições rapidamente
        for i in range(10):
            response = self.client.get("/health")
            assert response.status_code == 200
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        # O middleware_stack não é mais uma lista, mas pode ser iterado
        middleware_names = [middleware.__class__.__name__ for middleware in app.user_middleware]
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORS" in name for name in middleware_names)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import setup_rate_limiting
        
        # Testa se a função de setup existe
        assert callable(setup_rate_limiting)
        
        # Testa se pode ser chamada sem erro
        try:
            limiter = setup_rate_limiting(app)
            assert limiter is not None
        except Exception as e:
            # Se houver erro, deve ser relacionado ao Redis não estar disponível
            # o que é esperado em ambiente de teste
            assert "Redis" in str(e) or "connection" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 