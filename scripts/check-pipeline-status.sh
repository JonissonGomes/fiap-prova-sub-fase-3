#!/bin/bash

# Script para verificar o status do pipeline CI/CD
# Uso: ./scripts/check-pipeline-status.sh

set -e

echo "🔍 Verificando status do pipeline CI/CD..."

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto"
    exit 1
fi

# Verificar se o git está configurado
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Erro: Repositório Git não configurado"
    exit 1
fi

# Obter informações do repositório
REPO_URL=$(git remote get-url origin)
if [[ $REPO_URL == *"github.com"* ]]; then
    REPO_PATH=$(echo $REPO_URL | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')
    REPO_PATH=$(echo $REPO_PATH | sed 's/\.git$//')
    echo "📦 Repositório: $REPO_PATH"
else
    echo "❌ Erro: Repositório não é do GitHub"
    exit 1
fi

# Verificar branch atual
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Branch atual: $CURRENT_BRANCH"

# Verificar último commit
LAST_COMMIT=$(git log -1 --oneline)
echo "📝 Último commit: $LAST_COMMIT"

# Verificar status do git
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Há mudanças não commitadas"
else
    echo "✅ Repositório limpo"
fi

echo ""
echo "🧪 Executando testes locais..."

# Testar backend services
echo "🔧 Testando serviços backend..."
for service in auth-service core-service customer-service sales-service; do
    if [ -d "$service" ]; then
        echo "  - $service:"
        if [ -d "$service/tests" ]; then
            cd $service
            if python3 -m pytest tests/ -q --tb=no > /dev/null 2>&1; then
                echo "    ✅ Testes passando"
            else
                echo "    ❌ Testes falhando"
            fi
            cd ..
        else
            echo "    ⚠️  Sem testes"
        fi
    fi
done

# Testar frontend
echo "🎨 Testando frontend:"
if [ -d "frontend" ]; then
    cd frontend
    if npm test -- --watchAll=false --passWithNoTests > /dev/null 2>&1; then
        echo "  ✅ Testes passando"
    else
        echo "  ❌ Testes falhando"
    fi
    cd ..
else
    echo "  ⚠️  Diretório frontend não encontrado"
fi

echo ""
echo "🚀 Status do Pipeline:"
echo "📊 GitHub Actions: https://github.com/$REPO_PATH/actions"
echo "📈 Codecov: https://codecov.io/gh/$REPO_PATH"

echo ""
echo "💡 Comandos úteis:"
echo "  - Para forçar deploy: ./scripts/force-deploy.sh"
echo "  - Para ver logs: git log --oneline -10"
echo "  - Para ver status: git status"

# Verificar se há workflows configurados
if [ -d ".github/workflows" ]; then
    echo ""
    echo "📋 Workflows disponíveis:"
    for workflow in .github/workflows/*.yml; do
        if [ -f "$workflow" ]; then
            workflow_name=$(basename "$workflow" .yml)
            echo "  - $workflow_name"
        fi
    done
fi

echo ""
echo "✅ Verificação concluída!" 