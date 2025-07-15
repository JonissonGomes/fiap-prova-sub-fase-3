from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.vehicle import Vehicle

class VehicleRepository(ABC):
    @abstractmethod
    async def save(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    async def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        pass

    @abstractmethod
    async def find_all(self) -> List[Vehicle]:
        pass

    @abstractmethod
    async def find_available(self) -> List[Vehicle]:
        pass

    @abstractmethod
    async def update(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    async def delete(self, vehicle_id: str) -> None:
        pass 