from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

class MongoDBSettings(BaseSettings):
    """Configurações do MongoDB."""
    url: str = os.getenv("MONGODB_URL", "mongodb://sales-mongodb:27017")
    db_name: str = os.getenv("MONGODB_DB_NAME", "sales_db")
    collection: str = os.getenv("MONGODB_COLLECTION", "sales")

    class Config:
        env_prefix = "MONGODB_"
        env_file = ".env"

class MongoDB:
    """Classe para gerenciar a conexão com o MongoDB."""
    def __init__(self):
        self.settings = MongoDBSettings()
        self.client = None

    async def connect(self):
        """Estabelece conexão com o MongoDB."""
        try:
            print(f"Conectando ao MongoDB em: {self.settings.url}")
            self.client = AsyncIOMotorClient(self.settings.url)
            # Testa a conexão
            await self.client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise Exception(f"Erro ao conectar ao MongoDB: {str(e)}")

    async def disconnect(self):
        """Fecha a conexão com o MongoDB."""
        if self.client:
            self.client.close() 