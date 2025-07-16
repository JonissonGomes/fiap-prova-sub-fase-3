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
# Configurações do Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
KC_DB=dev-file
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=BCzhpesgtiAQENgLRuO2tlsLBdUPPMTv

# Configurações do Redis
REDIS_URL=redis://redis:6379

# Configurações do Auth Service
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB_NAME=auth_db
AUTH_MONGODB_COLLECTION=users
AUTH_SERVICE_URL=http://auth-service:8002

# Configurações do Core Service
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB_NAME=core_db
CORE_MONGODB_COLLECTION=vehicles

# Configurações do Sales Service  
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB_NAME=sales_db
SALES_MONGODB_COLLECTION=sales
CORE_SERVICE_URL=http://core-service:8000

# Configurações do Customer Service
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB_NAME=customer_db
CUSTOMER_MONGODB_COLLECTION=customers
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Configurações do Payment Service
PAYMENT_MONGODB_URL=mongodb://payment-mongodb:27017
PAYMENT_MONGODB_DB_NAME=payment_db
PAYMENT_MONGODB_COLLECTION=payments

# Configurações do Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CORE_SERVICE_URL=http://localhost:8000
REACT_APP_SALES_SERVICE_URL=http://localhost:8001
REACT_APP_AUTH_SERVICE_URL=http://localhost:8002
REACT_APP_CUSTOMER_SERVICE_URL=http://localhost:8003
REACT_APP_APP_NAME="Sistema de Vendas de Veículos"
REACT_APP_ENABLE_AUTH=true
REACT_APP_RETRY_ATTEMPTS=3
REACT_APP_RETRY_DELAY=1000
CHOKIDAR_USEPOLLING=true
EOF
        log_success "Arquivo .env criado"
    fi
    
    # Arquivo .env.development
    if [ ! -f ".env.development" ]; then
        cat > .env.development << EOF
# Configurações do Keycloak (Desenvolvimento)
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
KC_DB=dev-file
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=BCzhpesgtiAQENgLRuO2tlsLBdUPPMTv

# Configurações do Redis (Desenvolvimento)
REDIS_URL=redis://redis:6379

# Configurações do Auth Service (Desenvolvimento)
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB_NAME=auth_db
AUTH_MONGODB_COLLECTION=users
AUTH_SERVICE_URL=http://auth-service:8002

# Configurações do Core Service (Desenvolvimento)
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB_NAME=core_db
CORE_MONGODB_COLLECTION=vehicles

# Configurações do Sales Service (Desenvolvimento)
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB_NAME=sales_db
SALES_MONGODB_COLLECTION=sales
CORE_SERVICE_URL=http://core-service:8000

# Configurações do Customer Service (Desenvolvimento)
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB_NAME=customer_db
CUSTOMER_MONGODB_COLLECTION=customers
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Configurações do Payment Service (Desenvolvimento)
PAYMENT_MONGODB_URL=mongodb://payment-mongodb:27017
PAYMENT_MONGODB_DB_NAME=payment_db
PAYMENT_MONGODB_COLLECTION=payments

# Configurações do Frontend (Desenvolvimento)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CORE_SERVICE_URL=http://localhost:8000
REACT_APP_SALES_SERVICE_URL=http://localhost:8001
REACT_APP_AUTH_SERVICE_URL=http://localhost:8002
REACT_APP_CUSTOMER_SERVICE_URL=http://localhost:8003
REACT_APP_APP_NAME="Sistema de Vendas de Veículos"
REACT_APP_ENABLE_AUTH=true
REACT_APP_RETRY_ATTEMPTS=3
REACT_APP_RETRY_DELAY=1000
CHOKIDAR_USEPOLLING=true
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
AUTH_MONGODB_DB_NAME=auth_db
AUTH_MONGODB_COLLECTION=users
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB_NAME=core_db
CORE_MONGODB_COLLECTION=vehicles
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB_NAME=sales_db
SALES_MONGODB_COLLECTION=sales
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB_NAME=customer_db
CUSTOMER_MONGODB_COLLECTION=customers
PAYMENT_MONGODB_URL=mongodb://payment-mongodb:27017
PAYMENT_MONGODB_DB_NAME=payment_db
PAYMENT_MONGODB_COLLECTION=payments

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