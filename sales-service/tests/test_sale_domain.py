import pytest
from datetime import datetime
from bson import ObjectId
from app.domain.sale import Sale, PaymentStatus
from app.exceptions import InvalidSaleDataError

def test_sale_creation():
    sale = Sale(
        id="test_id",
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert sale.id == "test_id"
    assert sale.vehicle_id == "test_vehicle_id"
    assert sale.buyer_cpf == "12345678900"
    assert sale.sale_price == 50000.0
    assert sale.payment_code == "test_payment_code"
    assert sale.payment_status == PaymentStatus.PENDING

def test_sale_to_dict():
    sale = Sale(
        id=str(ObjectId()),
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    sale_dict = sale.to_dict()
    assert sale_dict["vehicle_id"] == "test_vehicle_id"
    assert sale_dict["buyer_cpf"] == "12345678900"
    assert sale_dict["sale_price"] == 50000.0
    assert sale_dict["payment_code"] == "test_payment_code"
    assert sale_dict["payment_status"] == "PENDENTE"

def test_sale_from_dict():
    sale_dict = {
        "_id": str(ObjectId()),
        "vehicle_id": "test_vehicle_id",
        "buyer_cpf": "12345678900",
        "sale_price": 50000.0,
        "payment_code": "test_payment_code",
        "payment_status": "PENDENTE",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    sale = Sale.from_dict(sale_dict)
    assert sale.vehicle_id == "test_vehicle_id"
    assert sale.buyer_cpf == "12345678900"
    assert sale.sale_price == 50000.0
    assert sale.payment_code == "test_payment_code"
    assert sale.payment_status == PaymentStatus.PENDING

def test_sale_status_transitions():
    sale = Sale(
        id="test_id",
        vehicle_id="test_vehicle_id",
        buyer_cpf="12345678900",
        sale_price=50000.0,
        payment_code="test_payment_code",
        payment_status=PaymentStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Testa transição PENDING -> PAID
    sale.payment_status = PaymentStatus.PAID
    assert sale.payment_status == PaymentStatus.PAID
    
    # Testa transição PAID -> CANCELED
    sale.payment_status = PaymentStatus.CANCELLED
    assert sale.payment_status == PaymentStatus.CANCELLED
    
    # Testa transição CANCELED -> PENDING
    sale.payment_status = PaymentStatus.PENDING
    assert sale.payment_status == PaymentStatus.PENDING
