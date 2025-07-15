import asyncio
import time
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware para controle de rate limiting."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, Dict] = {}
        
        # Configurações do Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Configurações de rate limiting
        self.limits = {
            "auth": {"requests": 5, "window": 60},  # 5 requests por minuto para auth
            "general": {"requests": 100, "window": 60},  # 100 requests por minuto geral
            "list": {"requests": 30, "window": 60},  # 30 requests por minuto para listagem
            "health": {"requests": 200, "window": 60},  # 200 requests por minuto para health
            "admin": {"requests": 50, "window": 60},  # 50 requests por minuto para admin
        }
        
        # Inicializar Redis
        if self.redis_enabled:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Inicializa conexão com Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar com Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def _get_limit_key(self, endpoint: str) -> str:
        """Determina qual limite aplicar baseado no endpoint."""
        if "/auth/" in endpoint or "/login" in endpoint or "/register" in endpoint:
            return "auth"
        elif "/health" in endpoint:
            return "health"
        elif "/rate-limit/" in endpoint:
            return "admin"
        elif endpoint.endswith("/sales") and "GET" in endpoint:
            return "list"
        else:
            return "general"
    
    def _get_client_id(self, request: Request) -> str:
        """Obtém identificador único do cliente."""
        # Usar IP + hash do token se disponível
        client_ip = request.client.host if request.client else "unknown"
        
        # Tentar obter token do header Authorization
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Usar hash do token para não expor dados sensíveis
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            return f"{client_ip}:{token_hash}"
        
        return client_ip
    
    async def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando Redis."""
        try:
            current_time = int(time.time())
            
            # Usar sliding window log
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                return False, current_requests
            
            return True, current_requests
            
        except Exception as e:
            logger.error(f"Erro no Redis rate limiting: {e}")
            # Fallback para memória
            return await self._check_rate_limit_memory(key, limit, window)
    
    async def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando memória local."""
        current_time = time.time()
        
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "count": 0}
        
        # Limpar requests antigos
        store = self.memory_store[key]
        store["requests"] = [req_time for req_time in store["requests"] 
                           if current_time - req_time < window]
        
        current_requests = len(store["requests"])
        
        if current_requests >= limit:
            return False, current_requests
        
        # Adicionar request atual
        store["requests"].append(current_time)
        store["count"] = current_requests + 1
        
        return True, current_requests + 1
    
    async def __call__(self, request: Request, call_next):
        """Middleware principal."""
        # Determinar limite baseado no endpoint
        endpoint = str(request.url.path)
        method = request.method
        limit_key = self._get_limit_key(f"{method} {endpoint}")
        
        # Obter configuração do limite
        limit_config = self.limits.get(limit_key, self.limits["general"])
        limit = limit_config["requests"]
        window = limit_config["window"]
        
        # Obter ID do cliente
        client_id = self._get_client_id(request)
        rate_limit_key = f"rate_limit:{client_id}:{limit_key}"
        
        # Verificar rate limit
        if self.redis_client:
            allowed, current_requests = await self._check_rate_limit_redis(
                rate_limit_key, limit, window
            )
        else:
            allowed, current_requests = await self._check_rate_limit_memory(
                rate_limit_key, limit, window
            )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {limit} requests por {window} segundos excedido",
                    "retry_after": window
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                    "Retry-After": str(window)
                }
            )
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        remaining = max(0, limit - current_requests)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Retorna estatísticas do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "memory_store_size": len(cls.memory_store) if hasattr(cls, 'memory_store') else 0
        }
    
    @classmethod
    def get_config(cls) -> Dict:
        """Retorna configuração do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true"
        }
    
    @classmethod
    def reset_counters(cls):
        """Reseta contadores de rate limiting."""
        if hasattr(cls, 'memory_store'):
            cls.memory_store.clear()
        # Para Redis, os contadores expiram automaticamente

def setup_rate_limiting(app: FastAPI):
    """Configura o middleware de rate limiting."""
    middleware = RateLimitMiddleware(app)
    app.middleware("http")(middleware) 
import time
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware para controle de rate limiting."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, Dict] = {}
        
        # Configurações do Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Configurações de rate limiting
        self.limits = {
            "auth": {"requests": 5, "window": 60},  # 5 requests por minuto para auth
            "general": {"requests": 100, "window": 60},  # 100 requests por minuto geral
            "list": {"requests": 30, "window": 60},  # 30 requests por minuto para listagem
            "health": {"requests": 200, "window": 60},  # 200 requests por minuto para health
            "admin": {"requests": 50, "window": 60},  # 50 requests por minuto para admin
        }
        
        # Inicializar Redis
        if self.redis_enabled:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Inicializa conexão com Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar com Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def _get_limit_key(self, endpoint: str) -> str:
        """Determina qual limite aplicar baseado no endpoint."""
        if "/auth/" in endpoint or "/login" in endpoint or "/register" in endpoint:
            return "auth"
        elif "/health" in endpoint:
            return "health"
        elif "/rate-limit/" in endpoint:
            return "admin"
        elif endpoint.endswith("/sales") and "GET" in endpoint:
            return "list"
        else:
            return "general"
    
    def _get_client_id(self, request: Request) -> str:
        """Obtém identificador único do cliente."""
        # Usar IP + hash do token se disponível
        client_ip = request.client.host if request.client else "unknown"
        
        # Tentar obter token do header Authorization
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Usar hash do token para não expor dados sensíveis
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            return f"{client_ip}:{token_hash}"
        
        return client_ip
    
    async def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando Redis."""
        try:
            current_time = int(time.time())
            
            # Usar sliding window log
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                return False, current_requests
            
            return True, current_requests
            
        except Exception as e:
            logger.error(f"Erro no Redis rate limiting: {e}")
            # Fallback para memória
            return await self._check_rate_limit_memory(key, limit, window)
    
    async def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando memória local."""
        current_time = time.time()
        
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "count": 0}
        
        # Limpar requests antigos
        store = self.memory_store[key]
        store["requests"] = [req_time for req_time in store["requests"] 
                           if current_time - req_time < window]
        
        current_requests = len(store["requests"])
        
        if current_requests >= limit:
            return False, current_requests
        
        # Adicionar request atual
        store["requests"].append(current_time)
        store["count"] = current_requests + 1
        
        return True, current_requests + 1
    
    async def __call__(self, request: Request, call_next):
        """Middleware principal."""
        # Determinar limite baseado no endpoint
        endpoint = str(request.url.path)
        method = request.method
        limit_key = self._get_limit_key(f"{method} {endpoint}")
        
        # Obter configuração do limite
        limit_config = self.limits.get(limit_key, self.limits["general"])
        limit = limit_config["requests"]
        window = limit_config["window"]
        
        # Obter ID do cliente
        client_id = self._get_client_id(request)
        rate_limit_key = f"rate_limit:{client_id}:{limit_key}"
        
        # Verificar rate limit
        if self.redis_client:
            allowed, current_requests = await self._check_rate_limit_redis(
                rate_limit_key, limit, window
            )
        else:
            allowed, current_requests = await self._check_rate_limit_memory(
                rate_limit_key, limit, window
            )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {limit} requests por {window} segundos excedido",
                    "retry_after": window
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                    "Retry-After": str(window)
                }
            )
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        remaining = max(0, limit - current_requests)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Retorna estatísticas do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "memory_store_size": len(cls.memory_store) if hasattr(cls, 'memory_store') else 0
        }
    
    @classmethod
    def get_config(cls) -> Dict:
        """Retorna configuração do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true"
        }
    
    @classmethod
    def reset_counters(cls):
        """Reseta contadores de rate limiting."""
        if hasattr(cls, 'memory_store'):
            cls.memory_store.clear()
        # Para Redis, os contadores expiram automaticamente

def setup_rate_limiting(app: FastAPI):
    """Configura o middleware de rate limiting."""
    middleware = RateLimitMiddleware(app)
    app.middleware("http")(middleware) 
import time
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware para controle de rate limiting."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, Dict] = {}
        
        # Configurações do Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Configurações de rate limiting
        self.limits = {
            "auth": {"requests": 5, "window": 60},  # 5 requests por minuto para auth
            "general": {"requests": 100, "window": 60},  # 100 requests por minuto geral
            "list": {"requests": 30, "window": 60},  # 30 requests por minuto para listagem
            "health": {"requests": 200, "window": 60},  # 200 requests por minuto para health
            "admin": {"requests": 50, "window": 60},  # 50 requests por minuto para admin
        }
        
        # Inicializar Redis
        if self.redis_enabled:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Inicializa conexão com Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar com Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def _get_limit_key(self, endpoint: str) -> str:
        """Determina qual limite aplicar baseado no endpoint."""
        if "/auth/" in endpoint or "/login" in endpoint or "/register" in endpoint:
            return "auth"
        elif "/health" in endpoint:
            return "health"
        elif "/rate-limit/" in endpoint:
            return "admin"
        elif endpoint.endswith("/sales") and "GET" in endpoint:
            return "list"
        else:
            return "general"
    
    def _get_client_id(self, request: Request) -> str:
        """Obtém identificador único do cliente."""
        # Usar IP + hash do token se disponível
        client_ip = request.client.host if request.client else "unknown"
        
        # Tentar obter token do header Authorization
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Usar hash do token para não expor dados sensíveis
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            return f"{client_ip}:{token_hash}"
        
        return client_ip
    
    async def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando Redis."""
        try:
            current_time = int(time.time())
            
            # Usar sliding window log
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                return False, current_requests
            
            return True, current_requests
            
        except Exception as e:
            logger.error(f"Erro no Redis rate limiting: {e}")
            # Fallback para memória
            return await self._check_rate_limit_memory(key, limit, window)
    
    async def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando memória local."""
        current_time = time.time()
        
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "count": 0}
        
        # Limpar requests antigos
        store = self.memory_store[key]
        store["requests"] = [req_time for req_time in store["requests"] 
                           if current_time - req_time < window]
        
        current_requests = len(store["requests"])
        
        if current_requests >= limit:
            return False, current_requests
        
        # Adicionar request atual
        store["requests"].append(current_time)
        store["count"] = current_requests + 1
        
        return True, current_requests + 1
    
    async def __call__(self, request: Request, call_next):
        """Middleware principal."""
        # Determinar limite baseado no endpoint
        endpoint = str(request.url.path)
        method = request.method
        limit_key = self._get_limit_key(f"{method} {endpoint}")
        
        # Obter configuração do limite
        limit_config = self.limits.get(limit_key, self.limits["general"])
        limit = limit_config["requests"]
        window = limit_config["window"]
        
        # Obter ID do cliente
        client_id = self._get_client_id(request)
        rate_limit_key = f"rate_limit:{client_id}:{limit_key}"
        
        # Verificar rate limit
        if self.redis_client:
            allowed, current_requests = await self._check_rate_limit_redis(
                rate_limit_key, limit, window
            )
        else:
            allowed, current_requests = await self._check_rate_limit_memory(
                rate_limit_key, limit, window
            )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {limit} requests por {window} segundos excedido",
                    "retry_after": window
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                    "Retry-After": str(window)
                }
            )
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        remaining = max(0, limit - current_requests)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Retorna estatísticas do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "memory_store_size": len(cls.memory_store) if hasattr(cls, 'memory_store') else 0
        }
    
    @classmethod
    def get_config(cls) -> Dict:
        """Retorna configuração do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true"
        }
    
    @classmethod
    def reset_counters(cls):
        """Reseta contadores de rate limiting."""
        if hasattr(cls, 'memory_store'):
            cls.memory_store.clear()
        # Para Redis, os contadores expiram automaticamente

def setup_rate_limiting(app: FastAPI):
    """Configura o middleware de rate limiting."""
    middleware = RateLimitMiddleware(app)
    app.middleware("http")(middleware) 
import time
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware para controle de rate limiting."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, Dict] = {}
        
        # Configurações do Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Configurações de rate limiting
        self.limits = {
            "auth": {"requests": 5, "window": 60},  # 5 requests por minuto para auth
            "general": {"requests": 100, "window": 60},  # 100 requests por minuto geral
            "list": {"requests": 30, "window": 60},  # 30 requests por minuto para listagem
            "health": {"requests": 200, "window": 60},  # 200 requests por minuto para health
            "admin": {"requests": 50, "window": 60},  # 50 requests por minuto para admin
        }
        
        # Inicializar Redis
        if self.redis_enabled:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Inicializa conexão com Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao conectar com Redis: {e}. Usando fallback em memória.")
            self.redis_client = None
    
    def _get_limit_key(self, endpoint: str) -> str:
        """Determina qual limite aplicar baseado no endpoint."""
        if "/auth/" in endpoint or "/login" in endpoint or "/register" in endpoint:
            return "auth"
        elif "/health" in endpoint:
            return "health"
        elif "/rate-limit/" in endpoint:
            return "admin"
        elif endpoint.endswith("/sales") and "GET" in endpoint:
            return "list"
        else:
            return "general"
    
    def _get_client_id(self, request: Request) -> str:
        """Obtém identificador único do cliente."""
        # Usar IP + hash do token se disponível
        client_ip = request.client.host if request.client else "unknown"
        
        # Tentar obter token do header Authorization
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Usar hash do token para não expor dados sensíveis
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            return f"{client_ip}:{token_hash}"
        
        return client_ip
    
    async def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando Redis."""
        try:
            current_time = int(time.time())
            
            # Usar sliding window log
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                return False, current_requests
            
            return True, current_requests
            
        except Exception as e:
            logger.error(f"Erro no Redis rate limiting: {e}")
            # Fallback para memória
            return await self._check_rate_limit_memory(key, limit, window)
    
    async def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Verifica rate limit usando memória local."""
        current_time = time.time()
        
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "count": 0}
        
        # Limpar requests antigos
        store = self.memory_store[key]
        store["requests"] = [req_time for req_time in store["requests"] 
                           if current_time - req_time < window]
        
        current_requests = len(store["requests"])
        
        if current_requests >= limit:
            return False, current_requests
        
        # Adicionar request atual
        store["requests"].append(current_time)
        store["count"] = current_requests + 1
        
        return True, current_requests + 1
    
    async def __call__(self, request: Request, call_next):
        """Middleware principal."""
        # Determinar limite baseado no endpoint
        endpoint = str(request.url.path)
        method = request.method
        limit_key = self._get_limit_key(f"{method} {endpoint}")
        
        # Obter configuração do limite
        limit_config = self.limits.get(limit_key, self.limits["general"])
        limit = limit_config["requests"]
        window = limit_config["window"]
        
        # Obter ID do cliente
        client_id = self._get_client_id(request)
        rate_limit_key = f"rate_limit:{client_id}:{limit_key}"
        
        # Verificar rate limit
        if self.redis_client:
            allowed, current_requests = await self._check_rate_limit_redis(
                rate_limit_key, limit, window
            )
        else:
            allowed, current_requests = await self._check_rate_limit_memory(
                rate_limit_key, limit, window
            )
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {limit} requests por {window} segundos excedido",
                    "retry_after": window
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window),
                    "Retry-After": str(window)
                }
            )
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        remaining = max(0, limit - current_requests)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Retorna estatísticas do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "memory_store_size": len(cls.memory_store) if hasattr(cls, 'memory_store') else 0
        }
    
    @classmethod
    def get_config(cls) -> Dict:
        """Retorna configuração do rate limiting."""
        return {
            "limits": cls.limits if hasattr(cls, 'limits') else {},
            "redis_enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true"
        }
    
    @classmethod
    def reset_counters(cls):
        """Reseta contadores de rate limiting."""
        if hasattr(cls, 'memory_store'):
            cls.memory_store.clear()
        # Para Redis, os contadores expiram automaticamente

def setup_rate_limiting(app: FastAPI):
    """Configura o middleware de rate limiting."""
    middleware = RateLimitMiddleware(app)
    app.middleware("http")(middleware) 