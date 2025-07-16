#!/bin/bash

# Script simplificado de validação de ambiente
# Compatível com shells mais antigos

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

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado. Execute 'make setup-env' primeiro."
    exit 1
fi

log_info "Validando configuração do ambiente..."

# Carregar variáveis do arquivo .env
source .env

# Lista de variáveis obrigatórias
REQUIRED_VARS="
KEYCLOAK_ADMIN
KEYCLOAK_ADMIN_PASSWORD
KEYCLOAK_URL
KEYCLOAK_CLIENT_SECRET
AUTH_MONGODB_URL
AUTH_MONGODB_DB_NAME
AUTH_SERVICE_URL
CORE_MONGODB_URL
CORE_MONGODB_DB_NAME
CORE_SERVICE_URL
SALES_MONGODB_URL
SALES_MONGODB_DB_NAME
CUSTOMER_MONGODB_URL
CUSTOMER_MONGODB_DB_NAME
CUSTOMER_SERVICE_URL
REDIS_URL
"

# Função para validar variáveis
validate_vars() {
    local missing_vars=""
    local warnings=""
    
    for var in $REQUIRED_VARS; do
        # Verificar se a variável está definida
        if [ -z "${!var}" ]; then
            missing_vars="$missing_vars $var"
        else
            # Verificar se contém valores padrão que devem ser alterados
            if [[ "${!var}" == *"change-me"* ]] || [[ "${!var}" == *"your-"* ]]; then
                warnings="$warnings $var"
            fi
        fi
    done
    
    if [ -n "$missing_vars" ]; then
        log_error "Variáveis obrigatórias ausentes no .env:"
        for var in $missing_vars; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ -n "$warnings" ]; then
        log_warning "Variáveis com valores padrão que devem ser alterados:"
        for var in $warnings; do
            echo "  - $var"
        done
    fi
    
    return 0
}

# Executar validação
if validate_vars; then
    log_success "Configuração do ambiente validada com sucesso!"
    
    echo ""
    echo "Resumo das configurações:"
    echo "========================="
    echo "Keycloak: $KEYCLOAK_URL"
    echo "Auth Service: $AUTH_SERVICE_URL"
    echo "Core Service: $CORE_SERVICE_URL"
    echo "Customer Service: $CUSTOMER_SERVICE_URL"
    echo "Redis: $REDIS_URL"
    echo ""
    echo "Próximos passos:"
    echo "1. Execute: make setup && make up"
    echo "2. Verifique: make status"
    echo "3. Teste: make test"
    
    exit 0
else
    log_error "Configuração do ambiente inválida!"
    echo ""
    echo "Para corrigir:"
    echo "1. Execute: make setup-env"
    echo "2. Edite o arquivo .env conforme necessário"
    echo "3. Execute: make validate-env novamente"
    
    exit 1
fi 