#!/bin/bash

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 

# Script de teste para verificar se o sistema de população de dados funciona
# Testa se o script pode ser executado dentro do container

set -e

echo "🧪 Testando sistema de população de dados..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

echo "🐳 Testando se o container auth-service está funcionando..."

# Verifica se o container auth-service está rodando
if ! docker-compose ps auth-service | grep -q "Up"; then
    echo "❌ Container auth-service não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Container auth-service está rodando!"

echo "🔍 Testando instalação de dependências no container..."

# Testa se pode instalar httpx no container
docker-compose exec -T auth-service bash -c "
    echo '📦 Instalando httpx...'
    pip install httpx --quiet
    echo '✅ httpx instalado com sucesso!'
    
    echo '🐍 Testando importação do httpx...'
    python3 -c 'import httpx; print(\"✅ httpx importado com sucesso!\")'
    
    echo '🔗 Testando conectividade com serviços...'
    python3 -c '
import httpx
import asyncio

async def test_connectivity():
    services = {
        \"auth\": \"http://auth-service:8002\",
        \"core\": \"http://core-service:8000\", 
        \"sales\": \"http://sales-service:8001\",
        \"customer\": \"http://customer-service:8003\"
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f\"{url}/health\", timeout=5)
                if response.status_code == 200:
                    print(f\"✅ {service_name.upper()} Service: OK\")
                else:
                    print(f\"❌ {service_name.upper()} Service: Error {response.status_code}\")
            except Exception as e:
                print(f\"❌ {service_name.upper()} Service: {e}\")

asyncio.run(test_connectivity())
'
"

echo ""
echo "✅ Teste de população de dados concluído com sucesso!"
echo ""
echo "🚀 Para popular dados reais, execute:"
echo "   make populate-data"
echo ""
echo "🧹 Para popular dados limpos (limpa bancos antes), execute:"
echo "   make populate-data-clean" 