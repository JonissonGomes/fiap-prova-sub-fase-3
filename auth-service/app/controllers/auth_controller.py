from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional, List
import logging

from app.domain.user import UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse, TokenValidationRequest, TokenValidationResponse, RefreshTokenRequest
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["autenticação"],
    responses={
        404: {"description": "Recurso não encontrado"},
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado"}
    }
)

# Dependency para obter o serviço de autenticação
async def get_auth_service() -> AuthService:
    # Esta função será implementada no main.py
    pass

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuário",
    description="Registra um novo usuário no sistema. O usuário será criado tanto no Keycloak quanto no MongoDB."
)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Registra um novo usuário"""
    try:
        return await auth_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Fazer login",
    description="Autentica um usuário e retorna tokens de acesso e renovação."
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Autentica um usuário"""
    try:
        return await auth_service.authenticate_user(login_data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao fazer login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Validar token",
    description="Valida um token de acesso e retorna informações do usuário se válido."
)
async def validate_token_post(
    token_data: TokenValidationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Valida um token de acesso"""
    try:
        return await auth_service.validate_token(token_data.token)
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Validar token",
    description="Valida um token de acesso e retorna informações do usuário se válido."
)
async def validate_token_get(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Valida um token de acesso via header Authorization"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        return await auth_service.validate_token(token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Renovar token",
    description="Renova um token de acesso usando o token de renovação."
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Renova um token de acesso"""
    try:
        return await auth_service.refresh_token(refresh_data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/logout",
    summary="Fazer logout",
    description="Faz logout de um usuário invalidando o token de renovação."
)
async def logout(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Faz logout de um usuário"""
    try:
        success = await auth_service.logout_user(refresh_token)
        if success:
            return {"message": "Logout realizado com sucesso"}
        else:
            raise HTTPException(status_code=400, detail="Erro ao fazer logout")
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Obter perfil",
    description="Obtém o perfil do usuário autenticado."
)
async def get_profile(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém o perfil do usuário autenticado"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        user = await auth_service.get_user_profile(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Atualizar perfil",
    description="Atualiza o perfil do usuário autenticado."
)
async def update_profile(
    user_data: UserUpdate,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Atualiza o perfil do usuário autenticado"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Usuário só pode atualizar seu próprio perfil
        updated_user = await auth_service.update_user(validation.user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Listar usuários",
    description="Lista todos os usuários do sistema (apenas para administradores)."
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Lista usuários (apenas para administradores)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        return await auth_service.list_users(skip, limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Obtém dados de um usuário específico pelo ID."
)
async def get_user(
    user_id: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtém um usuário pelo ID"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Usuário pode ver apenas seus próprios dados ou admin pode ver todos
        if validation.user.id != user_id and validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuário",
    description="Atualiza dados de um usuário específico."
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Atualiza dados de um usuário"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Usuário pode atualizar apenas seus próprios dados ou admin pode atualizar todos
        if validation.user.id != user_id and validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        return await auth_service.update_user(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar usuário",
    description="Remove um usuário do sistema (apenas para administradores)."
)
async def delete_user(
    user_id: str,
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Remove um usuário do sistema"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de acesso necessário")
        
        token = authorization.split(" ")[1]
        validation = await auth_service.validate_token(token)
        
        if not validation.valid:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        if validation.user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        success = await auth_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/health",
    summary="Verificar saúde",
    description="Endpoint para verificar se o serviço de autenticação está funcionando."
)
async def health_check():
    """Verifica a saúde do serviço"""
    return {"status": "healthy", "service": "auth-service"} 
