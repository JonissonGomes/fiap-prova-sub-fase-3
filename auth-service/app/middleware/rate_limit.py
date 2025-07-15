import time
import logging
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import os

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuração de rate limiting por tipo de endpoint"""
    
    # Limites por tipo de endpoint (requests per minute)
    LIMITS = {
        "auth": "5/minute",           # Endpoints de autenticação
        "general": "100/minute",      # Endpoints gerais
        "listing": "30/minute",       # Endpoints de listagem
        "health": "200/minute",       # Health checks
        "admin": "50/minute",         # Endpoints administrativos
    }
    
    # Mapeamento de rotas para tipos de limite
    ROUTE_LIMITS = {
        "/auth/login": "auth",
        "/auth/register": "auth",
        "/auth/refresh": "auth",
        "/auth/logout": "auth",
        "/auth/validate": "general",
        "/auth/profile": "general",
        "/auth/users": "listing",
        "/vehicles": "listing",
        "/sales": "listing",
        "/customers": "listing",
        "/health": "health",
    }
    
    @classmethod
    def get_limit_for_route(cls, route: str) -> str:
        """Obtém o limite para uma rota específica"""
        # Verifica correspondência exata primeiro
        if route in cls.ROUTE_LIMITS:
            limit_type = cls.ROUTE_LIMITS[route]
            return cls.LIMITS[limit_type]
        
        # Verifica correspondência parcial para rotas dinâmicas
        for route_pattern, limit_type in cls.ROUTE_LIMITS.items():
            if route.startswith(route_pattern):
                return cls.LIMITS[limit_type]
        
        # Padrão se não encontrar correspondência
        return cls.LIMITS["general"]

# Configuração do Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_db = int(os.getenv("REDIS_DB", "0"))

# Inicialização do Redis (com fallback)
try:
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
    redis_client.ping()
    logger.info(f"Conectado ao Redis em {redis_host}:{redis_port}")
except Exception as e:
    logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
    redis_client = None

# Fallback em memória se Redis não estiver disponível
memory_cache = {}

# Configuração do Limiter
def get_rate_limiter_key(request: Request):
    """Gera chave única para rate limiting baseada no IP do cliente"""
    client_ip = get_remote_address(request)
    return f"rate_limit:{client_ip}"

def get_rate_limit_key(request: Request):
    """Alias para compatibilidade"""
    return get_rate_limiter_key(request)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler personalizado para quando o rate limit é excedido"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Muitas requisições. Tente novamente em alguns minutos.",
            "retry_after": str(exc.retry_after)
        }
    )

def setup_rate_limiting(app):
    """Configura o middleware de rate limiting na aplicação"""
    limiter = Limiter(key_func=get_rate_limiter_key)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    logger.info("Rate limiting configurado com sucesso")
    return limiter

def apply_rate_limit(request: Request, response: Response):
    """Aplica rate limiting a uma requisição"""
    try:
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o rate limit baseado na rota
        key = get_rate_limiter_key(request)
        
        if redis_client:
            # Usa Redis para controle distribuído
            current_count = redis_client.incr(key)
            if current_count == 1:
                # Primeira requisição, define TTL
                redis_client.expire(key, 60)  # 1 minuto
            
            # Verifica se excedeu o limite
            limit_number = int(limit.split("/")[0])
            if current_count > limit_number:
                raise RateLimitExceeded(detail=f"Rate limit exceeded for {route}")
        else:
            # Fallback em memória
            current_time = time.time()
            if key not in memory_cache:
                memory_cache[key] = []
            
            # Remove entradas antigas (mais de 1 minuto)
            memory_cache[key] = [t for t in memory_cache[key] if current_time - t < 60]
            
            # Adiciona requisição atual
            memory_cache[key].append(current_time)
            
            # Verifica limite
            limit_number = int(limit.split("/")[0])
            if len(memory_cache[key]) > limit_number:
                raise RateLimitExceeded(detail=f"Rate limit exceeded for {route}")
        
        # Adiciona headers informativos
        response.headers["X-RateLimit-Limit"] = str(limit_number)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit_number - (current_count if redis_client else len(memory_cache[key]))))
        
    except RateLimitExceeded:
        raise
    except Exception as e:
        logger.error(f"Erro ao aplicar rate limiting: {e}")
        # Em caso de erro, não bloqueia a requisição

def with_rate_limit(limit: str = None):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Esta função seria implementada com base no contexto da requisição
            # Por enquanto, apenas retorna a função original
            return func(*args, **kwargs)
        return wrapper
    return decorator 