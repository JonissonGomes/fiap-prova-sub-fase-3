#!/bin/bash

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 

# Script para popular dados similares a dados reais
# Executa o script Python de população de dados dentro do Docker

set -e

echo "🚀 Iniciando população de dados..."

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
    echo "   Ou execute 'docker-compose up -d' para iniciar todos os serviços."
    exit 1
fi

echo ""
echo "🎯 Todos os serviços estão funcionando. Iniciando população..."
echo ""

# Copia o script Python para o container e executa
echo "🐳 Executando script de população dentro do container..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias no container
    pip install httpx --quiet
    
    # Cria o script Python temporário
    cat > /tmp/populate_data.py << 'EOF'
$(cat "$(dirname "$0")/populate-data.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/populate_data.py
    
    # Remove o arquivo temporário
    rm -f /tmp/populate_data.py
"

echo ""
echo "✅ População de dados concluída!"
echo ""
echo "⚠️  PROBLEMA CONHECIDO: Sistema de autenticação"
echo "   O sistema atual requer autenticação para criar dados."
echo "   O usuário admin deve ser criado manualmente no Keycloak."
echo ""
echo "🔧 SOLUÇÃO TEMPORÁRIA:"
echo "   1. Acesse o Keycloak: http://localhost:8080/admin"
echo "   2. Login: admin / admin123"
echo "   3. Vá para Users > Add User"
echo "   4. Crie um usuário com email: admin@vehiclesales.com"
echo "   5. Defina senha: admin123"
echo "   6. Atribua role: ADMIN"
echo ""
echo "🔗 Acesse os serviços:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo ""
echo "👤 Usuário admin (criar manualmente):"
echo "   - Email: admin@vehiclesales.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Para testar conectividade sem autenticação:"
echo "   - Execute: make test-populate-data"
echo "" 