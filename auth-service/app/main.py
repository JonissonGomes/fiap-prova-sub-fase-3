from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import Optional

from app.controllers.auth_controller import router as auth_router, get_auth_service
from app.controllers.rate_limit_controller import router as rate_limit_router
from app.infrastructure.keycloak_config import KeycloakConfig
from app.adapters.mongodb_user_repository import MongoDBUserRepository
from app.services.auth_service import AuthService
from app.middleware.rate_limit import setup_rate_limiting

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="Auth Service API",
    description="Serviço de Autenticação e Autorização com Rate Limiting",
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
keycloak_config = None
user_repository = None
auth_service = None

@app.get("/")
async def root():
    """Endpoint raiz para verificar se o serviço está funcionando."""
    return {"message": "Auth Service is running", "service": "auth-service"}

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do serviço."""
    return {"status": "healthy", "service": "auth-service"}

async def try_connect_mongodb(max_retries=5, delay=5):
    """Tenta conectar ao MongoDB com retry"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://auth-mongodb:27017")
    
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

async def setup_keycloak(max_retries=5, delay=5):
    """Configura o Keycloak com retry"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de configurar o Keycloak")
            keycloak_config = KeycloakConfig()
            await keycloak_config.setup_realm_and_client()
            logger.info("Keycloak configurado com sucesso!")
            return keycloak_config
        except Exception as e:
            logger.warning(f"Erro ao configurar o Keycloak (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                logger.error("Não foi possível configurar o Keycloak após todas as tentativas")
                return None

async def create_default_admin():
    """Cria o usuário administrador padrão se não existir"""
    try:
        from app.domain.user import UserCreate
        
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@vehiclesales.com")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        
        # Verifica se o admin já existe
        if await user_repository.email_exists(admin_email):
            logger.info(f"Usuário admin {admin_email} já existe")
            return
        
        # Cria o usuário admin
        admin_user = UserCreate(
            email=admin_email,
            password=admin_password,
            name="Administrador",
            role="ADMIN",
            status="ACTIVE"
        )
        
        await auth_service.register_user(admin_user)
        logger.info(f"Usuário admin {admin_email} criado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário admin: {e}")

def get_auth_service_dependency():
    """Dependency para obter o serviço de autenticação"""
    return auth_service

@app.on_event("startup")
async def startup_event():
    global mongodb_client, keycloak_config, user_repository, auth_service
    try:
        logger.info("Iniciando o serviço de autenticação...")
        
        # Conecta ao MongoDB com retry
        mongodb_client = await try_connect_mongodb()
        if not mongodb_client:
            raise Exception("Não foi possível conectar ao MongoDB após todas as tentativas")
        
        # Configura o Keycloak com retry
        keycloak_config = await setup_keycloak()
        if not keycloak_config:
            raise Exception("Não foi possível configurar o Keycloak após todas as tentativas")
        
        # Inicializa o repositório e o serviço
        db_name = os.getenv("MONGODB_DB_NAME", "auth_db")
        collection_name = os.getenv("MONGODB_COLLECTION", "users")
        
        user_repository = MongoDBUserRepository(
            mongodb_client,
            db_name,
            collection_name
        )
        
        auth_service = AuthService(user_repository, keycloak_config)
        
        # Cria usuário administrador padrão se não existir
        await create_default_admin()
        
        logger.info("Serviço de autenticação inicializado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o serviço: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar o serviço: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Conexão com MongoDB fechada")

# Substitui a dependency no app
app.dependency_overrides[get_auth_service] = get_auth_service_dependency

# Inclui as rotas
app.include_router(auth_router)
app.include_router(rate_limit_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 