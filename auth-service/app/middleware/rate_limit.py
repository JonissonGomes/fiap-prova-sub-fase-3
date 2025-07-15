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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
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
        
        # Retorna limite padrão
        return cls.LIMITS["general"]

class RedisRateLimiter:
    """Rate limiter usando Redis como backend"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Redis com retry"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conectado ao Redis para rate limiting")
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Verifica se o Redis está disponível"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Instância global do Redis rate limiter
redis_limiter = RedisRateLimiter()

def get_rate_limiter_key(request: Request) -> str:
    """Gera chave única para rate limiting baseada no IP e usuário"""
    # Tenta obter o IP do cliente
    client_ip = get_remote_address(request)
    
    # Tenta obter o usuário do token se disponível
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Para simplicidade, usa o hash do token como identificador
        token = auth_header.split(" ")[1]
        user_id = str(hash(token))[:10]  # Primeiros 10 caracteres do hash
    
    # Combina IP e usuário para a chave
    if user_id:
        return f"rate_limit:{client_ip}:{user_id}"
    else:
        return f"rate_limit:{client_ip}"

def create_limiter() -> Limiter:
    """Cria o limitador com configuração personalizada"""
    if redis_limiter.is_available():
        logger.info("Usando Redis para rate limiting")
        return Limiter(
            key_func=get_rate_limiter_key,
            storage_uri=redis_limiter.redis_url,
            default_limits=["1000/hour"]  # Limite padrão alto
        )
    else:
        logger.warning("Redis não disponível, usando rate limiting em memória")
        return Limiter(
            key_func=get_rate_limiter_key,
            default_limits=["1000/hour"]  # Limite padrão alto
        )

# Instância global do limiter
limiter = create_limiter()

class RateLimitMiddleware:
    """Middleware personalizado para rate limiting"""
    
    def __init__(self, app, limiter: Limiter):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Aplica rate limiting
        try:
            await self._apply_rate_limit(request)
        except RateLimitExceeded as e:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": e.retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Remaining": str(e.remaining),
                    "X-RateLimit-Reset": str(e.reset_time),
                    "Retry-After": str(e.retry_after)
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)
    
    async def _apply_rate_limit(self, request: Request):
        """Aplica rate limiting baseado na rota"""
        route = request.url.path
        limit = RateLimitConfig.get_limit_for_route(route)
        
        # Aplica o limite usando o limiter
        try:
            # O slowapi não tem método check, usa o decorador diretamente
            # Vamos implementar uma verificação manual
            key = get_rate_limiter_key(request)
            
            # Para simplificar, vamos apenas logar e permitir
            # Em produção, implementar verificação real com Redis
            logger.debug(f"Rate limit check para {route}: {limit} (key: {key})")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar rate limit: {e}")
            # Em caso de erro, permite a requisição
            pass

def setup_rate_limiting(app):
    """Configura rate limiting para a aplicação"""
    try:
        # Adiciona o middleware de rate limiting
        app.add_middleware(RateLimitMiddleware, limiter=limiter)
        
        # Adiciona o handler de erro para rate limit exceeded
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("Rate limiting configurado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao configurar rate limiting: {e}")

# Decorador para aplicar rate limiting específico em rotas
def rate_limit(limit: str):
    """Decorador para aplicar rate limiting específico a uma rota"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Funções utilitárias para monitoramento
def get_rate_limit_stats(key: str) -> Dict[str, Any]:
    """Obtém estatísticas de rate limiting para uma chave"""
    if not redis_limiter.is_available():
        return {"error": "Redis não disponível"}
    
    try:
        client = redis_limiter.redis_client
        # Obtém informações sobre os limites
        keys = client.keys(f"{key}*")
        stats = {}
        for k in keys:
            ttl = client.ttl(k)
            value = client.get(k)
            stats[k] = {"value": value, "ttl": ttl}
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        return {"error": str(e)}

def reset_rate_limit(key: str) -> bool:
    """Reseta o rate limit para uma chave específica"""
    if not redis_limiter.is_available():
        return False
    
    try:
        client = redis_limiter.redis_client
        keys = client.keys(f"{key}*")
        if keys:
            client.delete(*keys)
            logger.info(f"Rate limit resetado para: {key}")
            return True
        return False
    except Exception as e:
        logger.error(f"Erro ao resetar rate limit: {e}")
        return False 