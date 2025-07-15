from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.api.endpoints import router
from app.middleware.rate_limit import setup_rate_limiting

app = FastAPI(
    title="Vehicle API",
    description="API de Gerenciamento de Veículos com Rate Limiting",
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do serviço."""
    return {"status": "healthy", "service": "core-service"}

# Inclui as rotas
app.include_router(router, prefix="/vehicles", tags=["vehicles"]) 