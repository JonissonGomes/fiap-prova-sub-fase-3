from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.adapters.repository.database_config import get_database
from app.adapters.repository.mongodb_vehicle_repository import MongoDBVehicleRepository
from app.domain.vehicle_service import VehicleService
from app.ports.vehicle_repository import VehicleRepository

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency function that yields a MongoDB database connection.
    """
    db = await get_database()
    try:
        yield db
    finally:
        pass  # MongoDB não precisa fechar conexão

async def get_vehicle_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> VehicleRepository:
    """
    Dependency function that yields a VehicleRepository instance.
    """
    return MongoDBVehicleRepository(db)

async def get_vehicle_service(
    repository: VehicleRepository = Depends(get_vehicle_repository)
) -> VehicleService:
    """
    Dependency function that yields a VehicleService instance.
    """
    return VehicleService(repository)
