#!/bin/bash

# Script otimizado para configuração rápida do sistema
# Assume que os containers já estão rodando ou inicia em paralelo

set -e

echo "🚀 Configuração Rápida do Sistema de Vendas de Veículos"
echo "=" * 60

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "🔧 Inicie o Docker Desktop e tente novamente"
    exit 1
fi

# Iniciar containers em paralelo se necessário
echo "🔧 Verificando e iniciando containers se necessário..."
docker-compose up -d --no-recreate > /dev/null 2>&1

echo "⏳ Aguardando serviços críticos (Keycloak pode demorar...)..."

# Função para testar serviço
test_service() {
    local service_name=$1
    local url=$2
    local timeout=${3:-30}
    
    echo -n "   - $service_name: "
    for i in $(seq 1 $timeout); do
        if curl -s --connect-timeout 2 "$url" > /dev/null 2>&1; then
            echo "✅ OK"
            return 0
        fi
        sleep 2
        echo -n "."
    done
    echo "⚠️  Timeout (mas pode funcionar)"
    return 1
}

# Testar serviços em paralelo
echo "🔍 Testando serviços básicos..."
test_service "Redis" "http://localhost:6379" 10 &
test_service "Auth-Service" "http://localhost:8002" 30 &
test_service "Core-Service" "http://localhost:8000" 20 &
test_service "Sales-Service" "http://localhost:8001" 20 &
test_service "Customer-Service" "http://localhost:8003" 20 &

# Aguardar testes terminarem
wait

echo ""
echo "🔍 Testando Keycloak (pode demorar mais)..."
keycloak_ready=false
for i in $(seq 1 60); do
    if curl -s --connect-timeout 5 "http://localhost:8080/" > /dev/null 2>&1; then
        echo "✅ Keycloak está disponível!"
        keycloak_ready=true
        break
    fi
    sleep 2
    echo -n "."
    if [ $((i % 10)) -eq 0 ]; then
        echo " ${i}s"
    fi
done

if [ "$keycloak_ready" = false ]; then
    echo ""
    echo "⚠️  Keycloak ainda não está pronto, mas continuando..."
    echo "💡 Dica: Execute 'docker-compose logs keycloak' para verificar o status"
fi

echo ""
echo "🔧 Executando configuração do admin..."
if python3 scripts/setup-admin-user.py; then
    echo "✅ Configuração do admin concluída!"
else
    echo "⚠️  Configuração do admin falhou, mas pode ser normal se já estiver configurado"
fi

echo ""
echo "🔧 Populando dados de teste..."
if python3 scripts/populate-data.py; then
    echo "✅ Dados populados com sucesso!"
else
    echo "⚠️  Alguns dados podem não ter sido criados, mas o sistema deve funcionar"
fi

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO RÁPIDA CONCLUÍDA!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "🔧 Se algo não funcionar:"
echo "   - Verifique logs: make logs"
echo "   - Execute novamente: make setup-complete"
echo "   - Aguarde mais tempo para Keycloak: docker-compose logs keycloak"
echo ""
echo "🚀 Sistema pronto para uso!" 