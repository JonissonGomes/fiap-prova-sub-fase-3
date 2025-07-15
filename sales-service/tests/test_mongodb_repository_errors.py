import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from bson import ObjectId
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from app.domain.sale import Sale, PaymentStatus
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture
def mock_client():
    return AsyncMock(spec=AsyncIOMotorClient)

@pytest.fixture
def repository(mock_client):
    return MongoDBSaleRepository(mock_client)

@pytest.mark.asyncio
async def test_save_error(repository):
    repository.collection.insert_one.side_effect = Exception("Erro ao salvar venda")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.save(Sale(
            id=str(ObjectId()),
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code",
            payment_status=PaymentStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))
    
    assert "Erro ao salvar venda" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_by_id_error(repository):
    repository.collection.find_one.side_effect = Exception("Erro ao buscar venda")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.find_by_id(str(ObjectId()))
    
    assert "Erro ao buscar venda" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_by_vehicle_id_error(repository):
    repository.collection.find_one.side_effect = Exception("Erro ao buscar venda por ID do veículo")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.find_by_vehicle_id("test_vehicle_id")
    
    assert "Erro ao buscar venda por ID do veículo" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_by_payment_code_error(repository):
    repository.collection.find_one.side_effect = Exception("Erro ao buscar venda por código de pagamento")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.find_by_payment_code("test_payment_code")
    
    assert "Erro ao buscar venda por código de pagamento" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_all_error(repository):
    repository.collection.find.side_effect = Exception("Erro ao listar vendas")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.find_all()
    
    assert "Erro ao listar vendas" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_by_status_error(repository):
    repository.collection.find.side_effect = Exception("Erro ao listar vendas por status")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.find_by_status(PaymentStatus.PENDING)
    
    assert "Erro ao listar vendas por status" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_error(repository):
    repository.collection.update_one.side_effect = Exception("Erro ao atualizar venda")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.update(Sale(
            id=str(ObjectId()),
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code",
            payment_status=PaymentStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))
    
    assert "Erro ao atualizar venda" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_error(repository):
    repository.collection.delete_one.side_effect = Exception("Erro ao remover venda")
    
    with pytest.raises(ValueError) as exc_info:
        await repository.delete(str(ObjectId()))
    
    assert "Erro ao remover venda" in str(exc_info.value)

@pytest.mark.asyncio
async def test_find_by_id_invalid_object_id(repository):
    with pytest.raises(ValueError) as exc_info:
        await repository.find_by_id("ID de venda inválido")
    
    assert "ID de venda inválido" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_invalid_object_id(repository):
    with pytest.raises(ValueError) as exc_info:
        await repository.update(Sale(
            id="invalid_id",
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code",
            payment_status=PaymentStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))
    
    assert "ID de venda inválido"