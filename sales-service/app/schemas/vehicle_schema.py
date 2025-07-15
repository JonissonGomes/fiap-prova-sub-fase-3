from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class VehicleType(str, Enum):
    CAR = "CAR"
    MOTORCYCLE = "MOTORCYCLE"
    TRUCK = "TRUCK"

class VehicleBase(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    price: float
    type: VehicleType
    description: str | None = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 