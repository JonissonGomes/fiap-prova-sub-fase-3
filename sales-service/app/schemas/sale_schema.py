from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADA"

class SaleBase(BaseModel):
    """Schema base para vendas."""
    vehicle_id: str = Field(..., min_length=1, description="ID do veículo")
    buyer_cpf: str = Field(..., min_length=11, max_length=11, description="CPF do comprador")
    sale_price: float = Field(..., gt=0, description="Preço da venda")
    payment_code: str = Field(..., min_length=1, description="Código do pagamento")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Status do pagamento")

    @field_validator('buyer_cpf')
    @classmethod
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        return v

    @field_validator('payment_status', mode='before')
    @classmethod
    def validate_payment_status(cls, v):
        if isinstance(v, str):
            try:
                return PaymentStatus(v)
            except ValueError:
                raise ValueError(f"Status de pagamento inválido: {v}")
        return v

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    """Schema para atualização de vendas com campos opcionais."""
    vehicle_id: Optional[str] = Field(None, min_length=1, description="ID do veículo")
    buyer_cpf: Optional[str] = Field(None, min_length=11, max_length=11, description="CPF do comprador")
    sale_price: Optional[float] = Field(None, gt=0, description="Preço da venda")
    payment_code: Optional[str] = Field(None, min_length=1, description="Código do pagamento")
    payment_status: Optional[PaymentStatus] = Field(None, description="Status do pagamento")

    @field_validator('buyer_cpf')
    @classmethod
    def validate_cpf(cls, v):
        if v is None:
            return v
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        return v

    @field_validator('payment_status', mode='before')
    @classmethod
    def validate_payment_status(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return PaymentStatus(v)
            except ValueError:
                raise ValueError(f"Status de pagamento inválido: {v}")
        return v

class SaleResponse(SaleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_domain(cls, sale):
        return cls(
            id=str(sale.id),
            vehicle_id=sale.vehicle_id,
            buyer_cpf=sale.buyer_cpf,
            sale_price=sale.sale_price,
            payment_status=sale.payment_status,
            payment_code=sale.payment_code,
            created_at=sale.created_at,
            updated_at=sale.updated_at
        ) 