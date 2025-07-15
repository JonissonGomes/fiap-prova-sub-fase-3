import os
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging

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
        # URL do endpoint de verificação do Keycloak
        introspect_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
        
        # Dados para a requisição
        data = {
            "token": token,
            "client_id": KEYCLOAK_CLIENT_ID
        }
        
        # Fazer a requisição para o Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(introspect_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Erro na verificação do token: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_info = response.json()
            
            if not token_info.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado ou inválido"
                )
            
            return token_info
            
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na verificação do token"
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
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging

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
        # URL do endpoint de verificação do Keycloak
        introspect_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
        
        # Dados para a requisição
        data = {
            "token": token,
            "client_id": KEYCLOAK_CLIENT_ID
        }
        
        # Fazer a requisição para o Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(introspect_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Erro na verificação do token: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_info = response.json()
            
            if not token_info.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado ou inválido"
                )
            
            return token_info
            
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na verificação do token"
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
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging

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
        # URL do endpoint de verificação do Keycloak
        introspect_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
        
        # Dados para a requisição
        data = {
            "token": token,
            "client_id": KEYCLOAK_CLIENT_ID
        }
        
        # Fazer a requisição para o Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(introspect_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Erro na verificação do token: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_info = response.json()
            
            if not token_info.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado ou inválido"
                )
            
            return token_info
            
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na verificação do token"
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
import jwt
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging

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
        # URL do endpoint de verificação do Keycloak
        introspect_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
        
        # Dados para a requisição
        data = {
            "token": token,
            "client_id": KEYCLOAK_CLIENT_ID
        }
        
        # Fazer a requisição para o Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(introspect_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Erro na verificação do token: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            token_info = response.json()
            
            if not token_info.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado ou inválido"
                )
            
            return token_info
            
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com Keycloak: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na verificação do token"
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