# Guia de Deploy - Arquitetura Unificada

## Visão Geral

Esta documentação descreve como fazer deploy da arquitetura unificada onde:
- **Backend**: Todos os microserviços rodando em um único Web Service no Render
- **Frontend**: Deploy separado na Vercel

## Arquitetura

```
┌─────────────────┐    ┌──────────────────────────────┐
│                 │    │                              │
│   Vercel        │    │         Render               │
│   (Frontend)    │───▶│   (Backend Unificado)        │
│                 │    │                              │
│  React App      │    │  ┌─────────────────────────┐ │
│                 │    │  │      Nginx Proxy        │ │
└─────────────────┘    │  └─────────────────────────┘ │
                       │  ┌─────────────────────────┐ │
                       │  │   Auth Service :8002    │ │
                       │  │   Core Service :8000    │ │
                       │  │   Sales Service :8001   │ │
                       │  │ Customer Service :8003  │ │
                       │  └─────────────────────────┘ │
                       └──────────────────────────────┘
```

## Deploy do Backend (Render)

### 1. Preparação

1. **Arquivos necessários**:
   - `Dockerfile.unified` - Container unificado
   - `nginx.unified.conf` - Proxy reverso
   - `supervisor.unified.conf` - Gerenciador de processos
   - `start-unified.sh` - Script de inicialização
   - `render.unified.yaml` - Configuração do Render

### 2. Configuração no Render

1. **Criar Web Service**:
   ```bash
   # No dashboard do Render
   - New Web Service
   - Connect GitHub repository
   - Use render.unified.yaml
   ```

2. **Variáveis de Ambiente**:
   ```bash
   # Obrigatórias
   MONGODB_URL=mongodb://...
   REDIS_URL=redis://...
   
   # Keycloak
   KEYCLOAK_URL=https://...
   KEYCLOAK_REALM=fiap
   KEYCLOAK_CLIENT_ID=fiap-client
   KEYCLOAK_CLIENT_SECRET=***
   
   # Opcional
   ENVIRONMENT=production
   FRONTEND_URL=https://fiap-frontend.vercel.app
   ```

3. **Bancos de Dados**:
   - MongoDB: Plan Starter ($6/mês)
   - Redis: Plan Starter ($10/mês)

### 3. Custos Estimados (Render)

```bash
Web Service (Starter): $7/mês
MongoDB (Starter):     $6/mês  
Redis (Starter):       $10/mês
─────────────────────────────
Total:                 $23/mês
```

## Deploy do Frontend (Vercel)

### 1. Configuração

1. **Variáveis de Ambiente na Vercel**:
   ```bash
   REACT_APP_BACKEND_URL=https://fiap-unified-backend.onrender.com
   ```

2. **Deploy**:
   ```bash
   # Conectar repositório no Vercel
   # Deploy automático do diretório /frontend
   ```

### 2. Custos

```bash
Vercel (Hobby): $0/mês (até 100GB bandwidth)
```

## Endpoints da API Unificada

### Base URL
```
https://fiap-unified-backend.onrender.com
```

### Rotas Disponíveis

```bash
# Health Check
GET /health

# Auth Service
POST /auth/login
POST /auth/register
GET  /auth/me

# Core Service (Vehicles)
GET    /vehicles
POST   /vehicles
GET    /vehicles/{id}
PUT    /vehicles/{id}
DELETE /vehicles/{id}

# Sales Service
GET    /sales
POST   /sales
GET    /sales/{id}
PUT    /sales/{id}
PATCH  /sales/{id}/status

# Customer Service
GET    /customers
POST   /customers
GET    /customers/{id}
PUT    /customers/{id}
DELETE /customers/{id}

# Documentação
GET /docs
GET /openapi.json
```

## Monitoramento

### 1. Health Checks

```bash
# Verificar status geral
curl https://fiap-unified-backend.onrender.com/health

# Resposta esperada
{
  "status": "healthy",
  "service": "unified-backend",
  "timestamp": "2025-01-XX..."
}
```

### 2. Logs

```bash
# No Render Dashboard
- Acessar Web Service
- Aba "Logs"
- Filtrar por serviço específico
```

### 3. Métricas

```bash
# Render Dashboard
- CPU Usage
- Memory Usage  
- Response Time
- Error Rate
```

## Troubleshooting

### Problemas Comuns

1. **Cold Start Lento**:
   - Normal no Render (plano gratuito)
   - Considerar upgrade para Starter ($7/mês)

2. **Erro de CORS**:
   - Verificar FRONTEND_URL nas variáveis
   - Confirmar configuração do Nginx

3. **Timeout de Conexão**:
   - Verificar MongoDB_URL e REDIS_URL
   - Aguardar até 2 minutos para cold start

4. **Serviço Não Responde**:
   ```bash
   # Verificar logs específicos
   - Auth Service: /var/log/supervisor/auth-service.err.log
   - Core Service: /var/log/supervisor/core-service.err.log
   - Sales Service: /var/log/supervisor/sales-service.err.log
   - Customer Service: /var/log/supervisor/customer-service.err.log
   ```

### Comandos de Debug

```bash
# Testar conectividade
curl -I https://fiap-unified-backend.onrender.com/health

# Testar endpoint específico
curl https://fiap-unified-backend.onrender.com/vehicles

# Verificar CORS
curl -H "Origin: https://fiap-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://fiap-unified-backend.onrender.com/vehicles
```

## Rollback

### Em caso de problemas

1. **Render**:
   - Dashboard → Web Service → Deploys
   - Selecionar deploy anterior → "Redeploy"

2. **Vercel**:
   - Dashboard → Project → Deployments  
   - Selecionar deployment anterior → "Promote to Production"

## Próximos Passos

1. **Monitoramento Avançado**:
   - Configurar alertas no Render
   - Integrar com Datadog/New Relic

2. **Performance**:
   - Upgrade para Professional ($19/mês) se necessário
   - Implementar cache Redis

3. **Segurança**:
   - Configurar HTTPS obrigatório
   - Implementar rate limiting mais robusto
   - Configurar firewall no Render

## Custos Totais

```bash
Backend (Render):  $23/mês
Frontend (Vercel): $0/mês
─────────────────────────
Total:             $23/mês
```

**vs Arquitetura Anterior (múltiplos services):**
```bash
5 Web Services: 5 × $7 = $35/mês
MongoDB:        $6/mês
Redis:          $10/mês  
─────────────────────────
Total:          $51/mês
```

**Economia: $28/mês (55% menos)** 