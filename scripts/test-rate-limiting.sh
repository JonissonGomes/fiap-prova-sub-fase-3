#!/bin/bash

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 

# Script para testar rate limiting
# Uso: ./scripts/test-rate-limiting.sh

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

# Configurações
BASE_URL="http://localhost:8002"
HEALTH_URL="$BASE_URL/health"
LOGIN_URL="$BASE_URL/auth/login"
STATS_URL="$BASE_URL/rate-limit/stats"
CONFIG_URL="$BASE_URL/rate-limit/config"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$description - Status: $response"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $response"
        return 1
    fi
}

# Função para testar rate limiting
test_rate_limiting() {
    local url=$1
    local limit=$2
    local description=$3
    
    log_info "Testando rate limiting para $description"
    log_info "URL: $url, Limite: $limit requisições"
    
    local success_count=0
    local rate_limited_count=0
    
    # Faz requisições até atingir o limite
    for i in $(seq 1 $((limit + 5))); do
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
        
        if [ "$response" = "200" ]; then
            success_count=$((success_count + 1))
            echo -n "."
        elif [ "$response" = "429" ]; then
            rate_limited_count=$((rate_limited_count + 1))
            echo -n "X"
        else
            echo -n "?"
        fi
        
        # Pequena pausa entre requisições
        sleep 0.1
    done
    
    echo ""
    log_info "Sucessos: $success_count, Rate Limited: $rate_limited_count"
    
    if [ $rate_limited_count -gt 0 ]; then
        log_success "Rate limiting funcionando corretamente!"
        return 0
    else
        log_warning "Rate limiting pode não estar funcionando como esperado"
        return 1
    fi
}

# Função para obter token de admin
get_admin_token() {
    log_info "Obtendo token de administrador..."
    
    response=$(curl -s -X POST "$LOGIN_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@vehiclesales.com",
            "password": "admin123"
        }')
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            log_success "Token obtido com sucesso"
            echo "$token"
            return 0
        fi
    fi
    
    log_error "Falha ao obter token de administrador"
    return 1
}

# Função para testar endpoints de gerenciamento
test_management_endpoints() {
    local token=$1
    
    log_info "Testando endpoints de gerenciamento de rate limiting..."
    
    # Testa endpoint de configuração
    log_info "Testando GET /rate-limit/config"
    response=$(curl -s -w "%{http_code}" -o /tmp/config_response.json \
        -H "Authorization: Bearer $token" \
        "$CONFIG_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Configuração obtida com sucesso"
        cat /tmp/config_response.json | head -5
    else
        log_error "Falha ao obter configuração - Status: $response"
    fi
    
    # Testa endpoint de estatísticas
    log_info "Testando GET /rate-limit/stats"
    response=$(curl -s -w "%{http_code}" -o /tmp/stats_response.json \
        -H "Authorization: Bearer $token" \
        "$STATS_URL")
    
    if [ "$response" = "200" ]; then
        log_success "Estatísticas obtidas com sucesso"
        cat /tmp/stats_response.json | head -5
    else
        log_error "Falha ao obter estatísticas - Status: $response"
    fi
    
    # Cleanup
    rm -f /tmp/config_response.json /tmp/stats_response.json
}

# Função principal
main() {
    echo "================================================"
    echo "🛡️  Teste de Rate Limiting - Sistema de Vendas"
    echo "================================================"
    echo ""
    
    # Verifica se os serviços estão rodando
    log_info "Verificando se os serviços estão rodando..."
    if ! test_endpoint "$HEALTH_URL" "200" "Health check"; then
        log_error "Serviço não está rodando. Execute: make up"
        exit 1
    fi
    
    echo ""
    log_info "Aguardando 5 segundos para estabilizar..."
    sleep 5
    
    # Testa rate limiting no endpoint de health (limite alto)
    echo ""
    log_info "=== Teste 1: Health Check (limite alto) ==="
    test_rate_limiting "$HEALTH_URL" 10 "Health Check"
    
    # Aguarda reset do rate limiting
    echo ""
    log_info "Aguardando 60 segundos para reset do rate limiting..."
    sleep 60
    
    # Testa rate limiting no endpoint de login (limite baixo)
    echo ""
    log_info "=== Teste 2: Login (limite baixo) ==="
    test_rate_limiting "$LOGIN_URL" 5 "Login Endpoint"
    
    # Testa endpoints de gerenciamento
    echo ""
    log_info "=== Teste 3: Endpoints de Gerenciamento ==="
    
    # Aguarda mais um pouco para evitar rate limiting
    sleep 30
    
    admin_token=$(get_admin_token)
    if [ $? -eq 0 ] && [ -n "$admin_token" ]; then
        test_management_endpoints "$admin_token"
    else
        log_warning "Pulando testes de gerenciamento (falha na autenticação)"
    fi
    
    echo ""
    echo "================================================"
    echo "✅ Testes de Rate Limiting Concluídos"
    echo "================================================"
    echo ""
    echo "Resumo dos testes:"
    echo "1. ✅ Health Check com limite alto"
    echo "2. ✅ Login com limite baixo"
    echo "3. ✅ Endpoints de gerenciamento"
    echo ""
    echo "Para monitorar em tempo real:"
    echo "- Logs: make auth-logs"
    echo "- Redis: make redis-cli"
    echo "- Stats: curl -H 'Authorization: Bearer <token>' $STATS_URL"
    echo ""
}

# Verifica se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    log_error "Este script deve ser executado na raiz do projeto"
    exit 1
fi

# Executa função principal
main "$@" 