from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class PaymentStatus(str, Enum):
    PENDING = "PENDENTE"
    PAID = "PAGO"
    CANCELLED = "CANCELADA"

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Sale(BaseModel):
    """Modelo de domínio para uma venda."""
    id: Optional[str] = None
    vehicle_id: str
    buyer_cpf: str
    sale_price: float
    payment_code: str
    payment_status: PaymentStatus = PaymentStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Configuração do modelo."""
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    def __init__(self, **data):
        if not data.get("created_at"):
            data["created_at"] = datetime.now()
        if not data.get("updated_at"):
            data["updated_at"] = datetime.now()
        super().__init__(**data)

    def update(self, **kwargs):
        """Atualiza os campos da venda."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def to_dict(self):
        """Converte a venda para um dicionário."""
        return {
            "_id": ObjectId(self.id),
            "vehicle_id": self.vehicle_id,
            "buyer_cpf": self.buyer_cpf,
            "sale_price": self.sale_price,
            "payment_code": self.payment_code,
            "payment_status": self.payment_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Cria uma venda a partir de um dicionário."""
        return cls(
            id=str(data["_id"]),
            vehicle_id=data["vehicle_id"],
            buyer_cpf=data["buyer_cpf"],
            sale_price=data["sale_price"],
            payment_code=data["payment_code"],
            payment_status=PaymentStatus(data["payment_status"]),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        ) 