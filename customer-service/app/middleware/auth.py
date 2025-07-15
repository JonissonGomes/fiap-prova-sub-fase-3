from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import httpx
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Valida o token JWT e retorna os dados do usuário."""
    try:
        token = credentials.credentials
        
        # Valida o token com o serviço de autenticação
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            validation_response = response.json()
            
            # Verifica se o token é válido
            if not validation_response.get("valid", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Retorna os dados do usuário
            user_data = validation_response.get("user")
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Dados do usuário não encontrados",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_data
            
    except httpx.RequestError as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_roles: List[str]):
    """Decorator para verificar se o usuário tem uma das roles necessárias."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles necessárias: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Valida o token JWT opcionalmente (para endpoints que funcionam com ou sem autenticação)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import httpx
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Valida o token JWT e retorna os dados do usuário."""
    try:
        token = credentials.credentials
        
        # Valida o token com o serviço de autenticação
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            validation_response = response.json()
            
            # Verifica se o token é válido
            if not validation_response.get("valid", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Retorna os dados do usuário
            user_data = validation_response.get("user")
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Dados do usuário não encontrados",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_data
            
    except httpx.RequestError as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_roles: List[str]):
    """Decorator para verificar se o usuário tem uma das roles necessárias."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles necessárias: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Valida o token JWT opcionalmente (para endpoints que funcionam com ou sem autenticação)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import httpx
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Valida o token JWT e retorna os dados do usuário."""
    try:
        token = credentials.credentials
        
        # Valida o token com o serviço de autenticação
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            validation_response = response.json()
            
            # Verifica se o token é válido
            if not validation_response.get("valid", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Retorna os dados do usuário
            user_data = validation_response.get("user")
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Dados do usuário não encontrados",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_data
            
    except httpx.RequestError as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_roles: List[str]):
    """Decorator para verificar se o usuário tem uma das roles necessárias."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles necessárias: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Valida o token JWT opcionalmente (para endpoints que funcionam com ou sem autenticação)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import httpx
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Valida o token JWT e retorna os dados do usuário."""
    try:
        token = credentials.credentials
        
        # Valida o token com o serviço de autenticação
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            validation_response = response.json()
            
            # Verifica se o token é válido
            if not validation_response.get("valid", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Retorna os dados do usuário
            user_data = validation_response.get("user")
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Dados do usuário não encontrados",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_data
            
    except httpx.RequestError as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação indisponível"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na validação do token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_roles: List[str]):
    """Decorator para verificar se o usuário tem uma das roles necessárias."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles necessárias: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Valida o token JWT opcionalmente (para endpoints que funcionam com ou sem autenticação)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 