#!/bin/bash

# Script para testar as funcionalidades de autenticação

echo "=== Testando Sistema de Autenticação ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs dos serviços
AUTH_URL="http://localhost:8002"

# Gerar timestamp único para os testes
TIMESTAMP=$(date +%s)
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    echo -e "${YELLOW}Testando: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # Separar body e status code
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Sucesso (Status: $status_code)${NC}"
        if [ "$body" != "" ]; then
            echo "Response: $body" | head -c 200
            echo "..."
        fi
    else
        echo -e "${RED}✗ Falha (Status: $status_code, Esperado: $expected_status)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# Teste 1: Health check
test_endpoint "GET" "$AUTH_URL/auth/health" "" "200" "Health check do auth service"

# Teste 2: Registrar usuário
echo -e "${YELLOW}=== Testando Registro de Usuário ===${NC}"
register_data='{
    "name": "João Silva",
    "email": "'$TEST_EMAIL'",
    "password": "senha123456",
    "role": "CUSTOMER"
}'
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "201" "Registro de usuário"

# Teste 3: Login
echo -e "${YELLOW}=== Testando Login ===${NC}"
login_data='{
    "email": "'$TEST_EMAIL'",
    "password": "senha123456"
}'
login_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$AUTH_URL/auth/login")
echo "Login response: $login_response"

# Extrair token do response
access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Access token: ${access_token:0:50}..."
echo ""

if [ -n "$access_token" ]; then
    # Teste 4: Obter perfil
    echo -e "${YELLOW}=== Testando Obter Perfil ===${NC}"
    profile_response=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Profile response: $profile_response"
    echo ""
    
    # Teste 5: Atualizar perfil
    echo -e "${YELLOW}=== Testando Atualizar Perfil ===${NC}"
    update_data='{
        "name": "João Silva Santos",
        "email": "joao.santos'$TIMESTAMP'@example.com"
    }'
    update_response=$(curl -s -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $access_token" -d "$update_data" "$AUTH_URL/auth/profile")
    echo "Update response: $update_response"
    echo ""
    
    # Teste 6: Verificar se o perfil foi atualizado
    echo -e "${YELLOW}=== Verificando Perfil Atualizado ===${NC}"
    updated_profile=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Updated profile: $updated_profile"
    echo ""
else
    echo -e "${RED}✗ Não foi possível obter o token de acesso${NC}"
fi

# Teste 7: Tentar registrar usuário duplicado
echo -e "${YELLOW}=== Testando Usuário Duplicado ===${NC}"
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "400" "Registro de usuário duplicado (deve falhar)"

# Teste 8: Login com credenciais inválidas
echo -e "${YELLOW}=== Testando Login Inválido ===${NC}"
invalid_login='{
    "email": "'$TEST_EMAIL'",
    "password": "senhaerrada"
}'
test_endpoint "POST" "$AUTH_URL/auth/login" "$invalid_login" "401" "Login com senha incorreta (deve falhar)"

# Teste 9: Validar token inválido
echo -e "${YELLOW}=== Testando Token Inválido ===${NC}"
invalid_token_response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer token_invalido" "$AUTH_URL/auth/profile")
echo "Invalid token response: $invalid_token_response"

echo ""
echo -e "${GREEN}=== Testes Concluídos ===${NC}"
echo ""
echo "Para testar o frontend:"
echo "1. Acesse http://localhost:3000"
echo "2. Clique em 'Não tem uma conta? Cadastre-se'"
echo "3. Preencha o formulário de registro"
echo "4. Após o login, clique no avatar no canto superior direito"
echo "5. Selecione 'Perfil' para editar seus dados" 

# Script para testar as funcionalidades de autenticação

echo "=== Testando Sistema de Autenticação ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs dos serviços
AUTH_URL="http://localhost:8002"

# Gerar timestamp único para os testes
TIMESTAMP=$(date +%s)
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    echo -e "${YELLOW}Testando: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # Separar body e status code
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Sucesso (Status: $status_code)${NC}"
        if [ "$body" != "" ]; then
            echo "Response: $body" | head -c 200
            echo "..."
        fi
    else
        echo -e "${RED}✗ Falha (Status: $status_code, Esperado: $expected_status)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# Teste 1: Health check
test_endpoint "GET" "$AUTH_URL/auth/health" "" "200" "Health check do auth service"

# Teste 2: Registrar usuário
echo -e "${YELLOW}=== Testando Registro de Usuário ===${NC}"
register_data='{
    "name": "João Silva",
    "email": "'$TEST_EMAIL'",
    "password": "senha123456",
    "role": "CUSTOMER"
}'
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "201" "Registro de usuário"

# Teste 3: Login
echo -e "${YELLOW}=== Testando Login ===${NC}"
login_data='{
    "email": "'$TEST_EMAIL'",
    "password": "senha123456"
}'
login_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$AUTH_URL/auth/login")
echo "Login response: $login_response"

# Extrair token do response
access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Access token: ${access_token:0:50}..."
echo ""

if [ -n "$access_token" ]; then
    # Teste 4: Obter perfil
    echo -e "${YELLOW}=== Testando Obter Perfil ===${NC}"
    profile_response=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Profile response: $profile_response"
    echo ""
    
    # Teste 5: Atualizar perfil
    echo -e "${YELLOW}=== Testando Atualizar Perfil ===${NC}"
    update_data='{
        "name": "João Silva Santos",
        "email": "joao.santos'$TIMESTAMP'@example.com"
    }'
    update_response=$(curl -s -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $access_token" -d "$update_data" "$AUTH_URL/auth/profile")
    echo "Update response: $update_response"
    echo ""
    
    # Teste 6: Verificar se o perfil foi atualizado
    echo -e "${YELLOW}=== Verificando Perfil Atualizado ===${NC}"
    updated_profile=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Updated profile: $updated_profile"
    echo ""
else
    echo -e "${RED}✗ Não foi possível obter o token de acesso${NC}"
fi

# Teste 7: Tentar registrar usuário duplicado
echo -e "${YELLOW}=== Testando Usuário Duplicado ===${NC}"
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "400" "Registro de usuário duplicado (deve falhar)"

# Teste 8: Login com credenciais inválidas
echo -e "${YELLOW}=== Testando Login Inválido ===${NC}"
invalid_login='{
    "email": "'$TEST_EMAIL'",
    "password": "senhaerrada"
}'
test_endpoint "POST" "$AUTH_URL/auth/login" "$invalid_login" "401" "Login com senha incorreta (deve falhar)"

# Teste 9: Validar token inválido
echo -e "${YELLOW}=== Testando Token Inválido ===${NC}"
invalid_token_response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer token_invalido" "$AUTH_URL/auth/profile")
echo "Invalid token response: $invalid_token_response"

echo ""
echo -e "${GREEN}=== Testes Concluídos ===${NC}"
echo ""
echo "Para testar o frontend:"
echo "1. Acesse http://localhost:3000"
echo "2. Clique em 'Não tem uma conta? Cadastre-se'"
echo "3. Preencha o formulário de registro"
echo "4. Após o login, clique no avatar no canto superior direito"
echo "5. Selecione 'Perfil' para editar seus dados" 

# Script para testar as funcionalidades de autenticação

echo "=== Testando Sistema de Autenticação ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs dos serviços
AUTH_URL="http://localhost:8002"

# Gerar timestamp único para os testes
TIMESTAMP=$(date +%s)
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    echo -e "${YELLOW}Testando: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # Separar body e status code
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Sucesso (Status: $status_code)${NC}"
        if [ "$body" != "" ]; then
            echo "Response: $body" | head -c 200
            echo "..."
        fi
    else
        echo -e "${RED}✗ Falha (Status: $status_code, Esperado: $expected_status)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# Teste 1: Health check
test_endpoint "GET" "$AUTH_URL/auth/health" "" "200" "Health check do auth service"

# Teste 2: Registrar usuário
echo -e "${YELLOW}=== Testando Registro de Usuário ===${NC}"
register_data='{
    "name": "João Silva",
    "email": "'$TEST_EMAIL'",
    "password": "senha123456",
    "role": "CUSTOMER"
}'
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "201" "Registro de usuário"

# Teste 3: Login
echo -e "${YELLOW}=== Testando Login ===${NC}"
login_data='{
    "email": "'$TEST_EMAIL'",
    "password": "senha123456"
}'
login_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$AUTH_URL/auth/login")
echo "Login response: $login_response"

# Extrair token do response
access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Access token: ${access_token:0:50}..."
echo ""

if [ -n "$access_token" ]; then
    # Teste 4: Obter perfil
    echo -e "${YELLOW}=== Testando Obter Perfil ===${NC}"
    profile_response=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Profile response: $profile_response"
    echo ""
    
    # Teste 5: Atualizar perfil
    echo -e "${YELLOW}=== Testando Atualizar Perfil ===${NC}"
    update_data='{
        "name": "João Silva Santos",
        "email": "joao.santos'$TIMESTAMP'@example.com"
    }'
    update_response=$(curl -s -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $access_token" -d "$update_data" "$AUTH_URL/auth/profile")
    echo "Update response: $update_response"
    echo ""
    
    # Teste 6: Verificar se o perfil foi atualizado
    echo -e "${YELLOW}=== Verificando Perfil Atualizado ===${NC}"
    updated_profile=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Updated profile: $updated_profile"
    echo ""
else
    echo -e "${RED}✗ Não foi possível obter o token de acesso${NC}"
fi

# Teste 7: Tentar registrar usuário duplicado
echo -e "${YELLOW}=== Testando Usuário Duplicado ===${NC}"
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "400" "Registro de usuário duplicado (deve falhar)"

# Teste 8: Login com credenciais inválidas
echo -e "${YELLOW}=== Testando Login Inválido ===${NC}"
invalid_login='{
    "email": "'$TEST_EMAIL'",
    "password": "senhaerrada"
}'
test_endpoint "POST" "$AUTH_URL/auth/login" "$invalid_login" "401" "Login com senha incorreta (deve falhar)"

# Teste 9: Validar token inválido
echo -e "${YELLOW}=== Testando Token Inválido ===${NC}"
invalid_token_response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer token_invalido" "$AUTH_URL/auth/profile")
echo "Invalid token response: $invalid_token_response"

echo ""
echo -e "${GREEN}=== Testes Concluídos ===${NC}"
echo ""
echo "Para testar o frontend:"
echo "1. Acesse http://localhost:3000"
echo "2. Clique em 'Não tem uma conta? Cadastre-se'"
echo "3. Preencha o formulário de registro"
echo "4. Após o login, clique no avatar no canto superior direito"
echo "5. Selecione 'Perfil' para editar seus dados" 

# Script para testar as funcionalidades de autenticação

echo "=== Testando Sistema de Autenticação ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs dos serviços
AUTH_URL="http://localhost:8002"

# Gerar timestamp único para os testes
TIMESTAMP=$(date +%s)
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    echo -e "${YELLOW}Testando: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # Separar body e status code
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Sucesso (Status: $status_code)${NC}"
        if [ "$body" != "" ]; then
            echo "Response: $body" | head -c 200
            echo "..."
        fi
    else
        echo -e "${RED}✗ Falha (Status: $status_code, Esperado: $expected_status)${NC}"
        echo "Response: $body"
    fi
    echo ""
}

# Teste 1: Health check
test_endpoint "GET" "$AUTH_URL/auth/health" "" "200" "Health check do auth service"

# Teste 2: Registrar usuário
echo -e "${YELLOW}=== Testando Registro de Usuário ===${NC}"
register_data='{
    "name": "João Silva",
    "email": "'$TEST_EMAIL'",
    "password": "senha123456",
    "role": "CUSTOMER"
}'
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "201" "Registro de usuário"

# Teste 3: Login
echo -e "${YELLOW}=== Testando Login ===${NC}"
login_data='{
    "email": "'$TEST_EMAIL'",
    "password": "senha123456"
}'
login_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$AUTH_URL/auth/login")
echo "Login response: $login_response"

# Extrair token do response
access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Access token: ${access_token:0:50}..."
echo ""

if [ -n "$access_token" ]; then
    # Teste 4: Obter perfil
    echo -e "${YELLOW}=== Testando Obter Perfil ===${NC}"
    profile_response=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Profile response: $profile_response"
    echo ""
    
    # Teste 5: Atualizar perfil
    echo -e "${YELLOW}=== Testando Atualizar Perfil ===${NC}"
    update_data='{
        "name": "João Silva Santos",
        "email": "joao.santos'$TIMESTAMP'@example.com"
    }'
    update_response=$(curl -s -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $access_token" -d "$update_data" "$AUTH_URL/auth/profile")
    echo "Update response: $update_response"
    echo ""
    
    # Teste 6: Verificar se o perfil foi atualizado
    echo -e "${YELLOW}=== Verificando Perfil Atualizado ===${NC}"
    updated_profile=$(curl -s -H "Authorization: Bearer $access_token" "$AUTH_URL/auth/profile")
    echo "Updated profile: $updated_profile"
    echo ""
else
    echo -e "${RED}✗ Não foi possível obter o token de acesso${NC}"
fi

# Teste 7: Tentar registrar usuário duplicado
echo -e "${YELLOW}=== Testando Usuário Duplicado ===${NC}"
test_endpoint "POST" "$AUTH_URL/auth/register" "$register_data" "400" "Registro de usuário duplicado (deve falhar)"

# Teste 8: Login com credenciais inválidas
echo -e "${YELLOW}=== Testando Login Inválido ===${NC}"
invalid_login='{
    "email": "'$TEST_EMAIL'",
    "password": "senhaerrada"
}'
test_endpoint "POST" "$AUTH_URL/auth/login" "$invalid_login" "401" "Login com senha incorreta (deve falhar)"

# Teste 9: Validar token inválido
echo -e "${YELLOW}=== Testando Token Inválido ===${NC}"
invalid_token_response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer token_invalido" "$AUTH_URL/auth/profile")
echo "Invalid token response: $invalid_token_response"

echo ""
echo -e "${GREEN}=== Testes Concluídos ===${NC}"
echo ""
echo "Para testar o frontend:"
echo "1. Acesse http://localhost:3000"
echo "2. Clique em 'Não tem uma conta? Cadastre-se'"
echo "3. Preencha o formulário de registro"
echo "4. Após o login, clique no avatar no canto superior direito"
echo "5. Selecione 'Perfil' para editar seus dados" 