import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from app.services.sale_service_impl import SaleServiceImpl
from app.domain.sale import Sale
from app.schemas.sale_schema import SaleCreate, SaleUpdate, PaymentStatus
from datetime import datetime
import os
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def mock_mongodb():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    yield client
    client.close()

@pytest_asyncio.fixture
async def repository(mock_mongodb):
    db_name = os.getenv("MONGODB_DB_NAME", "sales_db")
    collection_name = os.getenv("MONGODB_COLLECTION", "sales")
    return MongoDBSaleRepository(mock_mongodb, db_name, collection_name)

@pytest_asyncio.fixture
async def service(repository):
    return SaleServiceImpl(repository)

@pytest.fixture
def mock_sale():
    return Sale(
        id="test_id",
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def mock_sale_create():
    return SaleCreate(
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code"
    )

@pytest.fixture
def mock_sale_update():
    return SaleUpdate(
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=55000.0,
        payment_code="test_payment_code_updated",
        payment_status=PaymentStatus.PAID
    )

@pytest.fixture
def mock_sales_list():
    return [
        Sale(
            id=f"test_id_{i}",
            vehicle_id=f"test_vehicle_id_{i}",
            buyer_cpf="12345678900",
            sale_price=50000.0 + (i * 1000),
            payment_code=f"test_payment_code_{i}",
            payment_status=PaymentStatus.PENDING if i % 2 == 0 else PaymentStatus.PAID,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(5)
    ]

@pytest_asyncio.fixture
async def clean_database(repository):
    """Fixture para limpar o banco de dados antes e depois dos testes"""
    await repository.collection.delete_many({})
    yield
    await repository.collection.delete_many({})

@pytest_asyncio.fixture
async def populated_database(repository, mock_sales_list):
    """Fixture para popular o banco de dados com dados de teste"""
    for sale in mock_sales_list:
        await repository.save(sale)
    return mock_sales_list 