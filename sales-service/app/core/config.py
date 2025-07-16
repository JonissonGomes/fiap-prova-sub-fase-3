import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sales Service"
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "sales_db")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "sales")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    
    # Keycloak
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "vehicle-sales")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "vehicle-sales-app")
    
    # Core Service
    CORE_SERVICE_URL: str = os.getenv("CORE_SERVICE_URL", "http://localhost:8000")
    
    class Config:
        case_sensitive = True

settings = Settings() 