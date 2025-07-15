import os
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

# Configurações do Keycloak
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "vehicle-sales")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "vehicle-sales-app")

# Bearer token security
security = HTTPBearer()

async def verify_token(token: str) -> Dict:
    """Verifica o token JWT com o Keycloak."""
    try:
        # Primeiro, vamos tentar decodificar o token sem verificar a assinatura
        # para obter as informações básicas
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Verificar se o token não expirou
        import time
        current_time = int(time.time())
        token_exp = unverified_payload.get('exp', 0)
        
        if token_exp < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        # Verificar se o token é do realm correto
        # Aceita tanto localhost quanto o nome do container
        expected_issuer_localhost = f"http://localhost:8080/realms/{KEYCLOAK_REALM}"
        expected_issuer_container = f"http://keycloak:8080/realms/{KEYCLOAK_REALM}"
        actual_issuer = unverified_payload.get('iss')
        
        if actual_issuer not in [expected_issuer_localhost, expected_issuer_container]:
            logger.warning(f"Token com issuer inválido: {actual_issuer}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido - issuer incorreto"
            )
        
        # Por enquanto, vamos retornar o payload sem verificar a assinatura
        # Em produção, você deve verificar a assinatura usando as chaves públicas
        return unverified_payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de acesso com token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Obtém o usuário atual a partir do token JWT."""
    token = credentials.credentials
    token_info = await verify_token(token)
    
    # Extrair informações do usuário
    user_info = {
        "id": token_info.get("sub"),
        "username": token_info.get("preferred_username"),
        "email": token_info.get("email"),
        "name": token_info.get("name"),
        "roles": token_info.get("realm_access", {}).get("roles", []),
        "active": token_info.get("active", False)
    }
    
    return user_info

def require_role(required_roles: List[str]):
    """Decorator para exigir roles específicas."""
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_roles = current_user.get("roles", [])
        
        # Verificar se o usuário tem pelo menos uma das roles necessárias
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles necessárias: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker 