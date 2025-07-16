# Guia de CI/CD - Sistema FIAP

Este documento descreve o pipeline completo de CI/CD implementado para o sistema de vendas de veículos da FIAP.

## 📋 Visão Geral

O pipeline de CI/CD automatiza todo o processo de desenvolvimento, desde testes até deploy em produção no Render.

### 🎯 Objetivos

- **Automatização**: Reduzir intervenção manual
- **Qualidade**: Garantir cobertura de testes mínima de 60%
- **Segurança**: Análise de vulnerabilidades automática
- **Deploy**: Deploy automático no Render
- **Monitoramento**: Health checks e logs centralizados

## 🔄 Pipeline de CI/CD

### 1. **Test Backend Services**
- Executa testes em todos os serviços Python
- Verifica cobertura mínima de 60%
- Gera relatórios de cobertura
- Upload para Codecov

### 2. **Test Frontend**
- Executa testes React/TypeScript
- Verifica linting
- Gera relatórios de cobertura
- Upload para Codecov

### 3. **Security Scan**
- Análise de vulnerabilidades com Bandit
- Gera relatório de segurança
- Upload de artefatos

### 4. **Build and Deploy**
- Build de imagens Docker
- Push para Docker Hub
- Deploy automático no Render

## 🛠️ Configuração

### Pré-requisitos

1. **GitHub Secrets**
   ```bash
   DOCKERHUB_USERNAME=sua_username
   DOCKERHUB_TOKEN=sua_token
   RENDER_API_KEY=sua_api_key
   RENDER_SERVICE_ID=seu_service_id
   ```

2. **Codecov**
   - Conectar repositório no Codecov
   - Configurar token de acesso

3. **Render**
   - Criar conta no Render
   - Configurar serviços
   - Obter API key

### Configuração Local

1. **Instalar dependências**
   ```bash
   # Backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Configurar health checks**
   ```bash
   python scripts/setup-health-checks.py
   ```

3. **Configurar variáveis de ambiente**
   ```bash
   export RENDER_API_KEY=sua_api_key
   python scripts/setup-render-env.py
   ```

## 📊 Cobertura de Testes

### Configuração

O arquivo `codecov.yml` define:
- **Target**: 60% de cobertura mínima
- **Threshold**: 5% de tolerância
- **Flags**: Separação por serviço
- **Ignore**: Arquivos não relevantes

### Execução Local

```bash
# Backend
cd auth-service
coverage run -m pytest tests/
coverage report --show-missing --fail-under=60

# Frontend
cd frontend
npm test -- --coverage --watchAll=false
```

## 🐳 Docker

### Imagens

- `fiap-auth-service:latest`
- `fiap-core-service:latest`
- `fiap-customer-service:latest`
- `fiap-payment-service:latest`
- `fiap-sales-service:latest`
- `fiap-frontend:latest`

### Build Local

```bash
# Build individual
docker build -t fiap-auth-service auth-service/

# Build todos
docker-compose -f docker-compose.prod.yml build
```

## 🚀 Deploy no Render

### Configuração

O arquivo `render.yaml` define:
- **6 serviços web** (Python)
- **1 serviço estático** (Frontend)
- **1 banco de dados** (MongoDB)
- **Health checks** automáticos
- **Variáveis de ambiente**

### Serviços

1. **fiap-auth-service**
   - Porta: 8001
   - Health: `/health`

2. **fiap-core-service**
   - Porta: 8002
   - Health: `/health`

3. **fiap-customer-service**
   - Porta: 8003
   - Health: `/health`

4. **fiap-payment-service**
   - Porta: 8004
   - Health: `/health`

5. **fiap-sales-service**
   - Porta: 8005
   - Health: `/health`

6. **fiap-frontend**
   - Porta: 3000
   - Build: `npm run build`

### Deploy Automático

O pipeline executa automaticamente quando:
- Push para `main`
- Push para `develop`
- Pull Request para `main`

## 🔒 Segurança

### Análise Automática

- **Bandit**: Análise de vulnerabilidades Python
- **Rate Limiting**: Nginx com limites de requisição
- **Security Headers**: Headers de segurança configurados
- **SSL/TLS**: Configuração para HTTPS

### Configurações

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=frontend:10m rate=30r/s;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
```

## 📈 Monitoramento

### Health Checks

Todos os serviços expõem endpoint `/health`:

```json
{
  "status": "healthy",
  "service": "auth-service",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Logs

- **Render**: Logs centralizados
- **Nginx**: Logs de acesso e erro
- **Aplicação**: Logs estruturados

## 🔧 Troubleshooting

### Problemas Comuns

1. **Cobertura insuficiente**
   ```bash
   # Verificar cobertura local
   coverage report --show-missing
   ```

2. **Deploy falhou**
   ```bash
   # Verificar logs no Render
   # Verificar variáveis de ambiente
   # Verificar health checks
   ```

3. **Testes falharam**
   ```bash
   # Executar testes localmente
   pytest tests/ -v
   ```

### Comandos Úteis

```bash
# Executar pipeline local
python scripts/setup-health-checks.py
python scripts/setup-render-env.py

# Verificar status dos serviços
curl http://localhost:8001/health
curl http://localhost:8002/health

# Build e deploy local
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Próximos Passos

1. **Implementar testes E2E**
2. **Adicionar monitoramento com Prometheus**
3. **Configurar alertas**
4. **Implementar rollback automático**
5. **Adicionar testes de performance**

## 🤝 Contribuição

Para contribuir com o pipeline:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Execute os testes localmente
5. Abra um Pull Request

O pipeline será executado automaticamente e você receberá feedback sobre:
- Cobertura de testes
- Análise de segurança
- Build e deploy 