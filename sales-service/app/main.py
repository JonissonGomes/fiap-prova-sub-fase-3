from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import json
import os

from app.adapters.api.routes import router
from app.core.config import settings
from app.middleware.rate_limit import setup_rate_limiting

app = FastAPI(
    title="Sales Service",
    description="API para gerenciamento de vendas de veículos com Rate Limiting",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
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
    return {"status": "healthy", "service": "sales-service"}

# Carrega o arquivo openapi.json
def load_openapi_json():
    openapi_path = os.path.join(os.path.dirname(__file__), "adapters", "api", "openapi.json")
    with open(openapi_path, "r") as f:
        return json.load(f)

# Configuração do Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Sales Service API - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return load_openapi_json()

# Inclui as rotas da API
app.include_router(router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 