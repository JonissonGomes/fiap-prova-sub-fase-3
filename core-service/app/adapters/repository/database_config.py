from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://core-mongodb:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "core_db")

async def get_database() -> AsyncIOMotorDatabase:
    """
    Get a MongoDB database instance.
    """
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[MONGODB_DB] 