#!/bin/bash

# Script de configuração automática de ambiente
# Uso: ./scripts/setup-env.sh [development|staging|production]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de utilidade
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Definir ambiente
ENVIRONMENT=${1:-development}

if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "Ambiente inválido. Use: development, staging ou production"
    exit 1
fi

log_info "Configurando ambiente: $ENVIRONMENT"

# Criar diretório de scripts se não existir
mkdir -p scripts

# Criar arquivos de ambiente se não existirem
create_env_files() {
    local env=$1
    
    log_info "Criando arquivos de ambiente para: $env"
    
    # Arquivo .env principal
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Configuração do ambiente
ENVIRONMENT=$env
NODE_ENV=$env

# Serviços
AUTH_SERVICE_URL=http://localhost:8002
CORE_SERVICE_URL=http://localhost:8000
SALES_SERVICE_URL=http://localhost:8001
CUSTOMER_SERVICE_URL=http://localhost:8003
FRONTEND_URL=http://localhost:3000

# Keycloak
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=T14LidpfzazUfpvn6GsrlDyGooT8p0s6
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
MONGODB_URL=mongodb://localhost:27017
AUTH_MONGODB_URL=mongodb://localhost:27021
CORE_MONGODB_URL=mongodb://localhost:27019
SALES_MONGODB_URL=mongodb://localhost:27018
CUSTOMER_MONGODB_URL=mongodb://localhost:27020

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL=INFO
EOF
        log_success "Arquivo .env criado"
    fi
    
    # Arquivo .env.development
    if [ ! -f ".env.development" ]; then
        cat > .env.development << EOF
# Configuração para desenvolvimento
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs para desenvolvimento
AUTH_SERVICE_URL=http://localhost:8002
CORE_SERVICE_URL=http://localhost:8000
SALES_SERVICE_URL=http://localhost:8001
CUSTOMER_SERVICE_URL=http://localhost:8003
FRONTEND_URL=http://localhost:3000

# Keycloak desenvolvimento
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=T14LidpfzazUfpvn6GsrlDyGooT8p0s6
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB para desenvolvimento
MONGODB_URL=mongodb://localhost:27017
AUTH_MONGODB_URL=mongodb://localhost:27021
CORE_MONGODB_URL=mongodb://localhost:27019
SALES_MONGODB_URL=mongodb://localhost:27018
CUSTOMER_MONGODB_URL=mongodb://localhost:27020

# Redis para desenvolvimento
REDIS_URL=redis://localhost:6379

# JWT para desenvolvimento
JWT_SECRET_KEY=dev-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
EOF
        log_success "Arquivo .env.development criado"
    fi
    
    # Arquivo .env.production
    if [ ! -f ".env.production" ]; then
        cat > .env.production << EOF
# Configuração para produção
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# URLs para produção (ajustar conforme necessário)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003
FRONTEND_URL=http://frontend:3000

# Keycloak produção
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=CHANGE-ME-IN-PRODUCTION
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=CHANGE-ME-IN-PRODUCTION

# MongoDB para produção
MONGODB_URL=mongodb://mongodb:27017
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Redis para produção
REDIS_URL=redis://redis:6379

# JWT para produção
JWT_SECRET_KEY=CHANGE-ME-IN-PRODUCTION
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
EOF
        log_success "Arquivo .env.production criado"
    fi
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    if [ -f ".env.$env" ]; then
        log_info "Copiando configuração para .env"
        cp ".env.$env" ".env"
        log_success "Arquivo .env atualizado com configuração de $env"
    fi
}

# Gerar secrets seguros
generate_secrets() {
    local env=$1
    
    if [ "$env" = "production" ]; then
        log_warning "Para produção, recomenda-se gerar secrets únicos:"
        echo "  JWT_SECRET_KEY: $(openssl rand -hex 32)"
        echo "  KEYCLOAK_CLIENT_SECRET: $(openssl rand -hex 24)"
        echo ""
        echo "Atualize os arquivos .env com estes valores antes do deploy!"
    fi
}

# Criar diretório docs se não existir
create_docs_dir() {
    mkdir -p docs
    log_success "Diretório docs criado"
}

# Executar configuração
main() {
    echo "================================================"
    echo "🚀 Setup do Sistema de Vendas de Veículos"
    echo "================================================"
    echo ""
    
    # Criar arquivos de ambiente se não existirem
    create_env_files "$ENVIRONMENT"
    
    # Criar diretório docs
    create_docs_dir
    
    # Copiar arquivos de ambiente
    copy_env_files "$ENVIRONMENT"
    
    # Gerar secrets se necessário
    generate_secrets "$ENVIRONMENT"
    
    echo ""
    echo "================================================"
    echo "✅ Configuração concluída para: $ENVIRONMENT"
    echo "================================================"
    echo ""
    echo "Próximos passos:"
    echo "1. Revisar os arquivos .env criados"
    echo "2. Atualizar secrets em produção"
    echo "3. Validar configuração: make validate-env"
    echo "4. Executar: make setup && make up"
    echo "5. Verificar: make status"
    echo ""
    echo "Documentação disponível em:"
    echo "- README.md"
    echo "- docs/ARCHITECTURE.md"
    echo "- docs/DEPLOYMENT.md"
    echo "- docs/API_DOCUMENTATION.md"
    echo "- docs/ENVIRONMENT_VARIABLES.md"
    echo ""
}

# Executar função principal
main "$@"