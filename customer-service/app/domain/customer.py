from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do cliente")
    email: EmailStr = Field(..., description="Email do cliente")
    phone: str = Field(..., min_length=10, max_length=15, description="Telefone do cliente")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF do cliente")
    address: Optional[str] = Field(None, max_length=200, description="Endereço do cliente")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do cliente")
    state: Optional[str] = Field(None, max_length=2, description="Estado do cliente")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP do cliente")

    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', v)
        
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            raise ValueError('CPF inválido')
        
        # Validação do CPF
        def validate_cpf_algorithm(cpf):
            # Primeiro dígito verificador
            sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
            digit1 = 11 - (sum1 % 11)
            if digit1 >= 10:
                digit1 = 0
            
            # Segundo dígito verificador
            sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
            digit2 = 11 - (sum2 % 11)
            if digit2 >= 10:
                digit2 = 0
            
            return cpf[9] == str(digit1) and cpf[10] == str(digit2)
        
        if not validate_cpf_algorithm(cpf):
            raise ValueError('CPF inválido')
        
        return cpf

    @validator('phone')
    def validate_phone(cls, v):
        # Remove caracteres não numéricos
        phone = re.sub(r'[^0-9]', '', v)
        
        if len(phone) < 10 or len(phone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        
        return phone

    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter 2 caracteres')
        return v.upper() if v else v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome completo do cliente")
    email: Optional[EmailStr] = Field(None, description="Email do cliente")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Telefone do cliente")
    address: Optional[str] = Field(None, max_length=200, description="Endereço do cliente")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do cliente")
    state: Optional[str] = Field(None, max_length=2, description="Estado do cliente")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP do cliente")

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove caracteres não numéricos
            phone = re.sub(r'[^0-9]', '', v)
            
            if len(phone) < 10 or len(phone) > 11:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
            
            return phone
        return v

    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter 2 caracteres')
        return v.upper() if v else v

class Customer(CustomerBase):
    id: Optional[str] = Field(None, description="ID do cliente")
    user_id: Optional[str] = Field(None, description="ID do usuário associado")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    active: bool = Field(default=True, description="Cliente ativo")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True

    def to_dict(self):
        """Converte o cliente para um dicionário"""
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "cpf": self.cpf,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Cria um cliente a partir de um dicionário"""
        return cls(
            id=str(data.get("_id", "")),
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            cpf=data["cpf"],
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            user_id=data.get("user_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            active=data.get("active", True)
        )

class CustomerResponse(CustomerBase):
    id: str = Field(..., description="ID do cliente")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    active: bool = Field(..., description="Cliente ativo")

class CustomerSearchRequest(BaseModel):
    cpf: Optional[str] = Field(None, description="CPF para busca")
    email: Optional[str] = Field(None, description="Email para busca")
    phone: Optional[str] = Field(None, description="Telefone para busca")
    name: Optional[str] = Field(None, description="Nome para busca (parcial)")

class CustomerStatsResponse(BaseModel):
    total_customers: int = Field(..., description="Total de clientes")
    active_customers: int = Field(..., description="Clientes ativos")
    inactive_customers: int = Field(..., description="Clientes inativos")
    customers_this_month: int = Field(..., description="Clientes cadastrados este mês") 
from typing import Optional
from datetime import datetime
import re

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do cliente")
    email: EmailStr = Field(..., description="Email do cliente")
    phone: str = Field(..., min_length=10, max_length=15, description="Telefone do cliente")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF do cliente")
    address: Optional[str] = Field(None, max_length=200, description="Endereço do cliente")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do cliente")
    state: Optional[str] = Field(None, max_length=2, description="Estado do cliente")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP do cliente")

    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', v)
        
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            raise ValueError('CPF inválido')
        
        # Validação do CPF
        def validate_cpf_algorithm(cpf):
            # Primeiro dígito verificador
            sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
            digit1 = 11 - (sum1 % 11)
            if digit1 >= 10:
                digit1 = 0
            
            # Segundo dígito verificador
            sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
            digit2 = 11 - (sum2 % 11)
            if digit2 >= 10:
                digit2 = 0
            
            return cpf[9] == str(digit1) and cpf[10] == str(digit2)
        
        if not validate_cpf_algorithm(cpf):
            raise ValueError('CPF inválido')
        
        return cpf

    @validator('phone')
    def validate_phone(cls, v):
        # Remove caracteres não numéricos
        phone = re.sub(r'[^0-9]', '', v)
        
        if len(phone) < 10 or len(phone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        
        return phone

    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter 2 caracteres')
        return v.upper() if v else v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome completo do cliente")
    email: Optional[EmailStr] = Field(None, description="Email do cliente")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Telefone do cliente")
    address: Optional[str] = Field(None, max_length=200, description="Endereço do cliente")
    city: Optional[str] = Field(None, max_length=100, description="Cidade do cliente")
    state: Optional[str] = Field(None, max_length=2, description="Estado do cliente")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP do cliente")

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove caracteres não numéricos
            phone = re.sub(r'[^0-9]', '', v)
            
            if len(phone) < 10 or len(phone) > 11:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
            
            return phone
        return v

    @validator('state')
    def validate_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter 2 caracteres')
        return v.upper() if v else v

class Customer(CustomerBase):
    id: Optional[str] = Field(None, description="ID do cliente")
    user_id: Optional[str] = Field(None, description="ID do usuário associado")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    active: bool = Field(default=True, description="Cliente ativo")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True

    def to_dict(self):
        """Converte o cliente para um dicionário"""
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "cpf": self.cpf,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Cria um cliente a partir de um dicionário"""
        return cls(
            id=str(data.get("_id", "")),
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            cpf=data["cpf"],
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            user_id=data.get("user_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            active=data.get("active", True)
        )

class CustomerResponse(CustomerBase):
    id: str = Field(..., description="ID do cliente")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    active: bool = Field(..., description="Cliente ativo")

class CustomerSearchRequest(BaseModel):
    cpf: Optional[str] = Field(None, description="CPF para busca")
    email: Optional[str] = Field(None, description="Email para busca")
    phone: Optional[str] = Field(None, description="Telefone para busca")
    name: Optional[str] = Field(None, description="Nome para busca (parcial)")

class CustomerStatsResponse(BaseModel):
    total_customers: int = Field(..., description="Total de clientes")
    active_customers: int = Field(..., description="Clientes ativos")
    inactive_customers: int = Field(..., description="Clientes inativos")
    customers_this_month: int = Field(..., description="Clientes cadastrados este mês") 