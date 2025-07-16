#!/bin/bash

# Script de build para o Render
set -e

echo "🔧 Instalando dependências Python..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Verificar se email-validator foi instalado
echo "🔍 Verificando instalação do email-validator..."
python -c "import email_validator; print('✅ email-validator instalado com sucesso')"

echo "✅ Build concluído!" 