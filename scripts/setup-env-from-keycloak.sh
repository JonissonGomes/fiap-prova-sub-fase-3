#!/bin/bash

# Script para configurar variáveis de ambiente baseadas no Keycloak
# Obtém o client_secret dinamicamente e atualiza o docker-compose.yml

set -e

KEYCLOAK_URL="http://localhost:8080"
REALM="vehicle-sales"
CLIENT_ID="vehicle-sales-app"
ADMIN_USER="admin"
ADMIN_PASS="admin123"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

echo "🔧 Configurando variáveis de ambiente a partir do Keycloak..."
echo ""

# Verificar se o Keycloak está acessível
echo "🔍 Verificando se o Keycloak está acessível..."
if ! curl -s --connect-timeout 10 "$KEYCLOAK_URL/realms/master" > /dev/null 2>&1; then
    echo "❌ Keycloak não está acessível em $KEYCLOAK_URL"
    echo "💡 Certifique-se de que o Keycloak está rodando e tente novamente"
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
CLIENT_SECRET=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" | \
    jq -r '.[] | select(.clientId=="'$CLIENT_ID'") | .secret // empty')

if [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Erro: Client secret não encontrado para $CLIENT_ID"
    exit 1
fi

echo "✅ Client secret obtido com sucesso!"
echo "🔑 Client Secret: $CLIENT_SECRET"
echo ""

# Atualizar docker-compose.yml
echo "📝 Atualizando $DOCKER_COMPOSE_FILE..."
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    # Fazer backup do arquivo original
    cp "$DOCKER_COMPOSE_FILE" "$DOCKER_COMPOSE_FILE.backup"
    
    # Atualizar a linha do KEYCLOAK_CLIENT_SECRET
    sed -i.tmp "s/KEYCLOAK_CLIENT_SECRET=.*/KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET/" "$DOCKER_COMPOSE_FILE"
    rm "$DOCKER_COMPOSE_FILE.tmp"
    
    echo "✅ $DOCKER_COMPOSE_FILE atualizado com sucesso!"
    echo "📋 Backup salvo em: $DOCKER_COMPOSE_FILE.backup"
else
    echo "❌ Arquivo $DOCKER_COMPOSE_FILE não encontrado"
    exit 1
fi

# Criar/atualizar arquivo .env
echo "📝 Criando/atualizando arquivo $ENV_FILE..."
cat > "$ENV_FILE" << EOF
# Configurações do Keycloak - Gerado automaticamente
KEYCLOAK_URL=$KEYCLOAK_URL
KEYCLOAK_REALM=$REALM
KEYCLOAK_CLIENT_ID=$CLIENT_ID
KEYCLOAK_CLIENT_SECRET=$CLIENT_SECRET
KEYCLOAK_ADMIN=$ADMIN_USER
KEYCLOAK_ADMIN_PASSWORD=$ADMIN_PASS

# Configurações do MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=vehicle_sales_db
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB_NAME=auth_db

# Configurações do Redis
REDIS_URL=redis://localhost:6379

# Configurações da API
API_BASE_URL=http://localhost:8000
AUTH_SERVICE_URL=http://localhost:8002
CUSTOMER_SERVICE_URL=http://localhost:8003
SALES_SERVICE_URL=http://localhost:8001
PAYMENT_SERVICE_URL=http://localhost:8004

# Configurações do Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_AUTH_URL=http://localhost:8002

# Configurações de Segurança
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600

# Configurações de Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Configurações de Ambiente
NODE_ENV=development
ENVIRONMENT=dev
DEBUG=true

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

echo "✅ Arquivo $ENV_FILE criado com sucesso!"
echo ""

echo "🎉 Configuração concluída!"
echo "=================================="
echo "CLIENT_ID: $CLIENT_ID"
echo "CLIENT_SECRET: $CLIENT_SECRET"
echo "=================================="
echo ""
echo "💡 Próximos passos:"
echo "1. Reiniciar o auth-service: docker-compose restart auth-service"
echo "2. Aguardar alguns segundos para o serviço inicializar"
echo "3. Testar o login: curl -X POST http://localhost:8002/auth/login ..."
echo ""
echo "📝 Arquivos atualizados:"
echo "- $DOCKER_COMPOSE_FILE"
echo "- $ENV_FILE"
echo "- Backup: $DOCKER_COMPOSE_FILE.backup" 