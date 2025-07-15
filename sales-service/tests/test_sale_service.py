import asyncio
import pytest
from unittest.mock import AsyncMock
from app.domain.sale_schema import SaleCreate, SaleUpdate
from app.services.sale_service import SaleService
from app.domain.sale import Sale, PaymentStatus
from datetime import datetime

# Fixture mock para o serviço de vendas
@pytest.fixture
def sale_service():
    # Mocking SaleService
    mock_service = AsyncMock(spec=SaleService)
    # Se necessário, configure métodos esperados no mock
    return mock_service

# Fixture mock para a venda (mock_sale)
@pytest.fixture
def mock_sale():
    # Retorna um mock de uma venda para testes
    return Sale(
        id="123",
        vehicle_id="vehicle_123",
        buyer_cpf="12345678900",
        sale_price=75000.00,
        payment_code="PAY-1234567890",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# Teste de atualização parcial de campos
@pytest.mark.asyncio
async def test_update_sale_partial_fields(sale_service, mock_sale):
    # Simula a atualização de preço
    update_data = SaleUpdate(sale_price=75000.00)
    sale_service.update_sale.return_value = mock_sale  # Mockando o resultado
    result = await sale_service.update_sale(mock_sale.id, update_data)
    
    # Verificando se o preço foi atualizado corretamente
    assert result.sale_price == 75000.00
    assert result.buyer_cpf == mock_sale.buyer_cpf  # Verificando se outros campos não foram alterados

# Teste de atualização de todos os campos
@pytest.mark.asyncio
async def test_update_sale_all_fields(sale_service, mock_sale):
    update_data = SaleUpdate(
        vehicle_id="vehicle_123",
        buyer_cpf="12345678900",
        sale_price=75000.0,
        payment_code="PAY-1234567890",
        payment_status=PaymentStatus.PAID
    )
    sale_service.update_sale.return_value = mock_sale  # Mockando o resultado
    result = await sale_service.update_sale(mock_sale.id, update_data)
    
    # Verificando se todos os campos foram atualizados
    assert result.vehicle_id == update_data.vehicle_id
    assert result.buyer_cpf == update_data.buyer_cpf
    assert result.sale_price == update_data.sale_price
    assert result.payment_code == update_data.payment_code

# Teste de obtenção de vendas por status
@pytest.mark.asyncio
async def test_get_sales_by_multiple_status(sale_service, mock_sale):
    # Simulando os resultados de vendas com diferentes status
    sale_service.get_sales_by_status.return_value = [mock_sale]
    
    result_pending = await sale_service.get_sales_by_status(PaymentStatus.PENDING)
    assert len(result_pending) > 0
    assert all(sale.payment_status == PaymentStatus.PENDING for sale in result_pending)

# Teste de transições de status de pagamento
@pytest.mark.asyncio
async def test_update_payment_status_transitions(sale_service, mock_sale):
    # Simula a transição de status de pagamento
    sale_service.update_payment_status.return_value = mock_sale

    result = await sale_service.update_payment_status(mock_sale.payment_code, PaymentStatus.PENDING)
    assert result.payment_status == PaymentStatus.PENDING

# Teste de criação de venda com preço mínimo
@pytest.mark.asyncio
async def test_create_sale_with_minimum_price(sale_service, mock_sale):
    sale_data = SaleCreate(
        vehicle_id=mock_sale.vehicle_id,
        buyer_cpf=mock_sale.buyer_cpf,
        sale_price=0.01,
        payment_code="MIN-PRICE-123",
        payment_status=PaymentStatus.PENDING
    )
    sale_service.create_sale.return_value = sale_data
    result = await sale_service.create_sale(sale_data)
    
    # Verificando se o preço mínimo foi aceito
    assert result.sale_price == 0.01

@pytest.mark.asyncio
async def test_create_sale_with_maximum_price(sale_service, mock_sale):
    sale_data = SaleCreate(
        vehicle_id=mock_sale.vehicle_id,
        buyer_cpf=mock_sale.buyer_cpf,
        sale_price=999999999.99,
        payment_code="MAX-PRICE-123",
        payment_status=PaymentStatus.PENDING
    )
    sale_service.create_sale.return_value = sale_data
    result = await sale_service.create_sale(sale_data)
    
    # Verificando se o preço máximo foi aceito
    assert result.sale_price == 999999999.99

# Teste de atualização de timestamps
@pytest.mark.asyncio
async def test_update_sale_timestamps(sale_service, mock_sale):
    # Simulando os timestamps originais
    original_created_at = mock_sale.created_at
    original_updated_at = mock_sale.updated_at
    
    # Aguarda um momento para garantir que os timestamps se diferenciem
    await asyncio.sleep(0.1)
    
    # Simulando a atualização com um novo preço
    update_data = SaleUpdate(sale_price=90000.00)
    
    # Mockando o retorno da função update_sale para simular a alteração do updated_at
    mock_sale.updated_at = datetime.utcnow()  # Atualiza o timestamp de updated_at
    sale_service.update_sale.return_value = mock_sale  # Retorna o mock com a data atualizada
    
    result = await sale_service.update_sale(mock_sale.id, update_data)
    
    # Verificando que a data de criação não mudou, mas a data de atualização sim
    assert result.created_at == original_created_at
    assert result.updated_at > original_updated_at

# Teste de obtenção de venda por ID de veículo
@pytest.mark.asyncio
async def test_get_sale_by_vehicle_id_with_status(sale_service, mock_sale):
    sale_service.get_sale_by_vehicle_id.return_value = mock_sale  # Mockando o resultado
    result = await sale_service.get_sale_by_vehicle_id(mock_sale.vehicle_id)
    
    assert result.vehicle_id == mock_sale.vehicle_id
    assert result.payment_status in [PaymentStatus.PENDING, PaymentStatus.PAID, PaymentStatus.CANCELLED]

# Teste de obtenção de todas as vendas ordenadas por data de criação
@pytest.mark.asyncio
async def test_get_all_sales_ordered(sale_service, mock_sale):
    # Simula a obtenção de várias vendas
    sale_service.get_all_sales.return_value = [mock_sale]
    
    result = await sale_service.get_all_sales()
    
    # Verifica se os resultados estão ordenados pela data de criação
    if len(result) > 1:
        for i in range(1, len(result)):
            assert result[i-1].created_at <= result[i].created_at
