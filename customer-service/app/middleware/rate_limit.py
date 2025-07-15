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
        for pattern, limit_type in cls.ROUTE_LIMITS.items():
            if route.startswith(pattern):
                return cls.LIMITS[limit_type]
        
        # Retorna limite geral por padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Wrapper para Redis com fallback em memória"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

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

def setup_rate_limiting(app):
    """Configura rate limiting na aplicação FastAPI"""
    limiter = create_limiter()
    
    # Adiciona o limiter ao estado da aplicação
    app.state.limiter = limiter
    
    # Adiciona o middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Adiciona o handler de exceções
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator

def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Obtém informações da chave
        ttl = redis_client.ttl(key)
        current_count = redis_client.get(key)
        
        return {
            "key": key,
            "current_count": int(current_count) if current_count else 0,
            "ttl": ttl,
            "limit_active": ttl > 0
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limit: {e}")
        return {
            "key": key,
            "current_count": 0,
            "ttl": -1,
            "limit_active": False,
            "error": str(e)
        }

def reset_rate_limit(key: str) -> bool:
    """Reseta o contador de rate limit para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        result = redis_client.delete(key)
        logger.info(f"Rate limit resetado para chave: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Erro ao resetar rate limit: {e}")
        return False 
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
        for pattern, limit_type in cls.ROUTE_LIMITS.items():
            if route.startswith(pattern):
                return cls.LIMITS[limit_type]
        
        # Retorna limite geral por padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Wrapper para Redis com fallback em memória"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

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

def setup_rate_limiting(app):
    """Configura rate limiting na aplicação FastAPI"""
    limiter = create_limiter()
    
    # Adiciona o limiter ao estado da aplicação
    app.state.limiter = limiter
    
    # Adiciona o middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Adiciona o handler de exceções
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator

def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Obtém informações da chave
        ttl = redis_client.ttl(key)
        current_count = redis_client.get(key)
        
        return {
            "key": key,
            "current_count": int(current_count) if current_count else 0,
            "ttl": ttl,
            "limit_active": ttl > 0
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limit: {e}")
        return {
            "key": key,
            "current_count": 0,
            "ttl": -1,
            "limit_active": False,
            "error": str(e)
        }

def reset_rate_limit(key: str) -> bool:
    """Reseta o contador de rate limit para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        result = redis_client.delete(key)
        logger.info(f"Rate limit resetado para chave: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Erro ao resetar rate limit: {e}")
        return False 
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
        for pattern, limit_type in cls.ROUTE_LIMITS.items():
            if route.startswith(pattern):
                return cls.LIMITS[limit_type]
        
        # Retorna limite geral por padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Wrapper para Redis com fallback em memória"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

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

def setup_rate_limiting(app):
    """Configura rate limiting na aplicação FastAPI"""
    limiter = create_limiter()
    
    # Adiciona o limiter ao estado da aplicação
    app.state.limiter = limiter
    
    # Adiciona o middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Adiciona o handler de exceções
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator

def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Obtém informações da chave
        ttl = redis_client.ttl(key)
        current_count = redis_client.get(key)
        
        return {
            "key": key,
            "current_count": int(current_count) if current_count else 0,
            "ttl": ttl,
            "limit_active": ttl > 0
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limit: {e}")
        return {
            "key": key,
            "current_count": 0,
            "ttl": -1,
            "limit_active": False,
            "error": str(e)
        }

def reset_rate_limit(key: str) -> bool:
    """Reseta o contador de rate limit para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        result = redis_client.delete(key)
        logger.info(f"Rate limit resetado para chave: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Erro ao resetar rate limit: {e}")
        return False 
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
        for pattern, limit_type in cls.ROUTE_LIMITS.items():
            if route.startswith(pattern):
                return cls.LIMITS[limit_type]
        
        # Retorna limite geral por padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Wrapper para Redis com fallback em memória"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

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

def setup_rate_limiting(app):
    """Configura rate limiting na aplicação FastAPI"""
    limiter = create_limiter()
    
    # Adiciona o limiter ao estado da aplicação
    app.state.limiter = limiter
    
    # Adiciona o middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Adiciona o handler de exceções
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configurado com sucesso")

def rate_limit(limit: str):
    """Decorator para aplicar rate limiting a endpoints específicos"""
    def decorator(func):
        return func
    return decorator

def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Obtém informações da chave
        ttl = redis_client.ttl(key)
        current_count = redis_client.get(key)
        
        return {
            "key": key,
            "current_count": int(current_count) if current_count else 0,
            "ttl": ttl,
            "limit_active": ttl > 0
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limit: {e}")
        return {
            "key": key,
            "current_count": 0,
            "ttl": -1,
            "limit_active": False,
            "error": str(e)
        }

def reset_rate_limit(key: str) -> bool:
    """Reseta o contador de rate limit para uma chave"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        result = redis_client.delete(key)
        logger.info(f"Rate limit resetado para chave: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Erro ao resetar rate limit: {e}")
        return False 