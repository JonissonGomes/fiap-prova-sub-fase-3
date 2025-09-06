#!/bin/bash

# Script para popular o banco de dados com dados de exemplo
# Autor: Sistema FIAP III
# Data: $(date)

echo "🚀 Iniciando população do banco de dados..."
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    echo "❌ Erro: Execute este script a partir da pasta backend"
    exit 1
fi

# Verificar se o Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Erro: Node.js não está instalado"
    exit 1
fi

# Verificar se as dependências estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

echo ""
echo "Escolha uma opção:"
echo "1) População básica (dados mínimos)"
echo "2) População abrangente (dados moderados)"
echo "3) População avançada (dados completos - RECOMENDADO)"
echo "4) Apenas criar admin padrão"
echo ""
read -p "Digite sua escolha (1-4): " choice

case $choice in
    1)
        echo "📋 Executando população básica..."
        node scripts/populate-data.js
        ;;
    2)
        echo "📊 Executando população abrangente..."
        node scripts/populate-comprehensive-data.js
        ;;
    3)
        echo "🎯 Executando população avançada..."
        node scripts/populate-advanced-data.js
        ;;
    4)
        echo "👑 Criando apenas admin padrão..."
        node -e "
        require('dotenv').config({ path: './config.env' });
        const { connectDatabase } = require('./src/config/database');
        const { createDefaultAdmin } = require('./src/utils/seed');
        
        (async () => {
            try {
                await connectDatabase();
                await createDefaultAdmin();
                console.log('✅ Admin criado com sucesso');
                process.exit(0);
            } catch (error) {
                console.error('❌ Erro:', error);
                process.exit(1);
            }
        })();
        "
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Processo concluído!"
echo "🌐 Você pode agora iniciar o servidor e acessar o sistema"
echo "📝 Execute: npm start"
