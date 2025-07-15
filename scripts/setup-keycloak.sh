#!/bin/bash

# Script para configurar o Keycloak automaticamente

echo "=== Configurando Keycloak ==="
echo ""

# Configurações
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin123"
REALM_NAME="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
CLIENT_SECRET="vehicle-sales-secret"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Aguardar o Keycloak inicializar
echo -e "${YELLOW}Aguardando Keycloak inicializar...${NC}"
for i in {1..30}; do
    if curl -s "$KEYCLOAK_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}Keycloak está disponível!${NC}"
        break
    fi
    echo "Tentativa $i/30 - Aguardando..."
    sleep 5
done

# Função para obter token de acesso do admin
get_admin_token() {
    local response=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4
}

# Obter token de admin
echo -e "${YELLOW}Obtendo token de admin...${NC}"
ADMIN_TOKEN=$(get_admin_token)

if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}Erro: Não foi possível obter token de admin${NC}"
    echo "Verifique se o Keycloak está rodando e as credenciais estão corretas"
    exit 1
fi

echo -e "${GREEN}Token de admin obtido com sucesso!${NC}"

# Função para fazer requisições autenticadas
keycloak_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" = "GET" ]; then
        curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$KEYCLOAK_URL/admin/realms/$endpoint"
    else
        curl -s -X "$method" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$data" "$KEYCLOAK_URL/admin/realms/$endpoint"
    fi
}

# 1. Criar realm
echo -e "${YELLOW}Criando realm '$REALM_NAME'...${NC}"
realm_data='{
    "realm": "'$REALM_NAME'",
    "enabled": true,
    "displayName": "Vehicle Sales System",
    "registrationAllowed": true,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": true,
    "bruteForceProtected": true
}'

realm_response=$(curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$realm_data" "$KEYCLOAK_URL/admin/realms")
echo "Realm criado/atualizado"

# 2. Criar client
echo -e "${YELLOW}Criando client '$CLIENT_ID'...${NC}"
client_data='{
    "clientId": "'$CLIENT_ID'",
    "name": "Vehicle Sales App",
    "description": "Client for Vehicle Sales System",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "'$CLIENT_SECRET'",
    "redirectUris": ["*"],
    "webOrigins": ["*"],
    "protocol": "openid-connect",
    "publicClient": false,
    "bearerOnly": false,
    "consentRequired": false,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "implicitFlowEnabled": false,
    "fullScopeAllowed": true
}'

client_response=$(keycloak_request "POST" "$REALM_NAME/clients" "$client_data")
echo "Client criado/atualizado"

# 3. Criar roles
echo -e "${YELLOW}Criando roles...${NC}"

# Role ADMIN
admin_role='{
    "name": "ADMIN",
    "description": "Administrator role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$admin_role"

# Role CUSTOMER
customer_role='{
    "name": "CUSTOMER",
    "description": "Customer role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$customer_role"

# Role SALES
sales_role='{
    "name": "SALES",
    "description": "Sales role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$sales_role"

echo -e "${GREEN}Roles criadas: ADMIN, CUSTOMER, SALES${NC}"

# 4. Criar usuário admin padrão
echo -e "${YELLOW}Criando usuário admin padrão...${NC}"
admin_user_data='{
    "username": "admin",
    "email": "admin@vehiclesales.com",
    "firstName": "System",
    "lastName": "Administrator",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
        "type": "password",
        "value": "admin123",
        "temporary": false
    }]
}'

admin_user_response=$(keycloak_request "POST" "$REALM_NAME/users" "$admin_user_data")
echo "Usuário admin criado"

# Obter ID do usuário admin
admin_user_id=$(keycloak_request "GET" "$REALM_NAME/users?username=admin" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$admin_user_id" ]; then
    # Atribuir role ADMIN ao usuário
    admin_role_data='[{
        "name": "ADMIN",
        "id": "'$(keycloak_request "GET" "$REALM_NAME/roles/ADMIN" | grep -o '"id":"[^"]*' | cut -d'"' -f4)'"
    }]'
    
    keycloak_request "POST" "$REALM_NAME/users/$admin_user_id/role-mappings/realm" "$admin_role_data"
    echo -e "${GREEN}Role ADMIN atribuída ao usuário admin${NC}"
fi

# 5. Configurar client scopes
echo -e "${YELLOW}Configurando client scopes...${NC}"

# Obter client UUID
client_uuid=$(keycloak_request "GET" "$REALM_NAME/clients?clientId=$CLIENT_ID" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$client_uuid" ]; then
    # Configurar mappers para incluir roles no token
    role_mapper='{
        "name": "realm roles",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-realm-role-mapper",
        "consentRequired": false,
        "config": {
            "multivalued": "true",
            "userinfo.token.claim": "true",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "realm_access.roles",
            "jsonType.label": "String"
        }
    }'
    
    keycloak_request "POST" "$REALM_NAME/clients/$client_uuid/protocol-mappers/models" "$role_mapper"
    echo "Role mapper configurado"
fi

echo ""
echo -e "${GREEN}=== Configuração do Keycloak Concluída ===${NC}"
echo ""
echo "Configurações:"
echo "- Realm: $REALM_NAME"
echo "- Client ID: $CLIENT_ID"
echo "- Client Secret: $CLIENT_SECRET"
echo "- Admin User: admin / admin123"
echo "- Roles: ADMIN, CUSTOMER, SALES"
echo ""
echo "URLs importantes:"
echo "- Admin Console: $KEYCLOAK_URL/admin"
echo "- Realm Console: $KEYCLOAK_URL/admin/master/console/#/$REALM_NAME"
echo ""
echo -e "${YELLOW}Agora você pode testar o registro e login de usuários!${NC}" 

# Script para configurar o Keycloak automaticamente

echo "=== Configurando Keycloak ==="
echo ""

# Configurações
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin123"
REALM_NAME="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
CLIENT_SECRET="vehicle-sales-secret"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Aguardar o Keycloak inicializar
echo -e "${YELLOW}Aguardando Keycloak inicializar...${NC}"
for i in {1..30}; do
    if curl -s "$KEYCLOAK_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}Keycloak está disponível!${NC}"
        break
    fi
    echo "Tentativa $i/30 - Aguardando..."
    sleep 5
done

# Função para obter token de acesso do admin
get_admin_token() {
    local response=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4
}

# Obter token de admin
echo -e "${YELLOW}Obtendo token de admin...${NC}"
ADMIN_TOKEN=$(get_admin_token)

if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}Erro: Não foi possível obter token de admin${NC}"
    echo "Verifique se o Keycloak está rodando e as credenciais estão corretas"
    exit 1
fi

echo -e "${GREEN}Token de admin obtido com sucesso!${NC}"

# Função para fazer requisições autenticadas
keycloak_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" = "GET" ]; then
        curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$KEYCLOAK_URL/admin/realms/$endpoint"
    else
        curl -s -X "$method" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$data" "$KEYCLOAK_URL/admin/realms/$endpoint"
    fi
}

# 1. Criar realm
echo -e "${YELLOW}Criando realm '$REALM_NAME'...${NC}"
realm_data='{
    "realm": "'$REALM_NAME'",
    "enabled": true,
    "displayName": "Vehicle Sales System",
    "registrationAllowed": true,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": true,
    "bruteForceProtected": true
}'

realm_response=$(curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$realm_data" "$KEYCLOAK_URL/admin/realms")
echo "Realm criado/atualizado"

# 2. Criar client
echo -e "${YELLOW}Criando client '$CLIENT_ID'...${NC}"
client_data='{
    "clientId": "'$CLIENT_ID'",
    "name": "Vehicle Sales App",
    "description": "Client for Vehicle Sales System",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "'$CLIENT_SECRET'",
    "redirectUris": ["*"],
    "webOrigins": ["*"],
    "protocol": "openid-connect",
    "publicClient": false,
    "bearerOnly": false,
    "consentRequired": false,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "implicitFlowEnabled": false,
    "fullScopeAllowed": true
}'

client_response=$(keycloak_request "POST" "$REALM_NAME/clients" "$client_data")
echo "Client criado/atualizado"

# 3. Criar roles
echo -e "${YELLOW}Criando roles...${NC}"

# Role ADMIN
admin_role='{
    "name": "ADMIN",
    "description": "Administrator role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$admin_role"

# Role CUSTOMER
customer_role='{
    "name": "CUSTOMER",
    "description": "Customer role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$customer_role"

# Role SALES
sales_role='{
    "name": "SALES",
    "description": "Sales role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$sales_role"

echo -e "${GREEN}Roles criadas: ADMIN, CUSTOMER, SALES${NC}"

# 4. Criar usuário admin padrão
echo -e "${YELLOW}Criando usuário admin padrão...${NC}"
admin_user_data='{
    "username": "admin",
    "email": "admin@vehiclesales.com",
    "firstName": "System",
    "lastName": "Administrator",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
        "type": "password",
        "value": "admin123",
        "temporary": false
    }]
}'

admin_user_response=$(keycloak_request "POST" "$REALM_NAME/users" "$admin_user_data")
echo "Usuário admin criado"

# Obter ID do usuário admin
admin_user_id=$(keycloak_request "GET" "$REALM_NAME/users?username=admin" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$admin_user_id" ]; then
    # Atribuir role ADMIN ao usuário
    admin_role_data='[{
        "name": "ADMIN",
        "id": "'$(keycloak_request "GET" "$REALM_NAME/roles/ADMIN" | grep -o '"id":"[^"]*' | cut -d'"' -f4)'"
    }]'
    
    keycloak_request "POST" "$REALM_NAME/users/$admin_user_id/role-mappings/realm" "$admin_role_data"
    echo -e "${GREEN}Role ADMIN atribuída ao usuário admin${NC}"
fi

# 5. Configurar client scopes
echo -e "${YELLOW}Configurando client scopes...${NC}"

# Obter client UUID
client_uuid=$(keycloak_request "GET" "$REALM_NAME/clients?clientId=$CLIENT_ID" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$client_uuid" ]; then
    # Configurar mappers para incluir roles no token
    role_mapper='{
        "name": "realm roles",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-realm-role-mapper",
        "consentRequired": false,
        "config": {
            "multivalued": "true",
            "userinfo.token.claim": "true",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "realm_access.roles",
            "jsonType.label": "String"
        }
    }'
    
    keycloak_request "POST" "$REALM_NAME/clients/$client_uuid/protocol-mappers/models" "$role_mapper"
    echo "Role mapper configurado"
fi

echo ""
echo -e "${GREEN}=== Configuração do Keycloak Concluída ===${NC}"
echo ""
echo "Configurações:"
echo "- Realm: $REALM_NAME"
echo "- Client ID: $CLIENT_ID"
echo "- Client Secret: $CLIENT_SECRET"
echo "- Admin User: admin / admin123"
echo "- Roles: ADMIN, CUSTOMER, SALES"
echo ""
echo "URLs importantes:"
echo "- Admin Console: $KEYCLOAK_URL/admin"
echo "- Realm Console: $KEYCLOAK_URL/admin/master/console/#/$REALM_NAME"
echo ""
echo -e "${YELLOW}Agora você pode testar o registro e login de usuários!${NC}" 

# Script para configurar o Keycloak automaticamente

echo "=== Configurando Keycloak ==="
echo ""

# Configurações
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin123"
REALM_NAME="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
CLIENT_SECRET="vehicle-sales-secret"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Aguardar o Keycloak inicializar
echo -e "${YELLOW}Aguardando Keycloak inicializar...${NC}"
for i in {1..30}; do
    if curl -s "$KEYCLOAK_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}Keycloak está disponível!${NC}"
        break
    fi
    echo "Tentativa $i/30 - Aguardando..."
    sleep 5
done

# Função para obter token de acesso do admin
get_admin_token() {
    local response=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4
}

# Obter token de admin
echo -e "${YELLOW}Obtendo token de admin...${NC}"
ADMIN_TOKEN=$(get_admin_token)

if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}Erro: Não foi possível obter token de admin${NC}"
    echo "Verifique se o Keycloak está rodando e as credenciais estão corretas"
    exit 1
fi

echo -e "${GREEN}Token de admin obtido com sucesso!${NC}"

# Função para fazer requisições autenticadas
keycloak_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" = "GET" ]; then
        curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$KEYCLOAK_URL/admin/realms/$endpoint"
    else
        curl -s -X "$method" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$data" "$KEYCLOAK_URL/admin/realms/$endpoint"
    fi
}

# 1. Criar realm
echo -e "${YELLOW}Criando realm '$REALM_NAME'...${NC}"
realm_data='{
    "realm": "'$REALM_NAME'",
    "enabled": true,
    "displayName": "Vehicle Sales System",
    "registrationAllowed": true,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": true,
    "bruteForceProtected": true
}'

realm_response=$(curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$realm_data" "$KEYCLOAK_URL/admin/realms")
echo "Realm criado/atualizado"

# 2. Criar client
echo -e "${YELLOW}Criando client '$CLIENT_ID'...${NC}"
client_data='{
    "clientId": "'$CLIENT_ID'",
    "name": "Vehicle Sales App",
    "description": "Client for Vehicle Sales System",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "'$CLIENT_SECRET'",
    "redirectUris": ["*"],
    "webOrigins": ["*"],
    "protocol": "openid-connect",
    "publicClient": false,
    "bearerOnly": false,
    "consentRequired": false,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "implicitFlowEnabled": false,
    "fullScopeAllowed": true
}'

client_response=$(keycloak_request "POST" "$REALM_NAME/clients" "$client_data")
echo "Client criado/atualizado"

# 3. Criar roles
echo -e "${YELLOW}Criando roles...${NC}"

# Role ADMIN
admin_role='{
    "name": "ADMIN",
    "description": "Administrator role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$admin_role"

# Role CUSTOMER
customer_role='{
    "name": "CUSTOMER",
    "description": "Customer role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$customer_role"

# Role SALES
sales_role='{
    "name": "SALES",
    "description": "Sales role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$sales_role"

echo -e "${GREEN}Roles criadas: ADMIN, CUSTOMER, SALES${NC}"

# 4. Criar usuário admin padrão
echo -e "${YELLOW}Criando usuário admin padrão...${NC}"
admin_user_data='{
    "username": "admin",
    "email": "admin@vehiclesales.com",
    "firstName": "System",
    "lastName": "Administrator",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
        "type": "password",
        "value": "admin123",
        "temporary": false
    }]
}'

admin_user_response=$(keycloak_request "POST" "$REALM_NAME/users" "$admin_user_data")
echo "Usuário admin criado"

# Obter ID do usuário admin
admin_user_id=$(keycloak_request "GET" "$REALM_NAME/users?username=admin" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$admin_user_id" ]; then
    # Atribuir role ADMIN ao usuário
    admin_role_data='[{
        "name": "ADMIN",
        "id": "'$(keycloak_request "GET" "$REALM_NAME/roles/ADMIN" | grep -o '"id":"[^"]*' | cut -d'"' -f4)'"
    }]'
    
    keycloak_request "POST" "$REALM_NAME/users/$admin_user_id/role-mappings/realm" "$admin_role_data"
    echo -e "${GREEN}Role ADMIN atribuída ao usuário admin${NC}"
fi

# 5. Configurar client scopes
echo -e "${YELLOW}Configurando client scopes...${NC}"

# Obter client UUID
client_uuid=$(keycloak_request "GET" "$REALM_NAME/clients?clientId=$CLIENT_ID" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$client_uuid" ]; then
    # Configurar mappers para incluir roles no token
    role_mapper='{
        "name": "realm roles",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-realm-role-mapper",
        "consentRequired": false,
        "config": {
            "multivalued": "true",
            "userinfo.token.claim": "true",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "realm_access.roles",
            "jsonType.label": "String"
        }
    }'
    
    keycloak_request "POST" "$REALM_NAME/clients/$client_uuid/protocol-mappers/models" "$role_mapper"
    echo "Role mapper configurado"
fi

echo ""
echo -e "${GREEN}=== Configuração do Keycloak Concluída ===${NC}"
echo ""
echo "Configurações:"
echo "- Realm: $REALM_NAME"
echo "- Client ID: $CLIENT_ID"
echo "- Client Secret: $CLIENT_SECRET"
echo "- Admin User: admin / admin123"
echo "- Roles: ADMIN, CUSTOMER, SALES"
echo ""
echo "URLs importantes:"
echo "- Admin Console: $KEYCLOAK_URL/admin"
echo "- Realm Console: $KEYCLOAK_URL/admin/master/console/#/$REALM_NAME"
echo ""
echo -e "${YELLOW}Agora você pode testar o registro e login de usuários!${NC}" 

# Script para configurar o Keycloak automaticamente

echo "=== Configurando Keycloak ==="
echo ""

# Configurações
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="admin123"
REALM_NAME="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
CLIENT_SECRET="vehicle-sales-secret"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Aguardar o Keycloak inicializar
echo -e "${YELLOW}Aguardando Keycloak inicializar...${NC}"
for i in {1..30}; do
    if curl -s "$KEYCLOAK_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}Keycloak está disponível!${NC}"
        break
    fi
    echo "Tentativa $i/30 - Aguardando..."
    sleep 5
done

# Função para obter token de acesso do admin
get_admin_token() {
    local response=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4
}

# Obter token de admin
echo -e "${YELLOW}Obtendo token de admin...${NC}"
ADMIN_TOKEN=$(get_admin_token)

if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}Erro: Não foi possível obter token de admin${NC}"
    echo "Verifique se o Keycloak está rodando e as credenciais estão corretas"
    exit 1
fi

echo -e "${GREEN}Token de admin obtido com sucesso!${NC}"

# Função para fazer requisições autenticadas
keycloak_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" = "GET" ]; then
        curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$KEYCLOAK_URL/admin/realms/$endpoint"
    else
        curl -s -X "$method" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$data" "$KEYCLOAK_URL/admin/realms/$endpoint"
    fi
}

# 1. Criar realm
echo -e "${YELLOW}Criando realm '$REALM_NAME'...${NC}"
realm_data='{
    "realm": "'$REALM_NAME'",
    "enabled": true,
    "displayName": "Vehicle Sales System",
    "registrationAllowed": true,
    "loginWithEmailAllowed": true,
    "duplicateEmailsAllowed": false,
    "resetPasswordAllowed": true,
    "editUsernameAllowed": true,
    "bruteForceProtected": true
}'

realm_response=$(curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" -d "$realm_data" "$KEYCLOAK_URL/admin/realms")
echo "Realm criado/atualizado"

# 2. Criar client
echo -e "${YELLOW}Criando client '$CLIENT_ID'...${NC}"
client_data='{
    "clientId": "'$CLIENT_ID'",
    "name": "Vehicle Sales App",
    "description": "Client for Vehicle Sales System",
    "enabled": true,
    "clientAuthenticatorType": "client-secret",
    "secret": "'$CLIENT_SECRET'",
    "redirectUris": ["*"],
    "webOrigins": ["*"],
    "protocol": "openid-connect",
    "publicClient": false,
    "bearerOnly": false,
    "consentRequired": false,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": true,
    "serviceAccountsEnabled": true,
    "implicitFlowEnabled": false,
    "fullScopeAllowed": true
}'

client_response=$(keycloak_request "POST" "$REALM_NAME/clients" "$client_data")
echo "Client criado/atualizado"

# 3. Criar roles
echo -e "${YELLOW}Criando roles...${NC}"

# Role ADMIN
admin_role='{
    "name": "ADMIN",
    "description": "Administrator role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$admin_role"

# Role CUSTOMER
customer_role='{
    "name": "CUSTOMER",
    "description": "Customer role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$customer_role"

# Role SALES
sales_role='{
    "name": "SALES",
    "description": "Sales role"
}'
keycloak_request "POST" "$REALM_NAME/roles" "$sales_role"

echo -e "${GREEN}Roles criadas: ADMIN, CUSTOMER, SALES${NC}"

# 4. Criar usuário admin padrão
echo -e "${YELLOW}Criando usuário admin padrão...${NC}"
admin_user_data='{
    "username": "admin",
    "email": "admin@vehiclesales.com",
    "firstName": "System",
    "lastName": "Administrator",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
        "type": "password",
        "value": "admin123",
        "temporary": false
    }]
}'

admin_user_response=$(keycloak_request "POST" "$REALM_NAME/users" "$admin_user_data")
echo "Usuário admin criado"

# Obter ID do usuário admin
admin_user_id=$(keycloak_request "GET" "$REALM_NAME/users?username=admin" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$admin_user_id" ]; then
    # Atribuir role ADMIN ao usuário
    admin_role_data='[{
        "name": "ADMIN",
        "id": "'$(keycloak_request "GET" "$REALM_NAME/roles/ADMIN" | grep -o '"id":"[^"]*' | cut -d'"' -f4)'"
    }]'
    
    keycloak_request "POST" "$REALM_NAME/users/$admin_user_id/role-mappings/realm" "$admin_role_data"
    echo -e "${GREEN}Role ADMIN atribuída ao usuário admin${NC}"
fi

# 5. Configurar client scopes
echo -e "${YELLOW}Configurando client scopes...${NC}"

# Obter client UUID
client_uuid=$(keycloak_request "GET" "$REALM_NAME/clients?clientId=$CLIENT_ID" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$client_uuid" ]; then
    # Configurar mappers para incluir roles no token
    role_mapper='{
        "name": "realm roles",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-usermodel-realm-role-mapper",
        "consentRequired": false,
        "config": {
            "multivalued": "true",
            "userinfo.token.claim": "true",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "claim.name": "realm_access.roles",
            "jsonType.label": "String"
        }
    }'
    
    keycloak_request "POST" "$REALM_NAME/clients/$client_uuid/protocol-mappers/models" "$role_mapper"
    echo "Role mapper configurado"
fi

echo ""
echo -e "${GREEN}=== Configuração do Keycloak Concluída ===${NC}"
echo ""
echo "Configurações:"
echo "- Realm: $REALM_NAME"
echo "- Client ID: $CLIENT_ID"
echo "- Client Secret: $CLIENT_SECRET"
echo "- Admin User: admin / admin123"
echo "- Roles: ADMIN, CUSTOMER, SALES"
echo ""
echo "URLs importantes:"
echo "- Admin Console: $KEYCLOAK_URL/admin"
echo "- Realm Console: $KEYCLOAK_URL/admin/master/console/#/$REALM_NAME"
echo ""
echo -e "${YELLOW}Agora você pode testar o registro e login de usuários!${NC}" 