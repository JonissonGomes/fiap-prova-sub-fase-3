from typing import Optional, Dict, Any, List
from datetime import datetime
from passlib.context import CryptContext
import logging

from app.domain.user import User, UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse, TokenValidationResponse
from app.adapters.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.keycloak_config import KeycloakConfig

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repository: MongoDBUserRepository, keycloak_config: KeycloakConfig):
        self.user_repository = user_repository
        self.keycloak_config = keycloak_config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Registra um novo usuário no sistema"""
        try:
            # Verificar se o email já existe
            if await self.user_repository.email_exists(user_data.email):
                raise ValueError("Email já está em uso")
            
            # Criar usuário no Keycloak
            keycloak_id = await self.keycloak_config.create_user(
                email=user_data.email,
                password=user_data.password,
                name=user_data.name,
                role=user_data.role
            )
            
            # Criar hash da senha para armazenar localmente
            password_hash = self.pwd_context.hash(user_data.password)
            
            # Criar usuário no MongoDB
            user = User(
                email=user_data.email,
                name=user_data.name,
                role=user_data.role,
                status=user_data.status,
                password_hash=password_hash,
                keycloak_id=keycloak_id
            )
            
            created_user = await self.user_repository.create_user(user)
            logger.info(f"Usuário {user_data.email} registrado com sucesso")
            
            return created_user.to_response()
            
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {e}")
            raise
    
    async def authenticate_user(self, login_data: LoginRequest) -> LoginResponse:
        """Autentica um usuário e retorna tokens"""
        try:
            # Buscar usuário no MongoDB
            user = await self.user_repository.get_user_by_email(login_data.email)
            if not user:
                raise ValueError("Credenciais inválidas")
            
            # Verificar se o usuário está ativo
            if user.status != "ACTIVE":
                raise ValueError("Usuário inativo ou bloqueado")
            
            # Autenticar no Keycloak
            token_data = await self.keycloak_config.authenticate_user(
                login_data.email, 
                login_data.password
            )
            
            if not token_data:
                raise ValueError("Credenciais inválidas")
            
            # Atualizar último login
            await self.user_repository.update_last_login(user.id)
            
            # Retornar resposta com tokens
            return LoginResponse(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_type="bearer",
                expires_in=token_data['expires_in'],
                user=user.to_response()
            )
            
        except Exception as e:
            logger.error(f"Erro ao autenticar usuário: {e}")
            raise
    
    async def validate_token(self, token: str) -> TokenValidationResponse:
        """Valida um token de acesso"""
        try:
            # Validar token no Keycloak
            token_info = await self.keycloak_config.validate_token(token)
            
            if not token_info:
                return TokenValidationResponse(valid=False)
            
            # Buscar usuário pelo email do token
            email = token_info.get('email')
            if not email:
                return TokenValidationResponse(valid=False)
            
            user = await self.user_repository.get_user_by_email(email)
            if not user:
                return TokenValidationResponse(valid=False)
            
            # Verificar se o usuário ainda está ativo
            if user.status != "ACTIVE":
                return TokenValidationResponse(valid=False)
            
            expires_at = datetime.fromtimestamp(token_info.get('exp', 0))
            
            return TokenValidationResponse(
                valid=True,
                user=user.to_response(),
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"Erro ao validar token: {e}")
            return TokenValidationResponse(valid=False)
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Renova um token de acesso"""
        try:
            return await self.keycloak_config.refresh_token(refresh_token)
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return None
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Faz logout de um usuário"""
        try:
            return await self.keycloak_config.logout_user(refresh_token)
        except Exception as e:
            logger.error(f"Erro ao fazer logout: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserResponse]:
        """Obtém o perfil de um usuário"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if user:
                return user.to_response()
            return None
        except Exception as e:
            logger.error(f"Erro ao obter perfil do usuário: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Obtém um usuário pelo ID"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if user:
                return user.to_response()
            return None
        except Exception as e:
            logger.error(f"Erro ao obter usuário por ID: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """Atualiza o perfil de um usuário"""
        try:
            # Buscar usuário atual
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return None
            
            # Atualizar apenas os campos fornecidos
            update_data = user_update.dict(exclude_unset=True)
            if not update_data:
                return user.to_response()
            
            # Aplicar as atualizações
            for field, value in update_data.items():
                setattr(user, field, value)
            
            # Atualizar no banco
            updated_user = await self.user_repository.update_user(user)
            return updated_user.to_response()
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil do usuário: {e}")
            return None
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Altera a senha de um usuário"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return False
            
            # Verificar senha atual
            if not self.pwd_context.verify(old_password, user.password_hash):
                return False
            
            # Atualizar senha no Keycloak
            if user.keycloak_id:
                await self.keycloak_config.update_user_password(user.keycloak_id, new_password)
            
            # Atualizar senha no MongoDB
            new_password_hash = self.pwd_context.hash(new_password)
            await self.user_repository.update_password(user_id, new_password_hash)
            
            logger.info(f"Senha alterada para usuário {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            return False
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Lista usuários (função administrativa)"""
        try:
            users = await self.user_repository.list_users(skip, limit)
            return [user.to_response() for user in users]
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []
    
    async def delete_user(self, user_id: str) -> bool:
        """Deleta um usuário (função administrativa)"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return False
            
            # Deletar do Keycloak
            if user.keycloak_id:
                await self.keycloak_config.delete_user(user.keycloak_id)
            
            # Deletar do MongoDB
            await self.user_repository.delete_user(user_id)
            
            logger.info(f"Usuário {user.email} deletado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar usuário: {e}")
            return False 