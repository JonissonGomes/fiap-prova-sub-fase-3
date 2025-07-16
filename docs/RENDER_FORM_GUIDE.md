# Guia para Preencher o Formulário do Render Web Service

## **Configuração Completa do Formulário**

### **1. Informações Básicas**
```
Name: fiap-vehicle-system
Project: (deixe vazio por enquanto)
Language: Docker ✅
Branch: master ✅
Region: Singapore (Southeast Asia) ✅
```

### **2. Configurações de Build**
```
Root Directory: (deixe vazio)
Dockerfile Path: ./Dockerfile ✅
Instance Type: Free (para começar)
```

### **3. Environment Variables**
Adicione estas variáveis uma por uma:

#### **MongoDB:**
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=fiap_db
```

#### **Keycloak:**
```
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=fiap
KEYCLOAK_CLIENT_ID=fiap-client
KEYCLOAK_CLIENT_SECRET=your-secret-here
```

#### **JWT:**
```
JWT_SECRET=your-super-secret-jwt-key-here
```

#### **Services URLs:**
```
AUTH_SERVICE_URL=http://localhost:8000
CORE_SERVICE_URL=http://localhost:8001
CUSTOMER_SERVICE_URL=http://localhost:8002
SALES_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
```

#### **Porta do Render:**
```
PORT=8000
```

### **4. Health Check**
```
Health Check Path: /health ✅
```

### **5. Docker Command**
```
Docker Command: make start-production
```

### **6. Configurações Avançadas**
```
Auto-Deploy: On Commit ✅
Registry Credential: No credential ✅
Docker Build Context Directory: . ✅
```

## **Como Adicionar Environment Variables**

1. Clique em **"Add Environment Variable"**
2. Para cada variável:
   - **NAME:** Nome da variável (ex: `MONGODB_URL`)
   - **VALUE:** Valor da variável (ex: `mongodb://localhost:27017`)
3. Clique em **"Add"**
4. Repita para todas as variáveis

## **Exemplo de Preenchimento**

### **Passo 1: Informações Básicas**
- ✅ **Name:** `fiap-vehicle-system`
- ✅ **Language:** `Docker`
- ✅ **Branch:** `master`
- ✅ **Region:** `Singapore (Southeast Asia)`

### **Passo 2: Build**
- ✅ **Dockerfile Path:** `./Dockerfile`
- ✅ **Instance Type:** `Free`

### **Passo 3: Environment Variables**
Adicione uma por uma:

```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=fiap_db
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=fiap
KEYCLOAK_CLIENT_ID=fiap-client
KEYCLOAK_CLIENT_SECRET=your-secret-here
JWT_SECRET=your-super-secret-jwt-key-here
AUTH_SERVICE_URL=http://localhost:8000
CORE_SERVICE_URL=http://localhost:8001
CUSTOMER_SERVICE_URL=http://localhost:8002
SALES_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
PORT=8000
```

### **Passo 4: Health Check**
- ✅ **Health Check Path:** `/health`

### **Passo 5: Docker Command**
- ✅ **Docker Command:** `make start-production`

## **Após o Deploy**

### **1. Obter o Service ID**
Após criar o Web Service, copie o ID da URL:
```
https://dashboard.render.com/web/srv-abc123def456
```
O Service ID é: `srv-abc123def456`

### **2. Configurar GitHub Secrets**
Vá para: `https://github.com/JonissonGomes/fiap-prova-sub-fase-3/settings/secrets/actions`

Adicione:
- `RENDER_API_KEY`: Sua API Key do Render
- `RENDER_SERVICE_ID`: O Service ID que você copiou

### **3. Testar o Deploy**
1. Faça push para a branch `master`
2. O deploy automático será acionado
3. Acompanhe os logs no Render Dashboard

## **Troubleshooting**

### **Se o build falhar:**
1. Verifique se o Dockerfile está na raiz
2. Confirme se o Makefile tem o comando `start-production`
3. Verifique se as variáveis de ambiente estão corretas

### **Se o health check falhar:**
1. Confirme se o endpoint `/health` está funcionando
2. Verifique se a aplicação está rodando na porta correta
3. Aguarde alguns minutos para o primeiro deploy

### **Se as variáveis não carregarem:**
1. Verifique se os nomes estão corretos
2. Confirme se não há espaços extras
3. Reinicie o serviço após adicionar variáveis

## **Próximos Passos**

1. ✅ Preencher o formulário conforme este guia
2. ✅ Criar o Web Service
3. ✅ Copiar o Service ID
4. ✅ Configurar GitHub Secrets
5. ✅ Fazer push para master
6. ✅ Acompanhar o deploy automático

## **Links Úteis**

- [Render Dashboard](https://dashboard.render.com/web)
- [GitHub Secrets](https://github.com/JonissonGomes/fiap-prova-sub-fase-3/settings/secrets/actions)
- [Render API Keys](https://dashboard.render.com/account/api-keys) 