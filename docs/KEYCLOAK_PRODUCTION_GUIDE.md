# Guia de Keycloak para Produção

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 

## 📋 Visão Geral

Este guia explica como configurar e obter credenciais do Keycloak em diferentes ambientes, incluindo produção.

## 🚀 Configuração por Ambiente

### 1. Development (Desenvolvimento)
```bash
# Usar o script padrão para desenvolvimento local
make keycloak-secret

# Ou usar o script de produção com ambiente development
make keycloak-secret-dev
```

### 2. Staging (Homologação)
```bash
# Configurar arquivo .env.staging
cp .env.staging.example .env.staging
# Editar .env.staging com suas configurações

# Obter client secret
make keycloak-secret-staging
```

### 3. Production (Produção)
```bash
# Configurar arquivo .env.production
cp .env.production.example .env.production
# Editar .env.production com suas configurações

# Obter client secret
make keycloak-secret-prod
```

## 🔧 Configuração dos Arquivos de Ambiente

### .env.production
```bash
# URL do Keycloak em produção (HTTPS obrigatório)
KEYCLOAK_URL=https://keycloak.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin do Keycloak (MUDE ESTAS CREDENCIAIS!)
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=SUA_SENHA_SUPER_SEGURA_AQUI

# URLs válidas para produção
KEYCLOAK_VALID_REDIRECT_URIS=https://app.suaempresa.com/*
KEYCLOAK_WEB_ORIGINS=https://app.suaempresa.com
```

### .env.staging
```bash
# URL do Keycloak em staging
KEYCLOAK_URL=https://keycloak-staging.suaempresa.com

# Realm do Keycloak
KEYCLOAK_REALM=vehicle-sales

# Client ID
KEYCLOAK_CLIENT_ID=vehicle-sales-app

# Credenciais do admin
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASS=staging_admin_password

# URLs válidas para staging
KEYCLOAK_VALID_REDIRECT_URIS=https://app-staging.suaempresa.com/*,http://localhost:3000/*
KEYCLOAK_WEB_ORIGINS=https://app-staging.suaempresa.com,http://localhost:3000
```

## 🔒 Validações de Segurança

### Para Produção
O script automaticamente valida:

1. **Credenciais Padrão**: Rejeita senhas como "admin123"
2. **URLs Localhost**: Rejeita URLs localhost em produção
3. **HTTPS**: Valida certificados SSL em produção
4. **Timeouts**: Configura timeouts apropriados

### Exemplo de Erro de Validação
```bash
❌ ERRO: Credenciais padrão não são seguras para produção!
💡 Configure KEYCLOAK_ADMIN_PASS com uma senha segura no arquivo .env.production
```

## 🛠️ Uso dos Scripts

### Script de Produção
```bash
# Sintaxe
./scripts/get-keycloak-client-secret-prod.sh [environment]

# Exemplos
./scripts/get-keycloak-client-secret-prod.sh production
./scripts/get-keycloak-client-secret-prod.sh staging
./scripts/get-keycloak-client-secret-prod.sh development
```

### Comandos Make
```bash
make keycloak-secret-prod     # Produção
make keycloak-secret-staging  # Staging
make keycloak-secret-dev      # Development
make keycloak-secret          # Development (script original)
```

## 📁 Arquivos de Saída

### Localização
Os client secrets são salvos em:
- `/tmp/keycloak-credentials-production.env`
- `/tmp/keycloak-credentials-staging.env`
- `/tmp/keycloak-credentials-development.env`

### Formato do Arquivo
```bash
# Keycloak credentials for production environment
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=abc123def456...
KEYCLOAK_URL=https://keycloak.suaempresa.com
KEYCLOAK_REALM=vehicle-sales
```

## 🔐 Boas Práticas de Segurança

### 1. Credenciais Seguras
```bash
# ❌ Não use
KEYCLOAK_ADMIN_PASS=admin123

# ✅ Use
KEYCLOAK_ADMIN_PASS=MyV3ryS3cur3P@ssw0rd!2024
```

### 2. URLs HTTPS
```bash
# ❌ Não use em produção
KEYCLOAK_URL=http://keycloak.suaempresa.com

# ✅ Use em produção
KEYCLOAK_URL=https://keycloak.suaempresa.com
```

### 3. Gestão de Secrets
- Use ferramentas como HashiCorp Vault, AWS Secrets Manager
- Rotacione client secrets periodicamente
- Monitore uso de tokens no Keycloak
- Use variáveis de ambiente no CI/CD

### 4. Configuração de Rede
```bash
# Configurar firewall para permitir apenas IPs necessários
# Usar VPN ou bastion hosts para acesso administrativo
# Configurar load balancer com SSL termination
```

## 🚢 Deploy em Diferentes Plataformas

### Docker Compose (Produção)
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASS}
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=${DB_USERNAME}
      - KC_DB_PASSWORD=${DB_PASSWORD}
      - KC_HOSTNAME=${KEYCLOAK_HOSTNAME}
      - KC_HTTPS_CERTIFICATE_FILE=/opt/keycloak/conf/server.crt
      - KC_HTTPS_CERTIFICATE_KEY_FILE=/opt/keycloak/conf/server.key
    volumes:
      - ./certs:/opt/keycloak/conf
    ports:
      - "8080:8080"
      - "8443:8443"
    depends_on:
      - postgres
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
spec:
  replicas: 3
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:23.0.0
        env:
        - name: KEYCLOAK_ADMIN
          value: "admin"
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: keycloak-secret
              key: admin-password
        ports:
        - containerPort: 8080
        - containerPort: 8443
```

### AWS ECS/Fargate
```json
{
  "family": "keycloak",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "keycloak",
      "image": "quay.io/keycloak/keycloak:23.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KC_DB",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "KEYCLOAK_ADMIN_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:keycloak-admin-password"
        }
      ]
    }
  ]
}
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de SSL
```bash
❌ curl: (60) SSL certificate problem: unable to get local issuer certificate
```
**Solução**: Configurar certificados SSL corretamente ou usar `-k` para staging

#### 2. Timeout de Conexão
```bash
❌ Keycloak não está acessível em https://keycloak.suaempresa.com
```
**Solução**: Verificar firewall, DNS, e se o Keycloak está rodando

#### 3. Credenciais Inválidas
```bash
❌ Erro ao obter token de acesso: {"error":"invalid_grant"}
```
**Solução**: Verificar KEYCLOAK_ADMIN_USER e KEYCLOAK_ADMIN_PASS

#### 4. Client Não Encontrado
```bash
❌ Client 'vehicle-sales-app' não encontrado no realm 'vehicle-sales'
```
**Solução**: Criar o client manualmente ou executar setup script

### Logs Úteis
```bash
# Logs do Keycloak
docker-compose logs -f keycloak

# Teste de conectividade
curl -v https://keycloak.suaempresa.com/realms/master

# Verificar certificados SSL
openssl s_client -connect keycloak.suaempresa.com:443
```

## 📊 Monitoramento

### Métricas Importantes
- Taxa de autenticação
- Tempo de resposta dos tokens
- Falhas de autenticação
- Uso de CPU/memória
- Conexões de banco de dados

### Ferramentas Recomendadas
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Datadog

## 🔄 Rotação de Secrets

### Processo Recomendado
1. Gerar novo client secret no Keycloak
2. Atualizar aplicações com novo secret
3. Verificar funcionamento
4. Remover secret antigo
5. Documentar a mudança

### Script de Rotação
```bash
#!/bin/bash
# Exemplo de script de rotação
OLD_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)
./scripts/get-keycloak-client-secret-prod.sh production
NEW_SECRET=$(cat /tmp/keycloak-credentials-production.env | grep CLIENT_SECRET | cut -d'=' -f2)

echo "Secret rotacionado de $OLD_SECRET para $NEW_SECRET"
```

## 📚 Recursos Adicionais

- [Documentação Oficial do Keycloak](https://www.keycloak.org/documentation)
- [Guia de Produção do Keycloak](https://www.keycloak.org/server/configuration-production)
- [Keycloak Security Best Practices](https://www.keycloak.org/docs/latest/securing_apps/)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_performance-tuning) 