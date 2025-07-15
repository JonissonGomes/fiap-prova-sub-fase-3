#!/bin/bash

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 

# Script para obter o client secret do Keycloak
# Uso: ./get-keycloak-client-secret.sh

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"

echo "🔑 Obtendo client secret do Keycloak..."
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 5 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando: make keycloak"
    exit 1
fi
echo "✅ Keycloak está acessível!"

# Obter token de acesso
echo "📡 Obtendo token de acesso do admin..."
TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASS" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
    echo "❌ Erro ao obter token de acesso"
    exit 1
fi
echo "✅ Token de acesso obtido com sucesso!"

# Obter client secret
echo "🔍 Buscando client secret..."
SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -n "$SECRET" ] && [ "$SECRET" != "null" ] && [ "$SECRET" != "empty" ]; then
    echo "✅ Client '$CLIENT_ID' encontrado!"
    echo ""
    echo "🎉 Client Secret obtido com sucesso!"
    echo "================================="
    echo "CLIENT_ID: $CLIENT_ID"
    echo "CLIENT_SECRET: $SECRET"
    echo "================================="
    echo ""
    echo "💡 Adicione estas variáveis ao seu arquivo .env:"
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID"
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
    echo ""
    
    # Salvar em arquivo temporário
    echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" > /tmp/keycloak-credentials-development.env
    echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> /tmp/keycloak-credentials-development.env
    echo "📝 Credenciais salvas em: /tmp/keycloak-credentials-development.env"
    
else
    echo "❌ Client '$CLIENT_ID' não encontrado ou não tem secret configurado"
    echo ""
    echo "📋 Debug - Verificando se o client existe..."
    CLIENTS=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Clients disponíveis:"
    echo "$CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
    echo ""
    echo "💡 Soluções:"
    echo "   1. Executar: make keycloak-setup"
    echo "   2. Verificar se o realm existe"
    echo "   3. Criar o client manualmente no console admin"
    echo "   4. Verificar se o client tem 'Client authentication' habilitado"
    exit 1
fi 