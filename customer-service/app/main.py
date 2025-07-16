from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import Optional

from app.controllers.customer_controller import router as customer_router, get_customer_service
from app.adapters.mongodb_customer_repository import MongoDBCustomerRepository
from app.services.customer_service import CustomerService
from app.middleware.rate_limit import setup_rate_limiting

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Customer Service API",
    description="Serviço de Gerenciamento de Clientes com Rate Limiting",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Rate Limiting
setup_rate_limiting(app)

# Variáveis globais para dependências
mongodb_client = None
customer_repository = None
customer_service = None

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do serviço."""
    return {"status": "healthy", "service": "customer-service"}

async def try_connect_mongodb(max_retries=5, delay=5):
    """Tenta conectar ao MongoDB com retry"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://customer-mongodb:27017")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de conectar ao MongoDB: {mongodb_url}")
            client = AsyncIOMotorClient(mongodb_url)
            # Testa a conexão
            await client.admin.command('ping')
            logger.info("Conectado ao MongoDB com sucesso!")
            return client
        except Exception as e:
            logger.warning(f"Erro ao conectar ao MongoDB (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("Não foi possível conectar ao MongoDB após todas as tentativas")
                return None

@app.on_event("startup")
async def startup_event():
    global mongodb_client, customer_repository, customer_service
    try:
        logger.info("Iniciando o serviço de clientes...")
        
        # Conecta ao MongoDB com retry
        mongodb_client = await try_connect_mongodb()
        if not mongodb_client:
            raise Exception("Não foi possível conectar ao MongoDB após todas as tentativas")
        
        # Inicializa o repositório e o serviço
        db_name = os.getenv("MONGODB_DB_NAME", "customer_db")
        collection_name = os.getenv("MONGODB_COLLECTION", "customers")
        
        customer_repository = MongoDBCustomerRepository(
            mongodb_client,
            db_name,
            collection_name
        )
        
        customer_service = CustomerService(customer_repository)
        
        logger.info("Serviço de clientes inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o serviço: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar o serviço: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de shutdown para limpeza de recursos"""
    global mongodb_client
    try:
        if mongodb_client:
            mongodb_client.close()
            logger.info("Conexão com MongoDB fechada")
    except Exception as e:
        logger.error(f"Erro ao fechar conexões: {e}")

# Implementa a dependency para o customer service
async def get_customer_service_dependency() -> CustomerService:
    if not customer_service:
        raise HTTPException(status_code=500, detail="Serviço de clientes não inicializado")
    return customer_service

# Substitui a dependency no app
app.dependency_overrides[get_customer_service] = get_customer_service_dependency

# Inclui as rotas
app.include_router(customer_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 