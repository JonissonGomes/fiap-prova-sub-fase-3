from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 
from typing import Optional, Dict, Any
import logging

from app.middleware.rate_limit import get_rate_limit_stats, reset_rate_limit, get_rate_limiter_key
from app.services.auth_service import AuthService
from app.controllers.auth_controller import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rate-limit",
    tags=["rate-limiting"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

@router.get(
    "/stats",
    summary="Obter estatísticas de rate limiting",
    description="Obtém estatísticas de rate limiting para monitoramento (apenas para administradores)."
)
async def get_rate_limit_statistics(
    ip: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém estatísticas de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Se IP não especificado, usa um padrão para buscar estatísticas gerais
        key = ip or "rate_limit:"
        stats = get_rate_limit_stats(key)
        
        return {
            "key": key,
            "statistics": stats,
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/reset",
    summary="Resetar rate limiting",
    description="Reseta os contadores de rate limiting para um IP específico (apenas para administradores)."
)
async def reset_rate_limiting(
    ip: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reseta rate limiting para um IP específico"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Reseta o rate limiting para o IP especificado
        key = f"rate_limit:{ip}"
        success = reset_rate_limit(key)
        
        if success:
            return {
                "message": f"Rate limiting resetado para o IP: {ip}",
                "success": True
            }
        else:
            return {
                "message": f"Nenhum rate limiting encontrado para o IP: {ip}",
                "success": False
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/config",
    summary="Obter configuração de rate limiting",
    description="Obtém a configuração atual de rate limiting (apenas para administradores)."
)
async def get_rate_limit_config(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém a configuração atual de rate limiting"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        from app.middleware.rate_limit import RateLimitConfig
        
        return {
            "limits": RateLimitConfig.LIMITS,
            "route_limits": RateLimitConfig.ROUTE_LIMITS,
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 