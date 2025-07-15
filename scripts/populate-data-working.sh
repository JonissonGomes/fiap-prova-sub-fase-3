#!/bin/bash

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=("auth:8002" "core:8000" "sales:8001" "customer:8003")
all_running=true

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ ${name^^} Service: OK"
    else
        echo "❌ ${name^^} Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Executa o script Python dentro do container
echo "🐳 Executando script de população funcional..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_working.py << 'EOF'
$(cat "$(dirname "$0")/populate-data-working.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_working.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_working.py
"

echo ""
echo "✅ População de dados funcional concluída!"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo ""
echo "🔐 Login do admin:"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo "" 