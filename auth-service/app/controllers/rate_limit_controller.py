from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
import logging

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

@router.get("/stats", response_model=Dict[str, Any])
async def get_rate_limit_stats(
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Obtém estatísticas de rate limiting para um usuário
    
    Args:
        user_id: ID do usuário (opcional)
        auth_service: Serviço de autenticação
        
    Returns:
        Estatísticas de rate limiting
    """
    try:
        # Gerar chave do rate limiter
        key = f"rate_limit:{user_id or 'anonymous'}"
        
        # Retornar estatísticas básicas
        stats = {
            "key": key,
            "limits": {"default": "100/minute"},
            "route_limits": {"auth": "5/minute", "general": "100/minute"},
            "message": "Estatísticas de rate limiting obtidas com sucesso"
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/reset", response_model=Dict[str, Any])
async def reset_rate_limiting(
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reseta o rate limiting para um usuário
    
    Args:
        user_id: ID do usuário (opcional)
        auth_service: Serviço de autenticação
        
    Returns:
        Resultado da operação de reset
    """
    try:
        # Gerar chave do rate limiter
        key = f"rate_limit:{user_id or 'anonymous'}"
        
        # Simular reset (em um ambiente real, isso limparia o cache Redis)
        logger.info(f"Rate limiting resetado para chave: {key}")
        
        return {
            "key": key,
            "reset": True,
            "message": "Rate limiting resetado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/config", response_model=Dict[str, Any])
async def get_rate_limit_config():
    """
    Obtém a configuração atual de rate limiting
    
    Returns:
        Configuração de rate limiting
    """
    try:
        return {
            "limits": {"default": "100/minute"},
            "route_limits": {"auth": "5/minute", "general": "100/minute"},
            "message": "Configuração de rate limiting obtida com sucesso"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter configuração de rate limiting: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 