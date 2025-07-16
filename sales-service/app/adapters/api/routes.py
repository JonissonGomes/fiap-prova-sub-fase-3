from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os

from app.controllers.sale_controller import router as sale_router
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from app.services.sale_service_impl import SaleServiceImpl
from app.middleware.auth import get_current_user

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

# Router principal
router = APIRouter()

# Incluir as rotas do controller
router.include_router(sale_router, tags=["sales"])

# Endpoints de gerenciamento do Rate Limiting
@router.get("/rate-limit/stats")
async def get_rate_limit_stats(current_user: dict = Depends(get_current_user)):
    """Retorna estatísticas do rate limiting."""
    if not current_user.get("roles") or "ADMIN" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return {"message": "Rate limiting ativo", "service": "sales-service"}

@router.get("/rate-limit/config")
async def get_rate_limit_config(current_user: dict = Depends(get_current_user)):
    """Retorna configuração do rate limiting."""
    if not current_user.get("roles") or "ADMIN" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return {"limits": {"default": "100/minute"}, "service": "sales-service"}

@router.delete("/rate-limit/reset")
async def reset_rate_limit(current_user: dict = Depends(get_current_user)):
    """Reseta contadores do rate limiting."""
    if not current_user.get("roles") or "ADMIN" not in current_user["roles"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return {"message": "Contadores resetados com sucesso"} 