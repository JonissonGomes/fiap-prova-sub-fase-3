#!/bin/bash

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias principais
REQUIRED_VARS="KEYCLOAK_ADMIN KEYCLOAK_ADMIN_PASSWORD KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET 
AUTH_MONGODB_URL AUTH_MONGODB_DB_NAME AUTH_SERVICE_URL 
CORE_MONGODB_URL CORE_MONGODB_DB_NAME CORE_SERVICE_URL
SALES_MONGODB_URL SALES_MONGODB_DB_NAME
CUSTOMER_MONGODB_URL CUSTOMER_MONGODB_DB_NAME CUSTOMER_SERVICE_URL
REDIS_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 

# Script de validação de variáveis de ambiente
# Verifica se todas as variáveis obrigatórias estão definidas

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

# Variáveis obrigatórias por serviço
declare -A SERVICE_VARS
SERVICE_VARS["auth-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME KEYCLOAK_URL KEYCLOAK_CLIENT_SECRET JWT_SECRET_KEY DEFAULT_ADMIN_EMAIL DEFAULT_ADMIN_PASSWORD"
SERVICE_VARS["core-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"
SERVICE_VARS["sales-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME CORE_SERVICE_URL AUTH_SERVICE_URL CUSTOMER_SERVICE_URL"
SERVICE_VARS["customer-service"]="ENVIRONMENT MONGODB_URL MONGODB_DB_NAME AUTH_SERVICE_URL"

# Função para validar variáveis de um serviço
validate_service() {
    local service=$1
    local env_file="$service/.env"
    
    log_info "Validando $service..."
    
    if [ ! -f "$env_file" ]; then
        log_error "Arquivo $env_file não encontrado"
        return 1
    fi
    
    # Carregar variáveis do arquivo
    set -o allexport
    source "$env_file"
    set +o allexport
    
    local required_vars=(${SERVICE_VARS[$service]})
    local missing_vars=()
    local warning_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        elif [[ "${!var}" == *"change-in-production"* ]] || [[ "${!var}" == *"your-"* ]]; then
            warning_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Variáveis obrigatórias não definidas em $service:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        return 1
    fi
    
    if [ ${#warning_vars[@]} -gt 0 ]; then
        log_warning "Variáveis com valores padrão em $service (atualize para produção):"
        for var in "${warning_vars[@]}"; do
            echo "  - $var: ${!var}"
        done
    fi
    
    log_success "$service validado com sucesso"
    return 0
}

# Função principal
main() {
    log_info "Iniciando validação de variáveis de ambiente..."
    echo ""
    
    local services=("auth-service" "core-service" "sales-service" "customer-service")
    local failed_services=()
    local warning_services=()
    
    for service in "${services[@]}"; do
        if validate_service "$service"; then
            echo ""
        else
            failed_services+=("$service")
            echo ""
        fi
    done
    
    # Verificar arquivos Docker Compose
    log_info "Verificando docker-compose.yml..."
    if [ -f "docker-compose.yml" ]; then
        log_success "docker-compose.yml encontrado"
    else
        log_error "docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Verificar Makefile
    log_info "Verificando Makefile..."
    if [ -f "Makefile" ]; then
        log_success "Makefile encontrado"
    else
        log_error "Makefile não encontrado"
        exit 1
    fi
    
    # Verificar documentação
    log_info "Verificando documentação..."
    local docs=("README.md" "docs/ARCHITECTURE.md" "docs/DEPLOYMENT.md" "docs/API_DOCUMENTATION.md" "docs/ENVIRONMENT_VARIABLES.md")
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "$doc encontrado"
        else
            log_warning "$doc não encontrado"
        fi
    done
    
    echo ""
    echo "================================================"
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Validação falhou para os seguintes serviços:"
        for service in "${failed_services[@]}"; do
            echo "  - $service"
        done
        echo ""
        echo "Corrija os problemas e execute novamente."
        exit 1
    else
        log_success "Todos os serviços validados com sucesso!"
        echo ""
        echo "Sistema pronto para execução:"
        echo "1. Execute: make setup && make up"
        echo "2. Aguarde a inicialização (pode levar alguns minutos)"
        echo "3. Verifique: make status"
        echo "4. Acesse a documentação: make docs"
        echo ""
        echo "Endpoints disponíveis:"
        echo "- Auth Service: http://localhost:8002/docs"
        echo "- Core Service: http://localhost:8000/docs"
        echo "- Sales Service: http://localhost:8001/docs"
        echo "- Customer Service: http://localhost:8003/docs"
        echo "- Keycloak: http://localhost:8080"
        echo ""
        echo "Usuário padrão:"
        echo "- Email: admin@vehiclesales.com"
        echo "- Senha: admin123"
    fi
}

# Executar função principal
main "$@" 