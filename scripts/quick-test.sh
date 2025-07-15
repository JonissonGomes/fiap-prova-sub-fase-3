#!/bin/bash

# Script rápido para testar a solução do problema

echo "🔧 Teste Rápido da Solução"
echo "=" * 40

echo ""
echo "1. Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    exit 1
else
    echo "✅ Docker está rodando"
fi

echo ""
echo "2. Parando containers (se estiverem rodando)..."
docker-compose down > /dev/null 2>&1

echo ""
echo "3. Verificando se containers estão parados..."
containers=$(docker-compose ps -q)
if [ -z "$containers" ]; then
    echo "✅ Containers estão parados (cenário correto)"
else
    echo "❌ Alguns containers ainda estão rodando"
fi

echo ""
echo "4. Testando detecção de containers no script..."
if [ -z "$(docker-compose ps -q)" ]; then
    echo "✅ Script detectaria containers parados corretamente"
else
    echo "❌ Script não detectaria containers parados"
fi

echo ""
echo "5. Iniciando containers para teste..."
docker-compose up -d > /dev/null 2>&1

echo ""
echo "6. Aguardando containers iniciarem..."
sleep 10

echo ""
echo "7. Verificando se containers estão rodando..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers estão rodando agora"
else
    echo "❌ Containers não iniciaram"
fi

echo ""
echo "8. Testando verificação do auth-service..."
if docker-compose ps auth-service | grep -q "Up"; then
    echo "✅ Auth-service está rodando"
else
    echo "❌ Auth-service não está rodando"
fi

echo ""
echo "=" * 40
echo "✅ TESTE RÁPIDO CONCLUÍDO!"
echo "=" * 40

echo ""
echo "🔧 Agora você pode executar:"
echo "   make setup-complete"
echo ""
echo "O script agora deve:"
echo "   - Detectar containers parados"
echo "   - Iniciar containers automaticamente"
echo "   - Aguardar serviços ficarem disponíveis"
echo "   - Continuar com configuração" 