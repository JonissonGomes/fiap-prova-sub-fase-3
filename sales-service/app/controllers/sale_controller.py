from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId
import logging
import os

from app.services.sale_service_impl import SaleServiceImpl
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from app.schemas.sale_schema import (
    SaleCreate,
    SaleResponse,
    SaleUpdate,
    PaymentStatus
)
from app.domain.sale import Sale
from app.middleware.auth import get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales", tags=["sales"])

# Configuração do MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "sales_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "sales")

# Cliente MongoDB global
mongodb_client = None

async def get_mongodb_client():
    """Obtém o cliente MongoDB."""
    global mongodb_client
    if mongodb_client is None:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    return mongodb_client

async def get_repository():
    """Obtém o repositório de vendas."""
    client = await get_mongodb_client()
    return MongoDBSaleRepository(client, MONGODB_DB_NAME, MONGODB_COLLECTION)

async def get_service(repository: MongoDBSaleRepository = Depends(get_repository)):
    """Obtém o serviço de vendas."""
    return SaleServiceImpl(repository)

@router.post("/", response_model=SaleResponse)
async def create_sale(
    sale: SaleCreate,
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Cria uma nova venda."""
    try:
        # Cria o objeto de domínio
        domain_sale = Sale(
            id=str(ObjectId()),
            vehicle_id=sale.vehicle_id,
            buyer_cpf=sale.buyer_cpf,
            sale_price=sale.sale_price,
            payment_code=sale.payment_code,
            payment_status=sale.payment_status
        )
        
        # Salva a venda
        created_sale = await service.create_sale(domain_sale)
        
        # Notifica o core-service sobre a mudança de status do veículo
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": created_sale.vehicle_id,
                        "status": "PENDENTE"
                    }
                )
                logger.info(f"Notificação enviada para core-service: veículo {created_sale.vehicle_id} marcado como RESERVADO")
            except Exception as e:
                logger.error(f"Erro ao notificar o core-service: {e}")
                # Não interrompe o fluxo se falhar a notificação
                pass
        
        # Converte para o schema de resposta
        return SaleResponse.from_domain(created_sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Lista todas as vendas."""
    try:
        sales = await service.get_all_sales()
        return [SaleResponse.from_domain(sale) for sale in sales]
    except Exception as e:
        logger.error(f"Erro ao listar vendas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: str,
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Obtém uma venda pelo ID."""
    # Verifica se é um ObjectId válido
    if not ObjectId.is_valid(sale_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    try:
        sale = await service.get_sale(sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        return SaleResponse.from_domain(sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/status/{status}", response_model=List[SaleResponse])
async def get_sales_by_status(
    status: PaymentStatus,
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Lista vendas por status."""
    try:
        sales = await service.get_sales_by_status(status)
        return [SaleResponse.from_domain(sale) for sale in sales]
    except Exception as e:
        logger.error(f"Erro ao listar vendas por status: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/payment/{payment_code}", response_model=SaleResponse)
async def get_sale_by_payment_code(
    payment_code: str,
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Obtém uma venda pelo código de pagamento."""
    try:
        sale = await service.get_sale_by_payment_code(payment_code)
        if not sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        return SaleResponse.from_domain(sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: str,
    sale_update: SaleUpdate,
    current_user: dict = Depends(get_current_user),
    service: SaleServiceImpl = Depends(get_service)
):
    """Atualiza uma venda."""
    if not ObjectId.is_valid(sale_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    try:
        updated_sale = await service.update_sale(sale_id, sale_update)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{sale_id}")
async def delete_sale(
    sale_id: str,
    current_user: dict = Depends(require_role(["ADMIN"])),
    service: SaleServiceImpl = Depends(get_service)
):
    """Remove uma venda."""
    try:
        success = await service.delete_sale(sale_id)
        if not success:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        return {"message": "Venda removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover venda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.patch("/{sale_id}/mark-as-canceled", response_model=SaleResponse)
async def mark_sale_as_canceled(
    sale_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    service: SaleServiceImpl = Depends(get_service)
):
    """Marca uma venda como Cancelada."""
    try:
        updated_sale = await service.update_payment_status(sale_id, PaymentStatus.CANCELLED)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Notifica o serviço principal sobre a mudança de status
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": updated_sale.vehicle_id,
                        "status": PaymentStatus.CANCELLED.value
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao notificar o serviço principal: {e}")
        
        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao marcar venda como cancelada: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.patch("/{sale_id}/mark-as-pending", response_model=SaleResponse)
async def mark_sale_as_pending(
    sale_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    service: SaleServiceImpl = Depends(get_service)
):
    """Marca uma venda como Pendente."""
    try:
        updated_sale = await service.update_payment_status(sale_id, PaymentStatus.PENDING)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Notifica o serviço principal sobre a mudança de status
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": updated_sale.vehicle_id,
                        "status": PaymentStatus.PENDING.value
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao notificar o serviço principal: {e}")
        
        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao marcar venda como pendente: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.patch("/{sale_id}/mark-as-paid", response_model=SaleResponse)
async def mark_sale_as_paid(
    sale_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    service: SaleServiceImpl = Depends(get_service)
):
    """Marca uma venda como Pago."""
    try:
        updated_sale = await service.update_payment_status(sale_id, PaymentStatus.PAID)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Notifica o serviço principal sobre a mudança de status
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": updated_sale.vehicle_id,
                        "status": PaymentStatus.PAID.value
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao notificar o serviço principal: {e}")
        
        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao marcar venda como pago: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.patch("/{sale_id}/payment/confirm", response_model=SaleResponse)
async def confirm_payment(
    sale_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "SALES"])),
    service: SaleServiceImpl = Depends(get_service)
):
    """Confirma o pagamento de uma venda."""
    try:
        updated_sale = await service.update_payment_status(sale_id, PaymentStatus.PAID)
        if not updated_sale:
            raise HTTPException(status_code=404, detail="Venda não encontrada")
        
        # Notifica o serviço principal sobre a mudança de status
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": updated_sale.vehicle_id,
                        "status": "PAGO"
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao notificar o serviço principal: {e}")
        
        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao confirmar pagamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/webhook/payment", response_model=SaleResponse)
async def payment_webhook(
    payment_data: dict,
    service: SaleServiceImpl = Depends(get_service)
):
    """Webhook para atualização de status de pagamento."""
    try:
        logger.info(f"Recebido webhook de pagamento: {payment_data}")
        
        payment_code = payment_data.get("payment_code")
        status = payment_data.get("status")
        vehicle_id = payment_data.get("vehicle_id")

        if not all([payment_code, status, vehicle_id]):
            raise HTTPException(
                status_code=400,
                detail="Dados de pagamento incompletos. São necessários: payment_code, status e vehicle_id"
            )

        # Valida o status
        try:
            logger.info(f"Tentando converter status: {status}")
            payment_status = PaymentStatus(status.upper())
            logger.info(f"Status convertido com sucesso: {payment_status}")
        except ValueError:
            logger.error(f"Status inválido: {status}")
            raise HTTPException(
                status_code=400,
                detail="Status de pagamento inválido. Valores aceitos: PAGO, PENDENTE, CANCELADO"
            )

        # Busca a venda pelo código de pagamento
        logger.info(f"Buscando venda pelo código de pagamento: {payment_code}")
        sale = await service.get_sale_by_payment_code(payment_code)
        if not sale:
            logger.error(f"Venda não encontrada para o código: {payment_code}")
            raise HTTPException(status_code=404, detail="Venda não encontrada para o código de pagamento fornecido")
        
        logger.info(f"Venda encontrada: {sale.id}")

        # Atualiza o status da venda usando o ID
        logger.info(f"Atualizando status da venda {sale.id} para {payment_status}")
        updated_sale = await service.update_payment_status(sale.id, payment_status)
        if not updated_sale:
            logger.error(f"Erro ao atualizar status da venda {sale.id}")
            raise HTTPException(status_code=404, detail="Erro ao atualizar status da venda")

        # Notifica o serviço principal sobre a mudança de status
        logger.info(f"Notificando core-service sobre mudança de status do veículo {vehicle_id}")
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://core-service:8000/vehicles/sale-status",
                    json={
                        "vehicle_id": vehicle_id,
                        "status": payment_status.value
                    }
                )
                logger.info("Notificação enviada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao notificar o serviço principal: {e}")
                # Não interrompe o fluxo se falhar a notificação
                pass

        return SaleResponse.from_domain(updated_sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar webhook de pagamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar webhook de pagamento: {str(e)}"
        ) 