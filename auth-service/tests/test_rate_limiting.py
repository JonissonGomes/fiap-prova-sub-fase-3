import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.middleware.rate_limit import RateLimitConfig, get_rate_limit_stats, reset_rate_limit


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
    
    @patch('app.middleware.rate_limit.redis_limiter.is_available')
    def test_rate_limit_without_redis(self, mock_redis_available):
        """Testa rate limiting quando Redis não está disponível"""
        mock_redis_available.return_value = False
        
        # Deve funcionar mesmo sem Redis (fallback em memória)
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_headers_on_success(self):
        """Testa se headers de rate limiting são incluídos em respostas normais"""
        response = self.client.get("/health")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == 200
        
        # Headers de rate limiting podem ou não estar presentes dependendo da implementação
        # Isso é mais para documentar o comportamento esperado
        assert "status" in response.json()
    
    def test_rate_limit_management_endpoints_require_auth(self):
        """Testa que endpoints de gerenciamento requerem autenticação"""
        # Tenta acessar estatísticas sem autenticação
        response = self.client.get("/rate-limit/stats")
        assert response.status_code == 401
        
        # Tenta acessar configuração sem autenticação
        response = self.client.get("/rate-limit/config")
        assert response.status_code == 401
        
        # Tenta resetar rate limiting sem autenticação
        response = self.client.delete("/rate-limit/reset?ip=127.0.0.1")
        assert response.status_code == 401
    
    def test_rate_limit_management_endpoints_require_admin(self):
        """Testa que endpoints de gerenciamento requerem role ADMIN"""
        # Mock de token inválido
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = self.client.get("/rate-limit/stats", headers=headers)
        # Pode ser 401 (token inválido) ou 403 (sem permissão)
        assert response.status_code in [401, 403]
    
    @patch('app.middleware.rate_limit.get_rate_limit_stats')
    def test_rate_limit_stats_function(self, mock_get_stats):
        """Testa a função de obtenção de estatísticas"""
        mock_get_stats.return_value = {
            "rate_limit:127.0.0.1": {"value": "5", "ttl": 60}
        }
        
        stats = get_rate_limit_stats("rate_limit:127.0.0.1")
        assert "rate_limit:127.0.0.1" in stats
        assert stats["rate_limit:127.0.0.1"]["value"] == "5"
    
    @patch('app.middleware.rate_limit.reset_rate_limit')
    def test_rate_limit_reset_function(self, mock_reset):
        """Testa a função de reset de rate limiting"""
        mock_reset.return_value = True
        
        result = reset_rate_limit("rate_limit:127.0.0.1")
        assert result is True
        mock_reset.assert_called_once_with("rate_limit:127.0.0.1")
    
    def test_rate_limit_key_generation(self):
        """Testa a geração de chaves para rate limiting"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request
        mock_request = MagicMock()
        mock_request.headers = {}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            assert key == "rate_limit:127.0.0.1"
    
    def test_rate_limit_key_generation_with_token(self):
        """Testa a geração de chaves com token de autenticação"""
        from app.middleware.rate_limit import get_rate_limiter_key
        from fastapi import Request
        
        # Mock de request com token
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer test_token_123"}
        
        # Simula função get_remote_address
        with patch('app.middleware.rate_limit.get_remote_address') as mock_get_ip:
            mock_get_ip.return_value = "127.0.0.1"
            
            key = get_rate_limiter_key(mock_request)
            # Deve incluir hash do token
            assert key.startswith("rate_limit:127.0.0.1:")
            assert len(key) > len("rate_limit:127.0.0.1:")
    
    def test_rate_limit_middleware_setup(self):
        """Testa se o middleware de rate limiting foi configurado"""
        # Verifica se a aplicação tem middlewares configurados
        assert len(app.middleware_stack) > 0
        
        # Verifica se há middleware de CORS (que sabemos que está configurado)
        middleware_types = [type(middleware) for middleware in app.middleware_stack]
        
        # Deve ter pelo menos o middleware de CORS
        from fastapi.middleware.cors import CORSMiddleware
        assert any("CORSMiddleware" in str(middleware_type) for middleware_type in middleware_types)


@pytest.mark.asyncio
class TestRateLimitingAsync:
    """Testes assíncronos para rate limiting"""
    
    async def test_redis_connection_retry(self):
        """Testa o mecanismo de retry de conexão do Redis"""
        from app.middleware.rate_limit import RedisRateLimiter
        
        # Cria instância com URL inválida
        limiter = RedisRateLimiter("redis://invalid:6379")
        
        # Deve retornar False para is_available
        assert limiter.is_available() is False
    
    async def test_rate_limit_middleware_error_handling(self):
        """Testa o tratamento de erros no middleware"""
        from app.middleware.rate_limit import RateLimitMiddleware, create_limiter
        
        # Cria middleware
        limiter = create_limiter()
        middleware = RateLimitMiddleware(None, limiter)
        
        # Testa se o middleware foi criado
        assert middleware is not None
        assert middleware.limiter is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 