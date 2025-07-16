#!/bin/bash

# Script de build para o Render
set -e

echo "🔧 Iniciando build do auth-service..."
echo "📋 Diretório atual: $(pwd)"
echo "📋 Conteúdo do diretório:"
ls -la

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Limpar cache do pip
echo "🧹 Limpando cache do pip..."
python -m pip cache purge

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt não encontrado!"
    echo "📋 Conteúdo atual:"
    ls -la
    exit 1
fi

# Instalar email-validator primeiro (forçar)
echo "📧 Instalando email-validator..."
python -m pip install --no-cache-dir --force-reinstall email-validator==2.1.0

# Verificar se email-validator foi instalado
echo "🔍 Verificando instalação do email-validator..."
python -c "import email_validator; print('✅ email-validator instalado com sucesso - versão:', email_validator.__version__)"

# Instalar pydantic com suporte a email (forçar)
echo "📋 Instalando pydantic[email]..."
python -m pip install --no-cache-dir --force-reinstall "pydantic[email]==2.5.0"

# Verificar se pydantic consegue usar email-validator
echo "🔍 Verificando integração Pydantic + email-validator..."
python -c "
from pydantic import BaseModel, EmailStr
class TestModel(BaseModel):
    email: EmailStr
print('✅ Pydantic EmailStr funcionando corretamente')
"

# Instalar outras dependências
echo "📦 Instalando outras dependências..."
python -m pip install --no-cache-dir -r requirements.txt

# Verificação final
echo "🔍 Verificação final..."
python -c "
import email_validator
from pydantic import BaseModel, EmailStr
print('✅ email-validator versão:', email_validator.__version__)
print('✅ Pydantic EmailStr funcionando')
"

echo "✅ Build do auth-service concluído com sucesso!" 