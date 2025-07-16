#!/bin/bash

# Script de build para o Render
set -e

echo "🔧 Iniciando build do customer-service..."

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Limpar cache do pip
echo "🧹 Limpando cache do pip..."
pip cache purge

# Instalar email-validator primeiro
echo "📧 Instalando email-validator..."
pip install --no-cache-dir email-validator==2.1.0

# Instalar pydantic com suporte a email
echo "📋 Instalando pydantic[email]..."
pip install --no-cache-dir "pydantic[email]==2.5.0"

# Instalar dependências de produção
echo "📦 Instalando dependências de produção..."
if [ -f "requirements-prod.txt" ]; then
    pip install --no-cache-dir -r requirements-prod.txt
else
    pip install --no-cache-dir -r requirements.txt
fi

# Verificar se email-validator foi instalado
echo "🔍 Verificando instalação do email-validator..."
python -c "import email_validator; print('✅ email-validator instalado com sucesso - versão:', email_validator.__version__)"

# Verificar se pydantic consegue usar email-validator
echo "🔍 Verificando integração Pydantic + email-validator..."
python -c "
from pydantic import BaseModel, EmailStr
class TestModel(BaseModel):
    email: EmailStr
print('✅ Pydantic EmailStr funcionando corretamente')
"

echo "✅ Build do customer-service concluído com sucesso!" 