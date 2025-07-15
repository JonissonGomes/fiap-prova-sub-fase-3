import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.vehicle_service import VehicleService
from app.domain.vehicle import Vehicle, VehicleStatus
from datetime import datetime, timezone

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def service(mock_repository):
    return VehicleService(mock_repository)

@pytest.fixture
def mock_vehicle():
    return Vehicle(
        brand="Toyota",
        model="Corolla",
        year=2020,
        color="Preto",
        price=85000.0,
        status=VehicleStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

@pytest.mark.asyncio
async def test_create_vehicle(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.save.return_value = mock_vehicle
    
    # Act
    result = await service.create_vehicle(mock_vehicle)
    
    # Assert
    assert result == mock_vehicle
    mock_repository.save.assert_called_once_with(mock_vehicle)

@pytest.mark.asyncio
async def test_get_vehicle(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_by_id.return_value = mock_vehicle
    
    # Act
    result = await service.get_vehicle("123")
    
    # Assert
    assert result == mock_vehicle
    mock_repository.find_by_id.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_get_vehicle_not_found(service, mock_repository):
    # Arrange
    mock_repository.find_by_id.return_value = None
    
    # Act
    result = await service.get_vehicle("123")
    
    # Assert
    assert result is None
    mock_repository.find_by_id.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_list_vehicles(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_all.return_value = [mock_vehicle]
    
    # Act
    result = await service.list_vehicles()
    
    # Assert
    assert result == [mock_vehicle]
    mock_repository.find_all.assert_called_once()

@pytest.mark.asyncio
async def test_list_vehicles_by_status(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_by_status.return_value = [mock_vehicle]
    
    # Act
    result = await service.list_vehicles_by_status(VehicleStatus.AVAILABLE)
    
    # Assert
    assert result == [mock_vehicle]
    mock_repository.find_by_status.assert_called_once_with(VehicleStatus.AVAILABLE)

@pytest.mark.asyncio
async def test_list_available_vehicles(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_available.return_value = [mock_vehicle]
    
    # Act
    result = await service.list_available_vehicles()
    
    # Assert
    assert result == [mock_vehicle]
    mock_repository.find_available.assert_called_once()

@pytest.mark.asyncio
async def test_update_vehicle(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.update.return_value = mock_vehicle
    
    # Act
    result = await service.update_vehicle(mock_vehicle)
    
    # Assert
    assert result == mock_vehicle
    mock_repository.update.assert_called_once_with(mock_vehicle)

@pytest.mark.asyncio
async def test_delete_vehicle(service, mock_repository):
    # Act
    await service.delete_vehicle("123")
    
    # Assert
    mock_repository.delete.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_update_vehicle_status_to_sold(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_by_id.return_value = mock_vehicle
    mock_repository.update.return_value = mock_vehicle
    
    # Act
    result = await service.update_vehicle_status("123", VehicleStatus.SOLD)
    
    # Assert
    assert result == mock_vehicle
    assert mock_vehicle.status == VehicleStatus.SOLD
    mock_repository.update.assert_called_once_with(mock_vehicle)

@pytest.mark.asyncio
async def test_update_vehicle_status_to_reserved(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_by_id.return_value = mock_vehicle
    mock_repository.update.return_value = mock_vehicle
    
    # Act
    result = await service.update_vehicle_status("123", VehicleStatus.RESERVED)
    
    # Assert
    assert result == mock_vehicle
    assert mock_vehicle.status == VehicleStatus.RESERVED
    mock_repository.update.assert_called_once_with(mock_vehicle)

@pytest.mark.asyncio
async def test_update_vehicle_status_to_available(service, mock_repository):
    # Arrange
    mock_vehicle = Vehicle(
        brand="Toyota",
        model="Corolla",
        year=2020,
        color="Preto",
        price=85000.0,
        status=VehicleStatus.RESERVED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_repository.find_by_id.return_value = mock_vehicle
    mock_repository.update.return_value = mock_vehicle
    
    # Act
    result = await service.update_vehicle_status("123", VehicleStatus.AVAILABLE)
    
    # Assert
    assert result == mock_vehicle
    assert mock_vehicle.status == VehicleStatus.AVAILABLE
    mock_repository.update.assert_called_once_with(mock_vehicle)

@pytest.mark.asyncio
async def test_update_vehicle_status_not_found(service, mock_repository):
    # Arrange
    mock_repository.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Veículo não encontrado"):
        await service.update_vehicle_status("123", VehicleStatus.SOLD)

@pytest.mark.asyncio
async def test_update_vehicle_status_invalid_transition(service, mock_repository, mock_vehicle):
    # Arrange
    mock_repository.find_by_id.return_value = mock_vehicle
    
    # Act & Assert
    with pytest.raises(ValueError, match="Apenas veículos reservados podem ser marcados como disponíveis"):
        await service.update_vehicle_status("123", VehicleStatus.AVAILABLE) 