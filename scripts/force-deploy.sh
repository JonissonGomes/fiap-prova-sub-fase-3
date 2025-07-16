#!/bin/bash

# Script para forçar deploy ignorando testes falhados
# Uso: ./scripts/force-deploy.sh [branch]

set -e

BRANCH=${1:-master}
COMMIT_MESSAGE="Force deploy - bypass tests"

echo "🚀 Iniciando deploy forçado na branch: $BRANCH"
echo "⚠️  ATENÇÃO: Este deploy irá ignorar testes falhados!"

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto"
    exit 1
fi

# Verificar se o git está limpo
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Erro: Há mudanças não commitadas. Faça commit ou stash antes de continuar."
    exit 1
fi

# Fazer commit vazio para forçar o workflow
echo "📝 Criando commit vazio para forçar o workflow..."
git commit --allow-empty -m "$COMMIT_MESSAGE"

# Fazer push para a branch especificada
echo "📤 Fazendo push para $BRANCH..."
git push origin $BRANCH

echo "✅ Deploy forçado iniciado!"
echo "🔍 Acompanhe o progresso em: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')/actions" 