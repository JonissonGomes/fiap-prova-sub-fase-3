import pytest
import os
from app.infrastructure.mongodb_config import MongoDBSettings, MongoDB

@pytest.mark.asyncio
async def test_mongodb_connection_error():
    os.environ["MONGODB_URL"] = "mongodb://invalid_host:27017"
    
    mongodb = MongoDB()
    with pytest.raises(Exception):
        await mongodb.connect()
    
    del os.environ["MONGODB_URL"]

