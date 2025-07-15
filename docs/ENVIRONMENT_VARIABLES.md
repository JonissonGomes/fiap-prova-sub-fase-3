# Guia de Variáveis de Ambiente

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 

## Visão Geral

Este documento detalha todas as variáveis de ambiente necessárias para configurar o sistema de vendas de veículos em diferentes ambientes.

## Estrutura de Configuração

```mermaid
graph TB
    subgraph "Configuração por Ambiente"
        DEV[Development<br/>.env.development]
        STG[Staging<br/>.env.staging]
        PROD[Production<br/>.env.production]
    end
    
    subgraph "Configuração por Serviço"
        AUTH[Auth Service<br/>auth-service/.env]
        CORE[Core Service<br/>core-service/.env]
        SALES[Sales Service<br/>sales-service/.env]
        CUSTOMER[Customer Service<br/>customer-service/.env]
    end
    
    subgraph "Configuração Global"
        DOCKER[docker-compose.yml]
        K8S[k8s/configmap.yaml]
        SECRETS[k8s/secrets.yaml]
    end
    
    DEV --> AUTH
    DEV --> CORE
    DEV --> SALES
    DEV --> CUSTOMER
    
    AUTH --> DOCKER
    CORE --> DOCKER
    SALES --> DOCKER
    CUSTOMER --> DOCKER
    
    DOCKER --> K8S
    K8S --> SECRETS
```

## Variáveis Globais

### Ambiente e Debug

| Variável | Descrição | Valores | Padrão | Obrigatória |
|----------|-----------|---------|---------|-------------|
| `ENVIRONMENT` | Ambiente de execução | `development`, `staging`, `production` | `development` | ✅ |
| `DEBUG` | Modo debug | `true`, `false` | `false` | ❌ |
| `LOG_LEVEL` | Nível de log | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

### Exemplo:
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

## Auth Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://auth-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `auth_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `users` | ✅ |

### Configuração do Keycloak

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `KEYCLOAK_URL` | URL do servidor Keycloak | `http://keycloak:8080` | ✅ |
| `KEYCLOAK_REALM` | Nome do realm | `vehicle-sales` | ✅ |
| `KEYCLOAK_CLIENT_ID` | ID do cliente | `vehicle-sales-app` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente | `your-client-secret` | ✅ |
| `KEYCLOAK_ADMIN` | Usuário admin do Keycloak | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin | `admin123` | ✅ |

### Configuração JWT

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `JWT_SECRET_KEY` | Chave secreta para JWT | `your-secret-key` | ✅ |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | ❌ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do access token (min) | `30` | ❌ |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Expiração do refresh token (dias) | `7` | ❌ |

### Usuário Administrador Padrão

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | `admin@vehiclesales.com` | ✅ |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | `admin123` | ✅ |

### Exemplo Completo - Auth Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://auth-mongodb:27017
MONGODB_DB_NAME=auth_db
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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Core Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://core-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `core_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `vehicles` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Core Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://core-mongodb:27017
MONGODB_DB_NAME=core_db
MONGODB_COLLECTION=vehicles

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Sales Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://sales-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `sales_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `sales` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `CORE_SERVICE_URL` | URL do Core Service | `http://core-service:8000` | ✅ |
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |
| `CUSTOMER_SERVICE_URL` | URL do Customer Service | `http://customer-service:8003` | ✅ |

### Exemplo Completo - Sales Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://sales-mongodb:27017
MONGODB_DB_NAME=sales_db
MONGODB_COLLECTION=sales

# Serviços
CORE_SERVICE_URL=http://core-service:8000
AUTH_SERVICE_URL=http://auth-service:8002
CUSTOMER_SERVICE_URL=http://customer-service:8003

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Customer Service

### Configuração do MongoDB

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `MONGODB_URL` | URL de conexão do MongoDB | `mongodb://customer-mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | Nome do banco de dados | `customer_db` | ✅ |
| `MONGODB_COLLECTION` | Nome da coleção | `customers` | ✅ |

### Configuração de Serviços

| Variável | Descrição | Exemplo | Obrigatória |
|----------|-----------|---------|-------------|
| `AUTH_SERVICE_URL` | URL do Auth Service | `http://auth-service:8002` | ✅ |

### Exemplo Completo - Customer Service (.env)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URL=mongodb://customer-mongodb:27017
MONGODB_DB_NAME=customer_db
MONGODB_COLLECTION=customers

# Serviços
AUTH_SERVICE_URL=http://auth-service:8002

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Configuração por Ambiente

### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# URLs dos Serviços (Docker Compose)
AUTH_SERVICE_URL=http://auth-service:8002
CORE_SERVICE_URL=http://core-service:8000
SALES_SERVICE_URL=http://sales-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8003

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret-change-in-production
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# MongoDB URLs
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
CORE_MONGODB_URL=mongodb://core-mongodb:27017
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017

# Database Names
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_DB=customer_db_dev

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
CORE_SERVICE_URL=https://core-staging.vehiclesales.com
SALES_SERVICE_URL=https://sales-staging.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer-staging.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas ou cluster dedicado)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_DB=customer_db_staging

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# URLs dos Serviços
AUTH_SERVICE_URL=https://auth.vehiclesales.com
CORE_SERVICE_URL=https://core.vehiclesales.com
SALES_SERVICE_URL=https://sales.vehiclesales.com
CUSTOMER_SERVICE_URL=https://customer.vehiclesales.com

# Keycloak
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# MongoDB URLs (MongoDB Atlas com replicação)
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
CORE_MONGODB_URL=${CORE_MONGODB_URL}
SALES_MONGODB_URL=${SALES_MONGODB_URL}
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}

# Database Names
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_DB=core_db
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_DB=customer_db

# JWT (configurações mais restritivas)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268

# Alertas
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
EMAIL_USERNAME=${EMAIL_USERNAME}
EMAIL_PASSWORD=${EMAIL_PASSWORD}
```

## Variáveis Sensíveis (Secrets)

### Para Kubernetes

```bash
# Encode em base64 antes de adicionar ao secrets.yaml
echo -n "your-secret-value" | base64
```

### Lista de Secrets

| Variável | Descrição | Tipo |
|----------|-----------|------|
| `KEYCLOAK_CLIENT_SECRET` | Secret do cliente Keycloak | String |
| `KEYCLOAK_ADMIN_PASSWORD` | Senha do admin Keycloak | String |
| `JWT_SECRET_KEY` | Chave secreta JWT | String |
| `AUTH_MONGODB_URL` | URL completa do MongoDB Auth | String |
| `CORE_MONGODB_URL` | URL completa do MongoDB Core | String |
| `SALES_MONGODB_URL` | URL completa do MongoDB Sales | String |
| `CUSTOMER_MONGODB_URL` | URL completa do MongoDB Customer | String |
| `DEFAULT_ADMIN_EMAIL` | Email do admin padrão | String |
| `DEFAULT_ADMIN_PASSWORD` | Senha do admin padrão | String |

### Exemplo de Secret para MongoDB Atlas

```bash
# Formato da URL do MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

## Configuração Automática

### Script de Setup

```bash
#!/bin/bash
# scripts/setup-env.sh

ENVIRONMENT=${1:-development}

echo "Configurando ambiente: $ENVIRONMENT"

# Copiar arquivos de ambiente
cp .env.$ENVIRONMENT .env

# Copiar para cada serviço
for service in auth-service core-service sales-service customer-service; do
    if [ -f $service/.env.$ENVIRONMENT ]; then
        cp $service/.env.$ENVIRONMENT $service/.env
        echo "Configurado $service para $ENVIRONMENT"
    fi
done

echo "Configuração concluída para $ENVIRONMENT"
```

### Uso do Script

```bash
# Configurar para desenvolvimento
./scripts/setup-env.sh development

# Configurar para staging
./scripts/setup-env.sh staging

# Configurar para produção
./scripts/setup-env.sh production
```

## Validação de Variáveis

### Script de Validação

```bash
#!/bin/bash
# scripts/validate-env.sh

REQUIRED_VARS=(
    "ENVIRONMENT"
    "MONGODB_URL"
    "KEYCLOAK_URL"
    "KEYCLOAK_CLIENT_SECRET"
    "JWT_SECRET_KEY"
    "DEFAULT_ADMIN_EMAIL"
    "DEFAULT_ADMIN_PASSWORD"
)

echo "Validando variáveis de ambiente..."

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável obrigatória não definida: $var"
        exit 1
    else
        echo "✅ $var: definida"
    fi
done

echo "✅ Todas as variáveis obrigatórias estão definidas"
```

## Boas Práticas

### Segurança

1. **Nunca commitar secrets**: Use `.gitignore` para arquivos `.env`
2. **Usar valores diferentes por ambiente**: Especialmente para JWT_SECRET_KEY
3. **Rotacionar secrets regularmente**: Principalmente em produção
4. **Usar ferramentas de gestão de secrets**: HashiCorp Vault, AWS Secrets Manager

### Organização

1. **Prefixos consistentes**: Use prefixos para agrupar variáveis relacionadas
2. **Documentação**: Sempre documente novas variáveis
3. **Validação**: Implemente validação de variáveis obrigatórias
4. **Defaults sensatos**: Forneça valores padrão quando apropriado

### Monitoramento

1. **Logs de configuração**: Registre (sem expor secrets) as configurações carregadas
2. **Health checks**: Verifique conectividade com serviços externos
3. **Alertas**: Configure alertas para falhas de configuração

## Troubleshooting

### Problemas Comuns

1. **Variável não definida**
   ```bash
   # Verificar se a variável está definida
   echo $VARIABLE_NAME
   
   # Verificar todas as variáveis do ambiente
   env | grep VEHICLE
   ```

2. **Conectividade com MongoDB**
   ```bash
   # Testar conexão
   mongosh "$MONGODB_URL"
   ```

3. **Conectividade com Keycloak**
   ```bash
   # Testar endpoint
   curl -f "$KEYCLOAK_URL/health" || echo "Keycloak não disponível"
   ```

4. **Problemas de CORS**
   ```bash
   # Verificar configuração
   echo $CORS_ORIGINS
   ```

### Logs de Debug

```bash
# Habilitar logs detalhados
export DEBUG=true
export LOG_LEVEL=DEBUG

# Executar serviço
python -m app.main
``` 