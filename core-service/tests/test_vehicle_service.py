import pytest
from unittest.mock import Mock
from app.domain.vehicle import Vehicle, VehicleStatus
from app.adapters.service.vehicle_service import VehicleServiceImpl

@pytest.fixture
def mock_repository():
    mock = Mock()
    mock.save = Mock()
    mock.find_by_id = Mock()
    mock.find_all = Mock()
    mock.find_by_status = Mock()
    mock.delete = Mock()
    return mock

@pytest.fixture
def vehicle_service(mock_repository):
    return VehicleServiceImpl(mock_repository)

def test_create_vehicle(vehicle_service, mock_repository):
    # Arrange
    vehicle_data = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0
    }
    vehicle = Vehicle(**vehicle_data)
    mock_repository.save.return_value = vehicle

def test_get_vehicle(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    vehicle_data = {
        "id": vehicle_id,
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2022,
        "color": "Prata",
        "price": 100000.0,
        "status": VehicleStatus.AVAILABLE
    }
    mock_repository.find_by_id.return_value = Vehicle(**vehicle_data)

    # Act
    result = vehicle_service.get_vehicle(vehicle_id)

    # Assert
    assert result.id == vehicle_id
    assert result.brand == "Toyota"
    assert result.model == "Corolla"
    assert result.year == 2022
    assert result.color == "Prata"
    assert result.price == 100000.0
    assert result.status == VehicleStatus.AVAILABLE
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)

def test_get_vehicle_not_found(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    mock_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Veículo não encontrado"):
        vehicle_service.get_vehicle(vehicle_id)
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)

def test_get_all_vehicles(vehicle_service, mock_repository):
    # Arrange
    vehicles = [
        Vehicle(
            id="1",
            brand="Toyota",
            model="Corolla",
            year=2022,
            color="Prata",
            price=100000.0,
            status=VehicleStatus.AVAILABLE
        ),
        Vehicle(
            id="2",
            brand="Honda",
            model="Civic",
            year=2023,
            color="Preto",
            price=110000.0,
            status=VehicleStatus.SOLD
        )
    ]
    mock_repository.find_all.return_value = vehicles

    # Act
    result = vehicle_service.get_all_vehicles()

    # Assert
    assert len(result) == 2
    assert result[0].id == "1"
    assert result[1].id == "2"
    mock_repository.find_all.assert_called_once()

def test_get_available_vehicles(vehicle_service, mock_repository):
    # Arrange
    vehicles = [
        Vehicle(
            id="1",
            brand="Toyota",
            model="Corolla",
            year=2022,
            color="Prata",
            price=100000.0,
            status=VehicleStatus.AVAILABLE
        ),
        Vehicle(
            id="2",
            brand="Honda",
            model="Civic",
            year=2023,
            color="Preto",
            price=110000.0,
            status=VehicleStatus.SOLD
        )
    ]
    mock_repository.find_all.return_value = vehicles

    # Act
    result = vehicle_service.get_all_vehicles()

    # Assert
    assert len(result) == 2
    assert result[0].id == "1"
    assert result[1].id == "2"
    assert result[0].status == VehicleStatus.AVAILABLE
    assert result[1].status == VehicleStatus.SOLD

    mock_repository.find_all.assert_called_once()

def test_update_vehicle(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.SOLD
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Act & Assert
    with pytest.raises(ValueError, match="Não é possível atualizar um veículo que não está disponível"):
        vehicle_service.update_vehicle(vehicle_id, brand="Honda")
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called()

def test_update_vehicle_not_available(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.SOLD
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Act & Assert
    with pytest.raises(ValueError, match="Não é possível atualizar um veículo que não está disponível"):
        vehicle_service.update_vehicle(vehicle_id, brand="Honda")
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called()

def test_delete_vehicle(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.AVAILABLE
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Act
    vehicle_service.delete_vehicle(vehicle_id)

    # Assert
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.delete.assert_called_once_with(vehicle_id)

def test_mark_vehicle_as_sold(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.SOLD
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Assert
    with pytest.raises(ValueError, match="Veículo não está disponível para venda"):
        vehicle_service.mark_vehicle_as_pending(vehicle_id)
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called()

def test_mark_vehicle_as_sold_already_sold(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.SOLD
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Assert
    with pytest.raises(ValueError, match="Veículo não está disponível para venda"):
        vehicle_service.mark_vehicle_as_pending(vehicle_id)
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called() 

def test_mark_vehicle_as_pending(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.AVAILABLE
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Assert
    with pytest.raises(ValueError, match="Veículo não está disponível para venda"):
        vehicle_service.mark_vehicle_as_pending(vehicle_id)
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called() 

def test_mark_vehicle_as_pending_already_pending(vehicle_service, mock_repository):
    # Arrange
    vehicle_id = "1"
    existing_vehicle = Vehicle(
        id=vehicle_id,
        brand="Toyota",
        model="Corolla",
        year=2022,
        color="Prata",
        price=100000.0,
        status=VehicleStatus.RESERVED
    )
    mock_repository.find_by_id.return_value = existing_vehicle

    # Act & Assert
    with pytest.raises(ValueError, match="Veículo não está disponível para venda"):
        vehicle_service.mark_vehicle_as_pending(vehicle_id)
    mock_repository.find_by_id.assert_called_once_with(vehicle_id)
    mock_repository.save.assert_not_called() 