from typing import List, Optional
from app.domain.vehicle import Vehicle, VehicleStatus
from app.ports.vehicle_repository import VehicleRepository
from datetime import datetime

class VehicleService:
    def __init__(self, vehicle_repository: VehicleRepository):
        self.vehicle_repository = vehicle_repository

    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        return await self.vehicle_repository.save(vehicle)

    async def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        return await self.vehicle_repository.find_by_id(vehicle_id)

    async def list_vehicles(self) -> List[Vehicle]:
        return await self.vehicle_repository.find_all()

    async def list_vehicles_by_status(self, status: VehicleStatus) -> List[Vehicle]:
        return await self.vehicle_repository.find_by_status(status)

    async def list_available_vehicles(self) -> List[Vehicle]:
        return await self.vehicle_repository.find_available()

    async def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        return await self.vehicle_repository.update(vehicle)

    async def delete_vehicle(self, vehicle_id: str) -> None:
        await self.vehicle_repository.delete(vehicle_id)

    async def update_vehicle_status(self, vehicle_id: str, status: VehicleStatus) -> Vehicle:
        vehicle = await self.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError("Veículo não encontrado")
        
        if status == VehicleStatus.SOLD:
            vehicle.mark_as_sold()
        elif status == VehicleStatus.RESERVED:
            vehicle.mark_as_pending()
        elif status == VehicleStatus.AVAILABLE:
            if vehicle.status == VehicleStatus.RESERVED:
                vehicle.status = VehicleStatus.AVAILABLE
                vehicle.updated_at = datetime.now()
            else:
                raise ValueError("Apenas veículos reservados podem ser marcados como disponíveis")
        
        return await self.update_vehicle(vehicle) 