from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.vehicle import Vehicle

class VehicleService(ABC):
    @abstractmethod
    def create_vehicle(self, brand: str, model: str, year: int, color: str, price: float) -> Vehicle:
        pass

    @abstractmethod
    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        pass

    @abstractmethod
    def get_all_vehicles(self) -> List[Vehicle]:
        pass

    @abstractmethod
    def get_available_vehicles(self) -> List[Vehicle]:
        pass

    @abstractmethod
    def update_vehicle(self, vehicle_id: int, **kwargs) -> Vehicle:
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: int) -> None:
        pass

    @abstractmethod
    def mark_vehicle_as_sold(self, vehicle_id: int) -> Vehicle:
        pass

    @abstractmethod
    def mark_vehicle_as_pending(self, vehicle_id: int) -> Vehicle:
        pass 