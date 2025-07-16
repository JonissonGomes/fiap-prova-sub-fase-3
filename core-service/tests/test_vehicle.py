import pytest
from datetime import datetime, timezone
from app.domain.vehicle import Vehicle, VehicleStatus

def test_create_vehicle():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.brand == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.year == 2022
    assert vehicle.color == "Prata"
    assert vehicle.price == 100000.0
    assert vehicle.status == VehicleStatus.AVAILABLE

def test_create_vehicle_with_id():
    # Arrange
    vehicle_data = {
        "id": "1",
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.id == "1"
    assert vehicle.brand == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.year == 2022
    assert vehicle.color == "Prata"
    assert vehicle.price == 100000.0
    assert vehicle.status == VehicleStatus.AVAILABLE

def test_create_vehicle_with_dates():
    # Arrange
    now = datetime.now(timezone.utc)
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE,
        "created_at": now,
        "updated_at": now
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.created_at == now
    assert vehicle.updated_at == now

def test_validate_year_valid():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.year == 2022

def test_validate_year_invalid():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 1800,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.year < 1886

def test_validate_price_valid():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.price == 100000.0

def test_validate_price_invalid():
       # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }

    # Act
    vehicle = Vehicle(**vehicle_data)

    # Assert
    assert vehicle.price > 0

def test_mark_as_sold():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }
    vehicle = Vehicle(**vehicle_data)

    # Act
    vehicle.mark_as_sold()

    # Assert
    assert vehicle.status == VehicleStatus.SOLD
    assert vehicle.updated_at is not None

def test_mark_as_sold_already_sold():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.SOLD
    }
    vehicle = Vehicle(**vehicle_data)

    # Act & Assert
    with pytest.raises(ValueError, match="Veículo já está vendido"):
        vehicle.mark_as_sold()

def test_mark_as_pending():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }
    vehicle = Vehicle(**vehicle_data)

    # Act
    vehicle.mark_as_pending()

    # Assert
    assert vehicle.status == VehicleStatus.RESERVED
    assert vehicle.updated_at is not None

def test_mark_as_pending_already_pending():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.RESERVED
    }
    vehicle = Vehicle(**vehicle_data)

    # Act & Assert
    with pytest.raises(ValueError, match="Veículo já está reservado"):
        vehicle.mark_as_pending()

def test_update():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }
    vehicle = Vehicle(**vehicle_data)

    # Act
    vehicle.update(brand="Honda", model="Civic")

    # Assert
    assert vehicle.brand == "Honda"
    assert vehicle.model == "Civic"
    assert vehicle.updated_at is not None

def test_mark_as_sold_reserved():
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.RESERVED
    }
    vehicle = Vehicle(**vehicle_data)

    # Act
    vehicle.mark_as_sold()

    # Assert
    assert vehicle.status == VehicleStatus.SOLD
    assert vehicle.updated_at is not None 