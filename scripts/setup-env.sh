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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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

# Criar arquivos de ambiente base se não existirem
create_env_files() {
    local env=$1
    
    # Arquivo de ambiente global
    if [ ! -f ".env.$env" ]; then
        log_info "Criando arquivo .env.$env"
        cat > ".env.$env" << EOF
# Configuração Global - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# URLs dos Serviços
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CORE_MONGODB_DB=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
SALES_MONGODB_DB=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
CUSTOMER_MONGODB_DB=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    fi
    
    # Arquivos de ambiente por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ ! -f "$service/.env.$env" ]; then
            log_info "Criando arquivo $service/.env.$env"
            
            case $service in
                "auth-service")
                    cat > "$service/.env.$env" << EOF
# Auth Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=users

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=your-client-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=$([ "$env" = "production" ] && echo "15" || echo "30")
JWT_REFRESH_TOKEN_EXPIRE_DAYS=$([ "$env" = "production" ] && echo "1" || echo "7")

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "core-service")
                    cat > "$service/.env.$env" << EOF
# Core Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "sales-service")
                    cat > "$service/.env.$env" << EOF
# Sales Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
                "customer-service")
                    cat > "$service/.env.$env" << EOF
# Customer Service - $env
ENVIRONMENT=$env
DEBUG=$([ "$env" = "development" ] && echo "true" || echo "false")
LOG_LEVEL=$([ "$env" = "development" ] && echo "DEBUG" || echo "INFO")

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db$([ "$env" != "production" ] && echo "_$env" || echo "")
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
                    ;;
            esac
        fi
    done
}

# Copiar arquivos de ambiente
copy_env_files() {
    local env=$1
    
    # Copiar arquivo global
    if [ -f ".env.$env" ]; then
        cp ".env.$env" ".env"
        log_success "Arquivo .env configurado para $env"
    else
        log_warning "Arquivo .env.$env não encontrado"
    fi
    
    # Copiar arquivos por serviço
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    
    for service in "${services[@]}"; do
        if [ -f "$service/.env.$env" ]; then
            cp "$service/.env.$env" "$service/.env"
            log_success "Arquivo $service/.env configurado para $env"
        else
            log_warning "Arquivo $service/.env.$env não encontrado"
        fi
    done
}

# Validar variáveis obrigatórias
validate_env() {
    log_info "Executando validação completa..."
    
    # Verificar se o script de validação existe
    if [ -f "scripts/validate-env.sh" ]; then
        chmod +x scripts/validate-env.sh
        ./scripts/validate-env.sh
        return $?
    else
        log_warning "Script de validação não encontrado, pulando validação"
        return 0
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