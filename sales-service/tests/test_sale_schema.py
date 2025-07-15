import pytest
from datetime import datetime
from app.schemas.sale_schema import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    PaymentStatus
)

def test_sale_create_schema():
    sale_data = {
        "vehicle_id": "test_vehicle_id",
        "buyer_cpf": "12345678900",
        "sale_price": 50000.0,
        "payment_code": "test_payment_code"
    }
    
    sale = SaleCreate(**sale_data)
    assert sale.vehicle_id == "test_vehicle_id"
    assert sale.buyer_cpf == "12345678900"
    assert sale.sale_price == 50000.0
    assert sale.payment_code == "test_payment_code"
    assert sale.payment_status == PaymentStatus.PENDING

def test_sale_create_schema_validation():
    with pytest.raises(ValueError):
        SaleCreate(
            vehicle_id="",  # ID vazio
            buyer_cpf="123",  # CPF inválido
            sale_price=-100.0,  # Preço negativo
            payment_code=""  # Código vazio
        )

def test_sale_update_schema():
    sale_data = {
        "vehicle_id": "valid_vehicle_id",
        "buyer_cpf": "98765432100",
        "sale_price": 60000.0,
        "payment_code": "updated_payment_code",
        "payment_status": PaymentStatus.PAID
    }
    
    sale = SaleUpdate(**sale_data)
    assert sale.vehicle_id == "valid_vehicle_id"
    assert sale.buyer_cpf == "98765432100"
    assert sale.sale_price == 60000.0
    assert sale.payment_code == "updated_payment_code"
    assert sale.payment_status == PaymentStatus.PAID

def test_sale_response_schema():
    sale_data = {
        "id": "test_id",
        "vehicle_id": "test_vehicle_id",
        "buyer_cpf": "12345678900",
        "sale_price": 50000.0,
        "payment_code": "test_payment_code",
        "payment_status": PaymentStatus.PENDING,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    sale = SaleResponse(**sale_data)
    assert sale.id == "test_id"
    assert sale.vehicle_id == "test_vehicle_id"
    assert sale.buyer_cpf == "12345678900"
    assert sale.sale_price == 50000.0
    assert sale.payment_code == "test_payment_code"
    assert sale.payment_status == PaymentStatus.PENDING
    assert isinstance(sale.created_at, datetime)
    assert isinstance(sale.updated_at, datetime)

def test_payment_status_enum():
    assert PaymentStatus.PENDING == "PENDENTE"
    assert PaymentStatus.PAID == "PAGO"
    assert PaymentStatus.CANCELLED == "CANCELADA"
    
    with pytest.raises(ValueError):
        PaymentStatus("INVALID_STATUS")

def test_sale_create_schema_with_min_max_values():
    # Teste com valor mínimo
    sale_min = SaleCreate(
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=0.01,
        payment_code="test_payment_code"
    )
    assert sale_min.sale_price == 0.01
    
    # Teste com valor máximo
    sale_max = SaleCreate(
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=999999999.99,
        payment_code="test_payment_code"
    )
    assert sale_max.sale_price == 999999999.99

def test_sale_update_schema_with_invalid_status():
    with pytest.raises(ValueError):
        SaleUpdate(
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code",
            payment_status="INVALID_STATUS"
        )

def test_sale_response_schema_with_invalid_dates():
    with pytest.raises(ValueError):
        SaleResponse(
            id="test_id",
            vehicle_id="test_vehicle_id",
            buyer_cpf="12345678900",
            sale_price=50000.0,
            payment_code="test_payment_code",
            payment_status=PaymentStatus.PENDING,
            created_at="invalid_date",
            updated_at=datetime.now()
        ) 