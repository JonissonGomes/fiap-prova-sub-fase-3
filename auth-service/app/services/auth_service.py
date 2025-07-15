from typing import Optional, Dict, Any
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
    
    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """Renova um token de acesso"""
        try:
            # Renovar token no Keycloak
            token_data = await self.keycloak_config.refresh_token(refresh_token)
            
            if not token_data:
                raise ValueError("Token de renovação inválido")
            
            # Validar o novo token para obter dados do usuário
            validation = await self.validate_token(token_data['access_token'])
            
            if not validation.valid:
                raise ValueError("Token renovado inválido")
            
            return LoginResponse(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_type="bearer",
                expires_in=token_data['expires_in'],
                user=validation.user
            )
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Faz logout de um usuário"""
        try:
            return await self.keycloak_config.logout_user(refresh_token)
        except Exception as e:
            logger.error(f"Erro ao fazer logout: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Busca um usuário pelo ID"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            return user.to_response() if user else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Busca um usuário pelo email"""
        try:
            user = await self.user_repository.get_user_by_email(email)
            return user.to_response() if user else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Atualiza dados de um usuário"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Atualizar campos fornecidos
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            updated_user = await self.user_repository.update_user(user)
            return updated_user.to_response()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Remove um usuário do sistema"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return False
            
            # Remover do MongoDB
            success = await self.user_repository.delete_user(user_id)
            
            # TODO: Remover do Keycloak também se necessário
            # await self.keycloak_config.delete_user(user.keycloak_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            raise
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        """Lista usuários com paginação"""
        try:
            users = await self.user_repository.list_users(skip, limit)
            return [user.to_response() for user in users]
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    async def get_user_profile(self, token: str) -> Optional[UserResponse]:
        """Obtém o perfil do usuário a partir do token"""
        try:
            validation = await self.validate_token(token)
            return validation.user if validation.valid else None
        except Exception as e:
            logger.error(f"Erro ao obter perfil do usuário: {e}")
            return None 
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
    
    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """Renova um token de acesso"""
        try:
            # Renovar token no Keycloak
            token_data = await self.keycloak_config.refresh_token(refresh_token)
            
            if not token_data:
                raise ValueError("Token de renovação inválido")
            
            # Validar o novo token para obter dados do usuário
            validation = await self.validate_token(token_data['access_token'])
            
            if not validation.valid:
                raise ValueError("Token renovado inválido")
            
            return LoginResponse(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                token_type="bearer",
                expires_in=token_data['expires_in'],
                user=validation.user
            )
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Faz logout de um usuário"""
        try:
            return await self.keycloak_config.logout_user(refresh_token)
        except Exception as e:
            logger.error(f"Erro ao fazer logout: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Busca um usuário pelo ID"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            return user.to_response() if user else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Busca um usuário pelo email"""
        try:
            user = await self.user_repository.get_user_by_email(email)
            return user.to_response() if user else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Atualiza dados de um usuário"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Atualizar campos fornecidos
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            updated_user = await self.user_repository.update_user(user)
            return updated_user.to_response()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Remove um usuário do sistema"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                return False
            
            # Remover do MongoDB
            success = await self.user_repository.delete_user(user_id)
            
            # TODO: Remover do Keycloak também se necessário
            # await self.keycloak_config.delete_user(user.keycloak_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            raise
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        """Lista usuários com paginação"""
        try:
            users = await self.user_repository.list_users(skip, limit)
            return [user.to_response() for user in users]
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    async def get_user_profile(self, token: str) -> Optional[UserResponse]:
        """Obtém o perfil do usuário a partir do token"""
        try:
            validation = await self.validate_token(token)
            return validation.user if validation.valid else None
        except Exception as e:
            logger.error(f"Erro ao obter perfil do usuário: {e}")
            return None 