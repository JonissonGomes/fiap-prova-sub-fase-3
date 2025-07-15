from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import Optional

from app.controllers.sale_controller import router as sale_router
from app.infrastructure.mongodb_config import MongoDB
from app.adapters.mongodb_sale_repository import MongoDBSaleRepository
from app.services.sale_service_impl import SaleServiceImpl

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(title="Sales Service API")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização das dependências
repository = None
service = None

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do serviço."""
    return {"status": "healthy"}

async def try_connect_mongodb(max_retries: int = 5, retry_delay: int = 5) -> Optional[MongoDB]:
    """Tenta conectar ao MongoDB com retries."""
    mongodb = MongoDB()
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {max_retries} de conexão com MongoDB...")
            await mongodb.connect()
            return mongodb
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Falha em todas as tentativas de conexão com MongoDB: {str(e)}")
                raise
            logger.warning(f"Falha na tentativa {attempt + 1}. Tentando novamente em {retry_delay} segundos...")
            await asyncio.sleep(retry_delay)
    return None

@app.on_event("startup")
async def startup_event():
    global repository, service
    try:
        logger.info("Iniciando o serviço...")
        # Conecta ao MongoDB com retry
        mongodb = await try_connect_mongodb()
        if not mongodb:
            raise Exception("Não foi possível conectar ao MongoDB após todas as tentativas")
        
        logger.info("Conectado ao MongoDB com sucesso!")
        
        # Inicializa o repositório e o serviço
        repository = MongoDBSaleRepository(
            mongodb.client,
            mongodb.settings.db_name,
            mongodb.settings.collection
        )
        service = SaleServiceImpl(repository)
        logger.info("Serviço inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar o serviço: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar o serviço: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    if repository and repository.client:
        await repository.client.close()
        logger.info("Conexão com MongoDB fechada.")

# Inclui as rotas
app.include_router(sale_router, tags=["sales"]) 