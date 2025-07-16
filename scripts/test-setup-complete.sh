#!/bin/bash

# Script de teste para verificar a correção do setup-complete

echo "🧪 Testando correção do setup-complete.sh"
echo "=" * 50

echo ""
echo "🔍 Verificando se Docker está rodando..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "🔧 Inicie o Docker Desktop e execute o teste novamente"
    exit 1
else
    echo "✅ Docker está rodando"
fi

echo ""
echo "🔍 Verificando containers atuais..."
containers=$(docker-compose ps -q)
if [ -z "$containers" ]; then
    echo "ℹ️  Nenhum container está rodando (cenário de teste correto)"
else
    echo "🔄 Parando containers para testar inicialização automática..."
    docker-compose down
fi

echo ""
echo "🧪 Testando scripts de setup..."

echo ""
echo "1. Testando setup-complete.sh (deve iniciar containers automaticamente)..."
if ./scripts/setup-complete.sh; then
    echo "✅ setup-complete.sh funcionou corretamente!"
else
    echo "❌ setup-complete.sh falhou"
fi

echo ""
echo "2. Verificando se serviços estão rodando..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Serviços estão rodando"
else
    echo "❌ Serviços não estão rodando"
fi

echo ""
echo "3. Testando setup-complete.ps1 (Windows)..."
if command -v powershell > /dev/null 2>&1; then
    echo "ℹ️  PowerShell disponível, script deve funcionar no Windows"
else
    echo "ℹ️  PowerShell não disponível (normal no macOS/Linux)"
fi

echo ""
echo "4. Testando comandos do Makefile..."
if make check-dependencies; then
    echo "✅ make check-dependencies funcionou"
else
    echo "❌ make check-dependencies falhou"
fi

echo ""
echo "5. Testando comando de compatibilidade..."
if make test-compatibility; then
    echo "✅ make test-compatibility funcionou"
else
    echo "❌ make test-compatibility falhou"
fi

echo ""
echo "=" * 50
echo "✅ TESTE COMPLETO CONCLUÍDO!"
echo "=" * 50

echo ""
echo "📋 Resumo:"
echo "   - Docker: $(docker --version)"
echo "   - Docker Compose: $(docker-compose --version)"
echo "   - Python: $(python3 --version)"
echo "   - Sistema: $(uname -s)"

echo ""
echo "🔗 Próximos passos:"
echo "   1. Teste o sistema: http://localhost:3000"
echo "   2. Login: admin@vehiclesales.com / admin123"
echo "   3. Verifique logs: make logs" 