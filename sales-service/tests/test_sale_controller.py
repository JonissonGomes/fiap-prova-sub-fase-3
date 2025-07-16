import pytest
import pytest_asyncio
from datetime import datetime
from fastapi import FastAPI
from httpx import AsyncClient
from bson import ObjectId
from app.controllers.sale_controller import router, get_service
from app.middleware.auth import get_current_user, require_role
from app.domain.sale import Sale, PaymentStatus
from app.schemas.sale_schema import SaleCreate, SaleUpdate, SaleResponse
from app.exceptions import SaleNotFoundError

valid_id = str(ObjectId())

@pytest.fixture
def app(mock_sale_service):
    app = FastAPI()

    async def override_get_service():
        return mock_sale_service

    # Mock das dependências de autenticação
    async def mock_get_current_user():
        return {"user_id": "test_user", "email": "test@example.com", "role": "ADMIN"}

    async def mock_require_role(roles):
        return {"user_id": "test_user", "email": "test@example.com", "role": "ADMIN"}

    app.dependency_overrides[get_service] = override_get_service
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_role] = mock_require_role
    app.include_router(router)
    return app

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_sale():
    return Sale(
        id=str(ObjectId()),
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def mock_sale_service():
    class MockSaleService:
        async def create_sale(self, sale: Sale) -> Sale:
            return Sale(
                id=str(ObjectId()),
                vehicle_id=sale.vehicle_id,
                buyer_cpf=sale.buyer_cpf,
                sale_price=sale.sale_price,
                payment_code=sale.payment_code,
                payment_status=PaymentStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        async def get_sale(self, sale_id: str) -> Sale:
            return Sale(
                id=sale_id,
                vehicle_id="test_vehicle_id",
                buyer_cpf="12345678900",
                sale_price=50000.0,
                payment_code="test_payment_code",
                payment_status=PaymentStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        async def get_all_sales(self) -> list[Sale]:
            return [
                Sale(
                    id=str(ObjectId()),
                    vehicle_id="test_vehicle_id",
                    buyer_cpf="12345678900",
                    sale_price=50000.0,
                    payment_code="test_payment_code",
                    payment_status=PaymentStatus.PENDING,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]

        async def update_sale(self, sale_id: str, sale_update: SaleUpdate) -> Sale:
            return Sale(
                id=sale_id,
                vehicle_id=sale_update.vehicle_id,
                buyer_cpf=sale_update.buyer_cpf,
                sale_price=sale_update.sale_price,
                payment_code=sale_update.payment_code,
                payment_status=sale_update.payment_status,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        async def delete_sale(self, sale_id: str) -> bool:
            return True

        async def get_sales_by_status(self, status: PaymentStatus) -> list[Sale]:
            return [
                Sale(
                    id=str(ObjectId()),
                    vehicle_id="test_vehicle_id",
                    buyer_cpf="12345678900",
                    sale_price=50000.0,
                    payment_code="test_payment_code",
                    payment_status=status,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]

        async def get_sale_by_payment_code(self, payment_code: str) -> Sale:
            return Sale(
                id=str(ObjectId()),
                vehicle_id="test_vehicle_id",
                buyer_cpf="12345678900",
                sale_price=50000.0,
                payment_code=payment_code,
                payment_status=PaymentStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        async def update_payment_status(self, sale_id: str, status: PaymentStatus) -> Sale:
            return Sale(
                id=sale_id,
                vehicle_id="test_vehicle_id",
                buyer_cpf="12345678900",
                sale_price=50000.0,
                payment_code="test_payment_code",
                payment_status=status,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    return MockSaleService()

@pytest.mark.asyncio
async def test_create_sale(client):
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": "test_vehicle_id",
            "buyer_cpf": "12345678900",
            "sale_price": 50000.0,
            "payment_code": "test_payment_code"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == "test_vehicle_id"
    assert data["buyer_cpf"] == "12345678900"
    assert data["sale_price"] == 50000.0
    assert data["payment_code"] == "test_payment_code"
    assert data["payment_status"] == "PENDENTE"

@pytest.mark.asyncio
async def test_get_sale_success(client):
    response = await client.get(f"/sales/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == valid_id
    assert data["vehicle_id"] == "test_vehicle_id"
    assert data["buyer_cpf"] == "12345678900"
    assert data["sale_price"] == 50000.0
    assert data["payment_code"] == "test_payment_code"
    assert data["payment_status"] == "PENDENTE"

@pytest.mark.asyncio
async def test_get_all_sales(client):
    response = await client.get("/sales/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["vehicle_id"] == "test_vehicle_id"
    assert data[0]["buyer_cpf"] == "12345678900"
    assert data[0]["sale_price"] == 50000.0
    assert data[0]["payment_code"] == "test_payment_code"
    assert data[0]["payment_status"] == "PENDENTE"

@pytest.mark.asyncio
async def test_get_sales_by_status(client):
    response = await client.get("/sales/status/PENDENTE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["payment_status"] == "PENDENTE"

@pytest.mark.asyncio
async def test_get_sale_by_payment_code(client):
    response = await client.get("/sales/payment/test_payment_code")
    assert response.status_code == 200
    data = response.json()
    assert data["payment_code"] == "test_payment_code"

@pytest.mark.asyncio
async def test_update_sale_success(client):
    valid_id = str(ObjectId())
    response = await client.put(
        f"/sales/{valid_id}",
        json={
            "vehicle_id": "valid_vehicle_id",
            "buyer_cpf": "98765432100",
            "sale_price": 60000.0,
            "payment_code": "updated_payment_code",
            "payment_status": "PAGO"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == "valid_vehicle_id"
    assert data["buyer_cpf"] == "98765432100"
    assert data["sale_price"] == 60000.0
    assert data["payment_code"] == "updated_payment_code"
    assert data["payment_status"] == "PAGO"









@pytest.mark.asyncio
async def test_get_sale_not_found(client):
    response = await client.get("/sales/non_existent_id")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "ID inválido"

@pytest.mark.asyncio
async def test_update_sale_not_found(client):
    response = await client.put(
        "/sales/non_existent_id",
        json={
            "vehicle_id": "updated_vehicle_id",
            "buyer_cpf": "98765432100",
            "sale_price": 60000.0,
            "payment_code": "updated_payment_code",
            "payment_status": "PAGO"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "ID inválido"



@pytest.mark.asyncio
async def test_get_sale_by_payment_code_not_found(app):
    class FailingMockSaleService:
        async def get_sale_by_payment_code(self, payment_code: str):
            raise SaleNotFoundError("ID inválido")

    async def override_get_service():
        return FailingMockSaleService()

    app.dependency_overrides[get_service] = override_get_service

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/sales/payment/non_existent_code")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Venda com ID ID inválido não encontrada"










@pytest.mark.asyncio
async def test_create_sale_invalid_data(client):
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": "",  # Campo vazio
            "buyer_cpf": "123",  # CPF inválido
            "sale_price": -100,  # Preço negativo
            "payment_code": ""  # Código vazio
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_update_sale_invalid_data(client):
    response = await client.put(
        "/sales/test_id",
        json={
            "vehicle_id": "",  # Campo vazio
            "buyer_cpf": "123",  # CPF inválido
            "sale_price": -100,  # Preço negativo
            "payment_code": "",  # Código vazio
            "payment_status": "INVALID_STATUS"  # Status inválido
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_create_sale_with_invalid_data(client, mock_sale):
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": "invalid_id",
            "buyer_cpf": "123",
            "sale_price": -100.00
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_sale_with_invalid_data(client, mock_sale):
    response = await client.put(
        f"/sales/{mock_sale.id}",
        json={
            "sale_price": -100.00,
            "payment_status": "invalid_status"
        }
    )
    assert response.status_code == 422







@pytest.mark.asyncio
async def test_get_sale_by_payment_code_with_invalid_code(client):
    response = await client.get(
        "/sales/payment/invalid_code"
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_sales_by_status_with_invalid_status(client):
    response = await client.get(
        "/sales/status/invalid_status"
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_sale_with_missing_fields(client):
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": str(ObjectId())
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_sale_with_duplicate_payment_code(client, mock_sale):
    # Primeiro cria uma venda
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": mock_sale.vehicle_id,
            "buyer_cpf": mock_sale.buyer_cpf,
            "sale_price": mock_sale.sale_price
        }
    )
    assert response.status_code == 422

    # Tenta criar outra venda com o mesmo código de pagamento
    response = await client.post(
        "/sales/",
        json={
            "vehicle_id": str(ObjectId()),
            "buyer_cpf": "98765432109",
            "sale_price": 60000.00
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_all_sales_with_empty_database(client):
    response = await client.get("/sales/")
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_get_sales_by_status_with_empty_database(client):
    response = await client.get("/sales/status/pending")
    assert response.status_code == 422
    assert len(response.json()) == 1 