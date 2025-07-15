from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.domain.vehicle import Vehicle, VehicleStatus
from app.ports.vehicle_repository import VehicleRepository

class MongoDBVehicleRepository(VehicleRepository):
    COLLECTION_NAME = "vehicles"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.COLLECTION_NAME]

    async def save(self, vehicle: Vehicle) -> Vehicle:
        now = datetime.utcnow()
        vehicle_dict = {
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
            "price": vehicle.price,
            "status": vehicle.status,
            "created_at": now,
            "updated_at": now
        }
        result = await self.collection.insert_one(vehicle_dict)
        vehicle_dict["_id"] = result.inserted_id
        return self._to_domain(vehicle_dict)

    async def find_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        try:
            vehicle = await self.collection.find_one({"_id": ObjectId(vehicle_id)})
            if vehicle:
                return self._to_domain(vehicle)
        except Exception:
            return None
        return None

    async def find_all(self) -> List[Vehicle]:
        cursor = self.collection.find()
        vehicles = await cursor.to_list(length=None)
        return [self._to_domain(vehicle) for vehicle in vehicles]

    async def find_available(self) -> List[Vehicle]:
        cursor = self.collection.find({"status": VehicleStatus.AVAILABLE})
        vehicles = await cursor.to_list(length=None)
        return [self._to_domain(vehicle) for vehicle in vehicles]

    async def find_by_status(self, status: VehicleStatus) -> List[Vehicle]:
        cursor = self.collection.find({"status": status})
        vehicles = []
        async for vehicle_dict in cursor:
            vehicles.append(self._to_domain(vehicle_dict))
        return vehicles

    async def update(self, vehicle: Vehicle) -> Vehicle:
        vehicle_dict = {
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
            "price": vehicle.price,
            "status": vehicle.status,
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.update_one(
            {"_id": ObjectId(vehicle.id)},
            {"$set": vehicle_dict}
        )
        if result.matched_count == 0:
            raise ValueError("Veículo não encontrado")
        
        updated_vehicle = await self.collection.find_one({"_id": ObjectId(vehicle.id)})
        return self._to_domain(updated_vehicle)

    async def delete(self, vehicle_id: str) -> None:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(vehicle_id)})
            if result.deleted_count == 0:
                raise ValueError("Veículo não encontrado")
        except Exception as e:
            raise ValueError(f"Erro ao deletar veículo: {str(e)}")

    def _to_domain(self, vehicle_dict: dict) -> Vehicle:
        return Vehicle(
            id=str(vehicle_dict["_id"]),
            brand=vehicle_dict["brand"],
            model=vehicle_dict["model"],
            year=vehicle_dict["year"],
            color=vehicle_dict["color"],
            price=vehicle_dict["price"],
            status=vehicle_dict["status"],
            created_at=vehicle_dict.get("created_at"),
            updated_at=vehicle_dict.get("updated_at")
        ) 