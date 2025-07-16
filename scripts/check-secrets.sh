#!/bin/bash

# Script para verificar se as variáveis de ambiente necessárias estão configuradas
# Uso: ./scripts/check-secrets.sh

set -e

echo "🔍 Verificando configuração das variáveis de ambiente..."

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

echo ""
echo "🔧 Variáveis necessárias para o deploy:"
echo ""

echo "📋 Render Web Service:"
echo "  - RENDER_API_KEY: API Key do Render"
echo "  - RENDER_SERVICE_ID: ID do Web Service no Render"
echo ""

echo "🔗 Links úteis:"
echo "  - GitHub Secrets: https://github.com/$REPO_PATH/settings/secrets/actions"
echo "  - Render API Keys: https://dashboard.render.com/account/api-keys"
echo "  - Render Web Services: https://dashboard.render.com/web"
echo ""

echo "📝 Como configurar:"
echo "1. Acesse: https://github.com/$REPO_PATH/settings/secrets/actions"
echo "2. Clique em 'New repository secret'"
echo "3. Adicione cada variável com seu respectivo valor"
echo ""

echo "🚀 Como criar Web Service no Render:"
echo "1. Acesse: https://dashboard.render.com/web"
echo "2. Clique em 'New +' > 'Web Service'"
echo "3. Conecte seu repositório GitHub"
echo "4. Configure o build e start commands"
echo "5. Configure as variáveis de ambiente"
echo "6. Copie o Service ID para o GitHub Secret"
echo ""

echo "✅ Verificação concluída!"
echo ""
echo "💡 Dica: Após configurar as variáveis, faça push para a branch master/main para acionar o deploy automático." 