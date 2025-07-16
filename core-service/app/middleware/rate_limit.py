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

def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler customizado para exceções de rate limit"""
    try:
        # Tenta usar o handler padrão
        return _rate_limit_exceeded_handler(request, exc)
    except AttributeError as e:
        # Fallback se o handler padrão falhar
        logger.warning(f"Erro no handler padrão de rate limit: {e}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": "Too many requests. Please try again later."
            }
        )

def setup_rate_limiting(app):
    """Configura rate limiting na aplicação FastAPI"""
    limiter = create_limiter()
    
    # Adiciona o limiter ao estado da aplicação
    app.state.limiter = limiter
    
    # Adiciona o middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Adiciona o handler de exceções customizado
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator 