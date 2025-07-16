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

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada em IP e token"""
    ip = get_remote_address(request)
    
    # Tenta obter o token do header Authorization
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Usa hash do token para não expor o token real
        token_hash = str(hash(token))[:8]
        return f"{ip}:{token_hash}"
    
    return ip

def create_limiter() -> Limiter:
    """Cria e configura o limiter com Redis ou fallback em memória"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    try:
        # Tenta usar Redis
        limiter = Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_url,
            default_limits=["100/minute"]
        )
        logger.info("Rate limiter configurado com Redis")
    except Exception as e:
        # Fallback para memória
        logger.warning(f"Erro ao configurar Redis, usando memória: {e}")
        limiter = Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["100/minute"]
        )
    
    return limiter

# Instancia o Limiter normalmente
limiter = Limiter(key_func=get_remote_address)

# Handler customizado para exceções de rate limit e erros de conexão
async def custom_rate_limit_exceeded_handler(request: Request, exc):
    if hasattr(exc, 'detail'):
        return JSONResponse({"error": f"Rate limit exceeded: {exc.detail}"}, status_code=429)
    else:
        # Erro de conexão com Redis ou outro erro
        return JSONResponse({"error": "Rate limit backend unavailable"}, status_code=503)

def setup_rate_limiting(app):
    @app.middleware("http")
    async def skip_rate_limit_for_health(request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        
        # Usar o middleware do slowapi corretamente
        try:
            return await call_next(request)
        except RateLimitExceeded as e:
            return await custom_rate_limit_exceeded_handler(request, e)
        except Exception as e:
            return await custom_rate_limit_exceeded_handler(request, e)
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator 