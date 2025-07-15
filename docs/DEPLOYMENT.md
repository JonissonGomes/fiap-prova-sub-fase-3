# Guia de Deployment

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 

## Visão Geral

Este documento fornece instruções detalhadas para fazer o deployment do sistema de vendas de veículos em diferentes ambientes (desenvolvimento, staging e produção).

## Ambientes

### Desenvolvimento (Local)
- **Objetivo**: Desenvolvimento e testes locais
- **Infraestrutura**: Docker Compose
- **Banco de Dados**: MongoDB local
- **Autenticação**: Keycloak local

### Staging
- **Objetivo**: Testes de integração e validação
- **Infraestrutura**: Docker Swarm ou Kubernetes
- **Banco de Dados**: MongoDB Atlas ou cluster dedicado
- **Autenticação**: Keycloak dedicado

### Produção
- **Objetivo**: Ambiente de produção
- **Infraestrutura**: Kubernetes
- **Banco de Dados**: MongoDB Atlas com replicação
- **Autenticação**: Keycloak em cluster

## Configuração de Variáveis de Ambiente

### Estrutura de Arquivos de Ambiente

```
project/
├── .env.development
├── .env.staging
├── .env.production
├── auth-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── core-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
├── sales-service/
│   ├── .env
│   ├── .env.development
│   ├── .env.staging
│   └── .env.production
└── customer-service/
    ├── .env
    ├── .env.development
    ├── .env.staging
    └── .env.production
```

### Variáveis por Ambiente

#### Desenvolvimento (.env.development)

```bash
# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Auth Service
AUTH_SERVICE_URL=http://auth-service:8002
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=dev-secret
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Bancos de Dados
AUTH_MONGODB_URL=mongodb://auth-mongodb:27017
AUTH_MONGODB_DB=auth_db_dev
CORE_MONGODB_URL=mongodb://core-mongodb:27017
CORE_MONGODB_DB=core_db_dev
SALES_MONGODB_URL=mongodb://sales-mongodb:27017
SALES_MONGODB_DB=sales_db_dev
CUSTOMER_MONGODB_URL=mongodb://customer-mongodb:27017
CUSTOMER_MONGODB_DB=customer_db_dev

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Configurações de Segurança
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging (.env.staging)

```bash
# Ambiente
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Auth Service
AUTH_SERVICE_URL=https://auth-staging.vehiclesales.com
KEYCLOAK_URL=https://keycloak-staging.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales-staging
KEYCLOAK_CLIENT_ID=vehicle-sales-app-staging
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db_staging
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db_staging
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db_staging
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db_staging

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app-staging.vehiclesales.com,https://admin-staging.vehiclesales.com
```

#### Produção (.env.production)

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Auth Service
AUTH_SERVICE_URL=https://auth.vehiclesales.com
KEYCLOAK_URL=https://keycloak.vehiclesales.com
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}

# Bancos de Dados
AUTH_MONGODB_URL=${AUTH_MONGODB_URL}
AUTH_MONGODB_DB=auth_db
CORE_MONGODB_URL=${CORE_MONGODB_URL}
CORE_MONGODB_DB=core_db
SALES_MONGODB_URL=${SALES_MONGODB_URL}
SALES_MONGODB_DB=sales_db
CUSTOMER_MONGODB_URL=${CUSTOMER_MONGODB_URL}
CUSTOMER_MONGODB_DB=customer_db

# Usuário Admin Padrão
DEFAULT_ADMIN_EMAIL=${DEFAULT_ADMIN_EMAIL}
DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}

# Configurações de Segurança
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=1

# CORS
CORS_ORIGINS=https://app.vehiclesales.com,https://admin.vehiclesales.com

# Monitoramento
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
JAEGER_URL=http://jaeger:14268
```

## Docker Deployment

### Desenvolvimento Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd fiap-prova-sub-fase-3

# 2. Copiar arquivos de ambiente
cp .env.development .env
cp auth-service/.env.development auth-service/.env
cp core-service/.env.development core-service/.env
cp sales-service/.env.development sales-service/.env
cp customer-service/.env.development customer-service/.env

# 3. Construir e executar
make setup
make up

# 4. Verificar status
make status
```

### Docker Compose para Staging

```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  # Keycloak
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN}
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak
      - KC_DB_USERNAME=${KEYCLOAK_DB_USER}
      - KC_DB_PASSWORD=${KEYCLOAK_DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
    ports:
      - "8080:8080"
    depends_on:
      - keycloak-db
    command: start

  keycloak-db:
    image: postgres:15
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER=${KEYCLOAK_DB_USER}
      - POSTGRES_PASSWORD=${KEYCLOAK_DB_PASSWORD}
    volumes:
      - keycloak-db-data:/var/lib/postgresql/data

  # Auth Service
  auth-service:
    image: vehiclesales/auth-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${AUTH_MONGODB_URL}
      - KEYCLOAK_URL=${KEYCLOAK_URL}
    ports:
      - "8002:8002"
    depends_on:
      - keycloak
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Core Service
  core-service:
    image: vehiclesales/core-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CORE_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Sales Service
  sales-service:
    image: vehiclesales/sales-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${SALES_MONGODB_URL}
      - CORE_SERVICE_URL=${CORE_SERVICE_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8001:8001"
    depends_on:
      - core-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  # Customer Service
  customer-service:
    image: vehiclesales/customer-service:staging
    environment:
      - ENVIRONMENT=staging
      - MONGODB_URL=${CUSTOMER_MONGODB_URL}
      - AUTH_SERVICE_URL=${AUTH_SERVICE_URL}
    ports:
      - "8003:8003"
    depends_on:
      - auth-service
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

volumes:
  keycloak-db-data:
```

## Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vehiclesales
  labels:
    name: vehiclesales
```

### ConfigMaps

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vehiclesales
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  KEYCLOAK_REALM: "vehicle-sales"
  KEYCLOAK_CLIENT_ID: "vehicle-sales-app"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vehiclesales
type: Opaque
data:
  KEYCLOAK_CLIENT_SECRET: <base64-encoded-secret>
  KEYCLOAK_ADMIN_PASSWORD: <base64-encoded-password>
  JWT_SECRET_KEY: <base64-encoded-key>
  MONGODB_AUTH_URL: <base64-encoded-url>
  MONGODB_CORE_URL: <base64-encoded-url>
  MONGODB_SALES_URL: <base64-encoded-url>
  MONGODB_CUSTOMER_URL: <base64-encoded-url>
  DEFAULT_ADMIN_EMAIL: <base64-encoded-email>
  DEFAULT_ADMIN_PASSWORD: <base64-encoded-password>
```

### Deployments

```yaml
# k8s/auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: vehiclesales/auth-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: MONGODB_AUTH_URL
        - name: KEYCLOAK_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: KEYCLOAK_CLIENT_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 60
          periodSeconds: 30
```

### Services

```yaml
# k8s/auth-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: vehiclesales
spec:
  selector:
    app: auth-service
  ports:
    - protocol: TCP
      port: 8002
      targetPort: 8002
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vehiclesales-ingress
  namespace: vehiclesales
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vehiclesales.com
    secretName: vehiclesales-tls
  rules:
  - host: api.vehiclesales.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 8002
      - path: /vehicles
        pathType: Prefix
        backend:
          service:
            name: core-service
            port:
              number: 8000
      - path: /sales
        pathType: Prefix
        backend:
          service:
            name: sales-service
            port:
              number: 8001
      - path: /customers
        pathType: Prefix
        backend:
          service:
            name: customer-service
            port:
              number: 8003
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r auth-service/requirements.txt
        pip install -r core-service/requirements.txt
        pip install -r sales-service/requirements.txt
        pip install -r customer-service/requirements.txt
    
    - name: Run tests
      run: |
        cd auth-service && python -m pytest tests/ -v
        cd ../core-service && python -m pytest tests/ -v
        cd ../sales-service && python -m pytest tests/ -v
        cd ../customer-service && python -m pytest tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./auth-service
        push: true
        tags: vehiclesales/auth-service:latest
    
    - name: Build and push Core Service
      uses: docker/build-push-action@v4
      with:
        context: ./core-service
        push: true
        tags: vehiclesales/core-service:latest
    
    - name: Build and push Sales Service
      uses: docker/build-push-action@v4
      with:
        context: ./sales-service
        push: true
        tags: vehiclesales/sales-service:latest
    
    - name: Build and push Customer Service
      uses: docker/build-push-action@v4
      with:
        context: ./customer-service
        push: true
        tags: vehiclesales/customer-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v1
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/
        kubectl rollout status deployment/auth-service -n vehiclesales
        kubectl rollout status deployment/core-service -n vehiclesales
        kubectl rollout status deployment/sales-service -n vehiclesales
        kubectl rollout status deployment/customer-service -n vehiclesales
```

## Monitoramento

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'core-service'
    static_configs:
      - targets: ['core-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'customer-service'
    static_configs:
      - targets: ['customer-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Vehicle Sales System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## Backup e Disaster Recovery

### Backup do MongoDB

```bash
#!/bin/bash
# scripts/backup-mongodb.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb/$DATE"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup de cada banco
mongodump --uri="$AUTH_MONGODB_URL" --db=auth_db --out=$BACKUP_DIR/auth
mongodump --uri="$CORE_MONGODB_URL" --db=core_db --out=$BACKUP_DIR/core
mongodump --uri="$SALES_MONGODB_URL" --db=sales_db --out=$BACKUP_DIR/sales
mongodump --uri="$CUSTOMER_MONGODB_URL" --db=customer_db --out=$BACKUP_DIR/customer

# Compactar backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR.tar.gz s3://vehiclesales-backups/mongodb/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Restore do MongoDB

```bash
#!/bin/bash
# scripts/restore-mongodb.sh

BACKUP_FILE=$1
TEMP_DIR="/tmp/mongodb_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extrair backup
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Restaurar cada banco
mongorestore --uri="$AUTH_MONGODB_URL" --db=auth_db $TEMP_DIR/auth/auth_db
mongorestore --uri="$CORE_MONGODB_URL" --db=core_db $TEMP_DIR/core/core_db
mongorestore --uri="$SALES_MONGODB_URL" --db=sales_db $TEMP_DIR/sales/sales_db
mongorestore --uri="$CUSTOMER_MONGODB_URL" --db=customer_db $TEMP_DIR/customer/customer_db

# Limpar arquivos temporários
rm -rf $TEMP_DIR

echo "Restore completed from: $BACKUP_FILE"
```

## Troubleshooting

### Logs Centralizados

```bash
# Visualizar logs de todos os serviços
kubectl logs -f deployment/auth-service -n vehiclesales
kubectl logs -f deployment/core-service -n vehiclesales
kubectl logs -f deployment/sales-service -n vehiclesales
kubectl logs -f deployment/customer-service -n vehiclesales

# Logs agregados com stern
stern -n vehiclesales "auth-service|core-service|sales-service|customer-service"
```

### Health Checks

```bash
# Verificar saúde dos serviços
curl -f http://localhost:8002/health || echo "Auth Service DOWN"
curl -f http://localhost:8000/health || echo "Core Service DOWN"
curl -f http://localhost:8001/health || echo "Sales Service DOWN"
curl -f http://localhost:8003/health || echo "Customer Service DOWN"
```

### Comandos de Depuração

```bash
# Verificar conectividade entre serviços
kubectl exec -it deployment/sales-service -n vehiclesales -- curl http://core-service:8000/health

# Verificar configuração do Keycloak
kubectl exec -it deployment/auth-service -n vehiclesales -- curl http://keycloak:8080/health

# Verificar logs do banco de dados
kubectl logs -f deployment/mongodb -n vehiclesales
```

## Checklist de Deployment

### Pré-deployment
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados
- [ ] Backup do banco de dados
- [ ] Monitoramento configurado

### Durante o Deployment
- [ ] Verificar status dos pods
- [ ] Verificar logs dos serviços
- [ ] Testar endpoints críticos
- [ ] Verificar conectividade entre serviços

### Pós-deployment
- [ ] Testes de fumaça
- [ ] Verificar métricas
- [ ] Verificar alertas
- [ ] Documentar deployment
- [ ] Comunicar equipe 