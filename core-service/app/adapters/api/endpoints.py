from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.domain.vehicle import Vehicle, VehicleCreate, VehicleUpdate, VehicleStatus
from app.domain.vehicle_service import VehicleService
from app.adapters.api.dependencies import get_vehicle_service

router = APIRouter(
    tags=["veículos"],
    responses={
        404: {"description": "Veículo não encontrado"},
        400: {"description": "Requisição inválida"}
    }
)

@router.post(
    "/",
    response_model=Vehicle,
    status_code=status.HTTP_201_CREATED,
    summary="Criar veículo",
    description="Cria um novo veículo com os dados fornecidos. O veículo será criado com status DISPONÍVEL por padrão.",
    responses={
        201: {"description": "Veículo criado com sucesso"},
        400: {"description": "Dados inválidos fornecidos"}
    }
)
async def create_vehicle(vehicle: VehicleCreate, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        return await vehicle_service.create_vehicle(vehicle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/",
    response_model=List[Vehicle],
    summary="Listar veículos",
    description="Retorna uma lista de todos os veículos cadastrados no sistema."
)
async def list_vehicles(vehicle_service: VehicleService = Depends(get_vehicle_service)):
    return await vehicle_service.list_vehicles()

@router.get(
    "/available/",
    response_model=List[Vehicle],
    summary="Listar veículos disponíveis",
    description="Retorna uma lista de veículos com status DISPONÍVEL."
)
async def list_available_vehicles(vehicle_service: VehicleService = Depends(get_vehicle_service)):
    return await vehicle_service.list_vehicles_by_status(VehicleStatus.AVAILABLE)

@router.get(
    "/reserved/",
    response_model=List[Vehicle],
    summary="Listar veículos reservados",
    description="Retorna uma lista de veículos com status RESERVADO."
)
async def list_reserved_vehicles(vehicle_service: VehicleService = Depends(get_vehicle_service)):
    return await vehicle_service.list_vehicles_by_status(VehicleStatus.RESERVED)

@router.get(
    "/sold/",
    response_model=List[Vehicle],
    summary="Listar veículos vendidos",
    description="Retorna uma lista de veículos com status VENDIDO."
)
async def list_sold_vehicles(vehicle_service: VehicleService = Depends(get_vehicle_service)):
    return await vehicle_service.list_vehicles_by_status(VehicleStatus.SOLD)

@router.get(
    "/{vehicle_id}",
    response_model=Vehicle,
    summary="Obter veículo por ID",
    description="Retorna os detalhes de um veículo específico pelo seu ID.",
    responses={
        200: {"description": "Veículo encontrado"},
        404: {"description": "Veículo não encontrado"}
    }
)
async def get_vehicle(vehicle_id: str, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    vehicle = await vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return vehicle

@router.put(
    "/{vehicle_id}",
    response_model=Vehicle,
    summary="Atualizar veículo",
    description="Atualiza os dados de um veículo existente. Não permite alterar o status do veículo.",
    responses={
        200: {"description": "Veículo atualizado com sucesso"},
        404: {"description": "Veículo não encontrado"},
        400: {"description": "Dados inválidos fornecidos"}
    }
)
async def update_vehicle(vehicle_id: str, vehicle_update: VehicleUpdate, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        vehicle = await vehicle_service.get_vehicle(vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")
        
        # Atualiza apenas os campos fornecidos
        update_data = vehicle_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        return await vehicle_service.update_vehicle(vehicle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar veículo",
    description="Remove um veículo do sistema pelo seu ID.",
    responses={
        204: {"description": "Veículo deletado com sucesso"},
        404: {"description": "Veículo não encontrado"}
    }
)
async def delete_vehicle(vehicle_id: str, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        await vehicle_service.delete_vehicle(vehicle_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/{vehicle_id}/mark-as-available",
    response_model=Vehicle,
    summary="Marcar veículo como disponível",
    description="Muda o status de um veículo para DISPONÍVEL. Apenas veículos reservados podem ser marcados como disponíveis.",
    responses={
        200: {"description": "Veículo marcado como disponível"},
        404: {"description": "Veículo não encontrado"},
        400: {"description": "Veículo não pode ser marcado como disponível (já está disponível ou vendido)"}
    }
)
async def mark_vehicle_as_available(vehicle_id: str, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        return await vehicle_service.update_vehicle_status(vehicle_id, VehicleStatus.AVAILABLE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post(
    "/{vehicle_id}/mark-as-reserved",
    response_model=Vehicle,
    summary="Marcar veículo como reservado",
    description="Muda o status de um veículo para RESERVADO. Apenas veículos disponíveis podem ser reservados.",
    responses={
        200: {"description": "Veículo marcado como reservado"},
        404: {"description": "Veículo não encontrado"},
        400: {"description": "Veículo não pode ser reservado (já está reservado ou vendido)"}
    }
)
async def mark_vehicle_as_reserved(vehicle_id: str, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        return await vehicle_service.update_vehicle_status(vehicle_id, VehicleStatus.RESERVED)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 

@router.post(
    "/{vehicle_id}/mark-as-sold",
    response_model=Vehicle,
    summary="Marcar veículo como vendido",
    description="Muda o status de um veículo para VENDIDO. Apenas veículos disponíveis ou reservados podem ser vendidos.",
    responses={
        200: {"description": "Veículo marcado como vendido"},
        404: {"description": "Veículo não encontrado"},
        400: {"description": "Veículo não pode ser vendido (já está vendido ou não está disponível/reservado)"}
    }
)
async def mark_vehicle_as_sold(vehicle_id: str, vehicle_service: VehicleService = Depends(get_vehicle_service)):
    try:
        return await vehicle_service.update_vehicle_status(vehicle_id, VehicleStatus.SOLD)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor") 