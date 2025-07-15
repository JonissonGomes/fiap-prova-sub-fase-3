from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VehicleStatus(str, Enum):
    AVAILABLE = "DISPONÍVEL"
    SOLD = "VENDIDO"
    RESERVED = "RESERVADO"

class VehicleBase(BaseModel):
    brand: str = Field(..., description="Marca do veículo")
    model: str = Field(..., description="Modelo do veículo")
    year: int = Field(..., description="Ano do veículo")
    color: str = Field(..., description="Cor do veículo")
    price: float = Field(..., description="Preço do veículo")
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, description="Status do veículo")

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    brand: Optional[str] = Field(None, description="Marca do veículo")
    model: Optional[str] = Field(None, description="Modelo do veículo")
    year: Optional[int] = Field(None, description="Ano do veículo")
    color: Optional[str] = Field(None, description="Cor do veículo")
    price: Optional[float] = Field(None, description="Preço do veículo")

class Vehicle(VehicleBase):
    id: Optional[str] = Field(None, description="ID do veículo")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True

    def _validate(self):
        if self.year < 1900 or self.year > datetime.now().year:
            raise ValueError("Ano do veículo inválido")
        
        if self.price <= 0:
            raise ValueError("Preço do veículo deve ser maior que zero")
        
        if self.status not in [status.value for status in VehicleStatus]:
            raise ValueError("Status do veículo inválido")

    def mark_as_sold(self):
        if self.status == "VENDIDO":
            raise ValueError("Veículo já está vendido")
        if self.status not in ["DISPONÍVEL", "RESERVADO"]:
            raise ValueError("Veículo não está disponível para venda")
        
        self.status = "VENDIDO"
        self.updated_at = datetime.now()

    def mark_as_pending(self):
        if self.status == "RESERVADO":
            raise ValueError("Veículo já está reservado")
        if self.status != "DISPONÍVEL":
            raise ValueError("Veículo não está disponível para venda")
        
        self.status = "RESERVADO"
        self.updated_at = datetime.now()

    def update(self, **kwargs):
        if self.status != "DISPONÍVEL":
            raise ValueError("Não é possível atualizar um veículo que não está disponível")
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self._validate()
        self.updated_at = datetime.now() 