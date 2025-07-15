#!/bin/bash

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 

# Script para obter o client secret do Keycloak (Produção)
# Uso: ./get-keycloak-client-secret-prod.sh [environment]
# Exemplo: ./get-keycloak-client-secret-prod.sh production

set -e

# Configuração padrão
DEFAULT_ENVIRONMENT="development"
ENVIRONMENT=${1:-$DEFAULT_ENVIRONMENT}

# Carregar variáveis de ambiente baseadas no ambiente
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo "📋 Carregando configurações do ambiente: $ENVIRONMENT"
    source .env.${ENVIRONMENT}
elif [ -f ".env" ]; then
    echo "📋 Carregando configurações do arquivo .env padrão"
    source .env
else
    echo "⚠️  Nenhum arquivo de configuração encontrado, usando valores padrão"
fi

# Configurações com fallback para valores padrão
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://localhost:8080"}
REALM=${KEYCLOAK_REALM:-"vehicle-sales"}
CLIENT_ID=${KEYCLOAK_CLIENT_ID:-"vehicle-sales-app"}
ADMIN_USER=${KEYCLOAK_ADMIN_USER:-"admin"}
ADMIN_PASS=${KEYCLOAK_ADMIN_PASS:-"admin123"}

# Validar se estamos em produção e as credenciais são seguras
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$ADMIN_PASS" = "admin123" ] || [ "$ADMIN_PASS" = "admin" ]; then
        echo "❌ ERRO: Credenciais padrão não são seguras para produção!"
        echo "💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production"
        exit 1
    fi
    
    if [[ "$KEYCLOAK_URL" == *"localhost"* ]]; then
        echo "❌ ERRO: URL localhost não é válida para produção!"
        echo "💡 Configure KEYCLOAK_URL com a URL real do Keycloak em produção"
        exit 1
    fi
fi

echo "🔑 Obtendo client secret do Keycloak..."
echo "Ambiente: $ENVIRONMENT"
echo "URL: $KEYCLOAK_URL"
echo "Realm: $REALM"
echo "Client ID: $CLIENT_ID"
echo ""

# Função para obter token de acesso do admin
get_admin_token() {
    echo "📡 Obtendo token de acesso do admin..."
    
    # Configurar curl para produção (com SSL)
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        # Em produção, validar certificados SSL
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            # Em staging, pode ignorar SSL se necessário
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    RESPONSE=$(curl $CURL_OPTS -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASS" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$'
    else
        echo "❌ Erro ao obter token de acesso:"
        echo "$RESPONSE"
        exit 1
    fi
}

# Função para obter o client secret
get_client_secret() {
    local token=$1
    
    echo "🔍 Buscando client secret..."
    
    # Configurar curl para produção
    CURL_OPTS="-s"
    if [[ "$KEYCLOAK_URL" == https://* ]]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
        else
            CURL_OPTS="$CURL_OPTS -k"
        fi
    fi
    
    # Listar todos os clients
    ALL_CLIENTS=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    # Verificar se a resposta é válida
    if [ -z "$ALL_CLIENTS" ] || echo "$ALL_CLIENTS" | grep -q "error"; then
        echo "❌ Erro ao listar clients:"
        echo "$ALL_CLIENTS"
        exit 1
    fi
    
    # Obter o ID interno do client
    CLIENT_INTERNAL_ID=$(echo "$ALL_CLIENTS" | jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .id' 2>/dev/null)
    
    if [ -z "$CLIENT_INTERNAL_ID" ] || [ "$CLIENT_INTERNAL_ID" = "null" ]; then
        echo "❌ Client '$CLIENT_ID' não encontrado no realm '$REALM'"
        echo "Clients disponíveis:"
        echo "$ALL_CLIENTS" | jq -r '.[].clientId' 2>/dev/null || echo "Erro ao processar JSON"
        exit 1
    fi
    
    echo "✅ Client encontrado (ID interno: $CLIENT_INTERNAL_ID)"
    
    # Obter o client secret
    SECRET_RESPONSE=$(curl $CURL_OPTS -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_INTERNAL_ID/client-secret" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$SECRET_RESPONSE" | grep -q "value"; then
        SECRET=$(echo "$SECRET_RESPONSE" | jq -r '.value' 2>/dev/null)
        echo ""
        echo "🎉 Client Secret obtido com sucesso!"
        echo "================================="
        echo "ENVIRONMENT: $ENVIRONMENT"
        echo "CLIENT_ID: $CLIENT_ID"
        echo "CLIENT_SECRET: $SECRET"
        echo "================================="
        echo ""
        
        # Salvar em arquivo específico do ambiente
        OUTPUT_FILE="/tmp/keycloak-credentials-${ENVIRONMENT}.env"
        echo "# Keycloak credentials for $ENVIRONMENT environment" > "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_ID=$CLIENT_ID" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_URL=$KEYCLOAK_URL" >> "$OUTPUT_FILE"
        echo "KEYCLOAK_REALM=$REALM" >> "$OUTPUT_FILE"
        
        echo "📝 Credenciais salvas em: $OUTPUT_FILE"
        echo ""
        echo "💡 Para usar em produção, adicione ao seu arquivo .env.production:"
        echo "KEYCLOAK_CLIENT_SECRET=$SECRET"
        
        # Se for produção, mostrar avisos de segurança
        if [ "$ENVIRONMENT" = "production" ]; then
            echo ""
            echo "🔒 AVISOS DE SEGURANÇA PARA PRODUÇÃO:"
            echo "1. Mantenha o client secret seguro e não o compartilhe"
            echo "2. Use variáveis de ambiente seguras no deploy"
            echo "3. Considere rotacionar o secret periodicamente"
            echo "4. Monitore o uso do client no Keycloak"
        fi
        
    else
        echo "❌ Erro ao obter client secret:"
        echo "$SECRET_RESPONSE"
        exit 1
    fi
}

# Verificar dependências
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instale com:"
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."

# Configurar curl para teste de conectividade
CURL_OPTS="-s --connect-timeout 10"
if [[ "$KEYCLOAK_URL" == https://* ]]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        CURL_OPTS="$CURL_OPTS --cacert /etc/ssl/certs/ca-certificates.crt"
    else
        CURL_OPTS="$CURL_OPTS -k"
    fi
fi

if ! curl $CURL_OPTS "$KEYCLOAK_URL/realms/master" > /dev/null; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Verifique:"
    echo "   - URL está correta no arquivo .env.$ENVIRONMENT"
    echo "   - Keycloak está rodando"
    echo "   - Rede/firewall permite acesso"
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "   - Para desenvolvimento: docker-compose up -d keycloak"
    fi
    exit 1
fi

echo "✅ Keycloak está acessível!"
echo ""

# Executar o processo
TOKEN=$(get_admin_token)
if [ -n "$TOKEN" ]; then
    echo "✅ Token de acesso obtido com sucesso!"
    echo ""
    get_client_secret "$TOKEN"
else
    echo "❌ Falha ao obter token de acesso"
    exit 1
fi 