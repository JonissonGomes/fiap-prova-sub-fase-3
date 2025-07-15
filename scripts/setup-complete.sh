#!/bin/bash

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "🔧 Inicie o Docker Desktop e tente novamente"
    exit 1
fi

# Verificar se os containers estão rodando
if [ -z "$(docker-compose ps -q)" ]; then
    echo "🔧 Containers não estão rodando. Iniciando serviços..."
    docker-compose up -d
    
    echo "⏳ Aguardando serviços iniciarem..."
    sleep 30
    
    # Aguardar Keycloak especificamente
    echo "⏳ Aguardando Keycloak inicializar (pode demorar até 2 minutos)..."
    timeout=120
    elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        # Testa se o Keycloak está respondendo na página principal
        if curl -s --connect-timeout 5 "http://localhost:8080/" > /dev/null 2>&1; then
            echo "✅ Keycloak está disponível!"
            break
        fi
        sleep 10
        elapsed=$((elapsed + 10))
        echo "⏳ Keycloak ainda inicializando... (${elapsed}s/120s)"
    done
    
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Keycloak não iniciou a tempo. Verifique os logs: docker-compose logs keycloak"
        echo "💡 Dica: O Keycloak pode demorar mais na primeira execução. Tente novamente."
        exit 1
    fi
else
    echo "✅ Containers já estão rodando!"
fi

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."

# Verificar se auth-service está rodando e respondendo
if ! curl -f -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "❌ Auth-service não está respondendo!"
    echo "🔧 Aguardando auth-service inicializar..."
    
    timeout=60
    elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if curl -f -s http://localhost:8002/health > /dev/null 2>&1; then
            echo "✅ Auth-service está respondendo!"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
        echo "⏳ Auth-service ainda inicializando... (${elapsed}s)"
    done
    
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Auth-service não iniciou a tempo. Verifique os logs: docker-compose logs auth-service"
        echo "📋 Status do container: $(docker-compose ps auth-service --format table)"
        exit 1
    fi
fi

# Aguardar auth-service estar disponível
echo "⏳ Aguardando auth-service estar disponível..."
timeout=60
elapsed=0

while [ $elapsed -lt $timeout ]; do
    # Testa se o auth-service está respondendo
    if curl -s --connect-timeout 5 "http://localhost:8002/" > /dev/null 2>&1; then
        echo "✅ Auth-service está disponível!"
        break
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo "⏳ Auth-service ainda inicializando... (${elapsed}s/60s)"
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Auth-service não respondeu a tempo. Verifique os logs: docker-compose logs auth-service"
    echo "💡 Dica: Tente executar 'make setup-complete' novamente."
    exit 1
fi

docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 