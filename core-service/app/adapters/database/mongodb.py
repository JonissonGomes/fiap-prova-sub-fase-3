"""
MongoDB configuration and connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _client = None
    _db = None

    @classmethod
    async def get_db(cls):
        if cls._db is None:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
            mongodb_db = os.getenv("MONGODB_DATABASE", "vehicle_db")
            
            cls._client = AsyncIOMotorClient(mongodb_url)
            cls._db = cls._client[mongodb_db]
        
        return cls._db

    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None 