import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.services.sale_service_impl import SaleServiceImpl
from app.domain.sale import Sale, PaymentStatus
from app.schemas.sale_schema import SaleCreate, SaleUpdate
from app.exceptions import SaleNotFoundError, InvalidSaleDataError

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def sale_service(mock_repository):
    return SaleServiceImpl(mock_repository)

@pytest.mark.asyncio
async def test_create_sale_error(sale_service, mock_repository):
    mock_repository.save.side_effect = Exception("Erro ao salvar venda")
    
    with pytest.raises(Exception) as exc_info:
        await sale_service.create_sale(SaleCreate(
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code"
        ))
    
    assert "Erro ao salvar venda"

@pytest.mark.asyncio
async def test_update_sale_error(sale_service, mock_repository):
    mock_repository.find_by_id.return_value = None

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.update_sale("test_id", SaleUpdate(
            sale_price=60000.0
        ))
    
    assert "Venda com ID test_id não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_sale_error(sale_service, mock_repository):
    mock_repository.delete.return_value = False

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.delete_sale("test_id")
    
    assert "Venda com ID test_id não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_payment_status_error(sale_service, mock_repository):
    mock_repository.find_by_id.return_value = None

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.update_payment_status("test_sale_id", PaymentStatus.PAID)
    
    assert "Venda com ID test_sale_id não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_update_payment_status_success(sale_service, mock_repository):
    # Mock de uma venda existente
    mock_sale = Sale(
        id="test_id",
        vehicle_id="test_vehicle",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    mock_repository.find_by_id.return_value = mock_sale
    mock_repository.update.return_value = mock_sale
    
    result = await sale_service.update_payment_status("test_id", PaymentStatus.PAID)
    
    assert result.payment_status == PaymentStatus.PAID
    mock_repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_get_sale_error(sale_service, mock_repository):
    mock_repository.find_by_id.return_value = None

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.get_sale("test_id")
    
    assert "Venda com ID test_id não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_sale_by_vehicle_id_error(sale_service, mock_repository):
    mock_repository.find_by_vehicle_id.return_value = None

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.get_sale_by_vehicle_id("test_vehicle_id")
    
    assert "Venda com veículo ID test_vehicle_id não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_sale_by_payment_code_error(sale_service, mock_repository):
    mock_repository.find_by_payment_code.return_value = None

    with pytest.raises(SaleNotFoundError) as exc_info:
        await sale_service.get_sale_by_payment_code("test_payment_code")
    
    assert "Venda com código de pagamento test_payment_code não encontrada" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_all_sales_error(sale_service, mock_repository):
    mock_repository.find_all.side_effect = Exception("Erro ao listar vendas")
    
    with pytest.raises(Exception) as exc_info:
        await sale_service.get_all_sales()
    
    assert "Erro ao listar vendas" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_sales_by_status_error(sale_service, mock_repository):
    mock_repository.find_by_status.side_effect = Exception("Erro ao listar vendas por status")
    
    with pytest.raises(Exception) as exc_info:
        await sale_service.get_sales_by_status(PaymentStatus.PENDING)
    
    assert "Erro ao listar vendas por status" in str(exc_info.value) 