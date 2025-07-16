from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    SALES = "SALES"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., description="Nome completo do usuário")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Papel do usuário")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Status do usuário")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Senha do usuário")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    name: Optional[str] = Field(None, description="Nome completo do usuário")
    role: Optional[UserRole] = Field(None, description="Papel do usuário")
    status: Optional[UserStatus] = Field(None, description="Status do usuário")

class UserResponse(UserBase):
    id: str = Field(..., description="ID do usuário")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    last_login: Optional[datetime] = Field(None, description="Último login")

class User(UserBase):
    id: Optional[str] = Field(None, description="ID do usuário")
    password_hash: str = Field(..., description="Hash da senha")
    keycloak_id: Optional[str] = Field(None, description="ID do usuário no Keycloak")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    last_login: Optional[datetime] = Field(None, description="Último login")

    model_config = ConfigDict(from_attributes=True)

    def to_response(self) -> UserResponse:
        return UserResponse(
            id=self.id,
            email=self.email,
            name=self.name,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login=self.last_login
        )

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de renovação")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UserResponse = Field(..., description="Dados do usuário")

class TokenValidationRequest(BaseModel):
    token: str = Field(..., description="Token para validação")

class TokenValidationResponse(BaseModel):
    valid: bool = Field(..., description="Se o token é válido")
    user: Optional[UserResponse] = Field(None, description="Dados do usuário se token válido")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração do token")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Token de renovação") 