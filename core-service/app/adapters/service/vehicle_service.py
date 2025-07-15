from typing import List
from datetime import datetime, UTC

from app.domain.vehicle import Vehicle, VehicleStatus
from app.ports.vehicle_repository import VehicleRepository
from app.ports.vehicle_service import VehicleService

class VehicleServiceImpl(VehicleService):
    def __init__(self, repository: VehicleRepository):
        self.repository = repository

    def create_vehicle(self, brand: str, model: str, year: int, color: str, price: float) -> Vehicle:
        vehicle = Vehicle(
            brand=brand,
            model=model,
            year=year,
            color=color,
            price=price,
            status="AVAILABLE"
        )
        return self.repository.save(vehicle)

    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        vehicle = self.repository.find_by_id(vehicle_id)
        if not vehicle:
            raise ValueError("Veículo não encontrado")
        return vehicle

    def get_all_vehicles(self) -> List[Vehicle]:
        return self.repository.find_all()

    def get_available_vehicles(self) -> List[Vehicle]:
        return self.repository.find_available()

    def update_vehicle(self, vehicle_id: int, **kwargs) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle.status != "AVAILABLE":
            raise ValueError("Não é possível atualizar um veículo que não está disponível")
        
        for key, value in kwargs.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)
        
        return self.repository.update(vehicle)

    def delete_vehicle(self, vehicle_id: int) -> None:
        vehicle = self.get_vehicle(vehicle_id)
        self.repository.delete(vehicle_id)

    def mark_vehicle_as_sold(self, vehicle_id: int) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle.status != "AVAILABLE":
            raise ValueError("Veículo não está disponível para venda")
        
        vehicle.mark_as_sold()
        return self.repository.update(vehicle)

    def mark_vehicle_as_pending(self, vehicle_id: int) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        if vehicle.status != "AVAILABLE":
            raise ValueError("Veículo não está disponível para venda")
        
        vehicle.mark_as_pending()
        return self.repository.update(vehicle) 