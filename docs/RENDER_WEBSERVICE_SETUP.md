# Guia de Configuração do Web Service no Render

## Visão Geral

O Render agora oferece **Web Services** que permitem deploy direto de aplicações, com suporte a Docker e comandos customizados de build/start.

## Como Criar um Web Service

### 1. **Acessar o Render Dashboard**
1. Vá para [Render Dashboard](https://dashboard.render.com/)
2. Faça login na sua conta
3. Clique em **"New +"**
4. Selecione **"Web Service"**

### 2. **Conectar o Repositório**
1. Conecte sua conta GitHub
2. Selecione o repositório `fiap-prova-sub-fase-3`
3. Escolha a branch (main/master)

### 3. **Configurar o Build**

#### **Opção A: Usando Docker (Recomendado)**
```bash
# Build Command
docker build -t fiap-app .

# Start Command
docker run -p $PORT:8000 fiap-app
```

#### **Opção B: Build Customizado**
```bash
# Build Command
pip install -r requirements.txt && npm install && npm run build

# Start Command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 4. **Configurações do Web Service**

#### **Informações Básicas:**
- **Name**: `fiap-vehicle-system`
- **Environment**: `Python 3.11` ou `Docker`
- **Region**: Escolha a mais próxima (ex: Oregon)

#### **Build & Deploy:**
- **Build Command**: `docker build -t fiap-app .`
- **Start Command**: `docker run -p $PORT:8000 fiap-app`
- **Health Check Path**: `/health`

#### **Environment Variables:**
```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=fiap_db

# Keycloak
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=fiap
KEYCLOAK_CLIENT_ID=fiap-client
KEYCLOAK_CLIENT_SECRET=your-secret

# JWT
JWT_SECRET=your-jwt-secret

# Services URLs
AUTH_SERVICE_URL=http://localhost:8000
CORE_SERVICE_URL=http://localhost:8001
CUSTOMER_SERVICE_URL=http://localhost:8002
SALES_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
```

### 5. **Configurar Health Check**
- **Health Check Path**: `/health`
- **Health Check Timeout**: `5 seconds`

## Configuração do Docker

### **Dockerfile Principal**
```dockerfile
# Dockerfile na raiz do projeto
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose para Desenvolvimento**
```yaml
# docker-compose.yml
version: '3.8'

services:
  auth-service:
    build: ./auth-service
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
    depends_on:
      - mongodb

  core-service:
    build: ./core-service
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017

  customer-service:
    build: ./customer-service
    ports:
      - "8002:8002"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017

  sales-service:
    build: ./sales-service
    ports:
      - "8003:8003"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## Configuração do GitHub Actions

### **Secrets Necessários:**
1. **RENDER_API_KEY**: API Key do Render
2. **RENDER_SERVICE_ID**: ID do Web Service

### **Como Obter:**
1. **API Key**: 
   - Render Dashboard > Account Settings > API Keys
   - Clique em "New API Key"

2. **Service ID**:
   - No Web Service, copie o ID da URL
   - Ex: `https://dashboard.render.com/web/srv-abc123def456`
   - O ID é: `srv-abc123def456`

## Deploy Automático

### **Via GitHub Actions:**
O pipeline já está configurado para fazer deploy automático quando você fizer push para a branch `main`.

### **Via Render Dashboard:**
1. Vá para o Web Service
2. Clique em "Manual Deploy"
3. Escolha a branch
4. Clique em "Deploy"

### **Via API:**
```bash
curl -X POST "https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": "do_not_clear"}'
```

## Monitoramento

### **Logs:**
- Render Dashboard > Web Service > Logs
- Logs em tempo real
- Histórico de deploys

### **Métricas:**
- CPU e Memory usage
- Response time
- Error rate

### **Health Check:**
- Endpoint `/health` é verificado automaticamente
- Status do serviço é atualizado em tempo real

## Troubleshooting

### **Build Falha:**
1. Verifique os logs de build
2. Confirme se o Dockerfile está correto
3. Verifique se as dependências estão instaladas

### **Deploy Falha:**
1. Verifique os logs de deploy
2. Confirme se o Start Command está correto
3. Verifique se as variáveis de ambiente estão configuradas

### **Health Check Falha:**
1. Confirme se o endpoint `/health` está funcionando
2. Verifique se a aplicação está rodando na porta correta
3. Confirme se o Health Check Path está correto

## Próximos Passos

1. **Criar o Web Service** no Render
2. **Configurar as variáveis de ambiente**
3. **Fazer o primeiro deploy**
4. **Configurar o domínio customizado** (opcional)
5. **Configurar SSL** (automático no Render)

## Links Úteis

- [Render Documentation](https://render.com/docs)
- [Web Services Guide](https://render.com/docs/web-services)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Health Checks](https://render.com/docs/health-checks) 