# Guia de Início Rápido - Keycloak

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 

## 🚀 Configuração Rápida (5 minutos)

### 1. Iniciar Keycloak
```bash
# Iniciar o Keycloak
make keycloak

# Aguardar inicialização (pode levar 2-3 minutos)
# Acompanhar logs:
make keycloak-logs
```

### 2. Verificar se está funcionando
```bash
# Testar conectividade
curl http://localhost:8080/realms/master

# Deve retornar um JSON com informações do realm
```

### 3. Configurar automaticamente
```bash
# Executar configuração automática
make keycloak-setup

# Aguardar mensagem de sucesso
```

### 4. Obter client secret
```bash
# Obter o client secret
make keycloak-secret

# Verificar se foi criado
cat /tmp/keycloak-credentials-development.env
```

### 5. Testar autenticação
```bash
# Testar login
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Deve retornar access_token e refresh_token
```

## 🔧 Configuração Manual (se automática falhar)

### 1. Acessar Console Admin
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### 2. Criar Realm
1. Clique em "Create Realm"
2. Nome: `vehicle-sales`
3. Clique em "Create"

### 3. Criar Client
1. Vá para "Clients" → "Create client"
2. Client ID: `vehicle-sales-app`
3. Client type: `OpenID Connect`
4. Clique em "Next"
5. Client authentication: `ON`
6. Standard flow: `ON`
7. Direct access grants: `ON`
8. Clique em "Save"

### 4. Configurar Client
1. Na aba "Settings":
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
2. Clique em "Save"

### 5. Obter Client Secret
1. Vá para aba "Credentials"
2. Copie o "Client secret"
3. Adicione ao arquivo `.env` do auth-service

### 6. Criar Roles
1. Vá para "Realm roles" → "Create role"
2. Criar roles:
   - `ADMIN`
   - `SALES`
   - `CUSTOMER`

### 7. Criar Usuário Admin
1. Vá para "Users" → "Create user"
2. Username: `admin`
3. Email: `admin@example.com`
4. Clique em "Create"
5. Na aba "Credentials":
   - Password: `admin123`
   - Temporary: `OFF`
6. Na aba "Role mapping":
   - Assign role: `ADMIN`

## 🚨 Troubleshooting

### Keycloak não inicia
```bash
# Verificar logs
make keycloak-logs

# Problemas comuns:
# 1. Porta 8080 já está em uso
sudo lsof -i :8080
# Parar processo que usa a porta ou mudar porta no docker-compose.yml

# 2. Falta de memória
docker stats
# Aumentar memória disponível para Docker

# 3. Dados corrompidos
make keycloak-clean
make keycloak
```

### Client secret não é obtido
```bash
# Verificar se Keycloak está acessível
curl http://localhost:8080/realms/master

# Verificar se o realm existe
curl http://localhost:8080/realms/vehicle-sales

# Verificar se o client existe
# Acessar http://localhost:8080/admin e verificar manualmente

# Reconfigurar tudo
make keycloak-setup
make keycloak-secret
```

### Erro de autenticação
```bash
# Verificar se o client secret está correto
cat /tmp/keycloak-credentials-development.env

# Verificar se o auth service está usando o secret correto
make auth-logs

# Verificar se o usuário admin existe
# Acessar http://localhost:8080/admin → Users
```

### Erro 401 Unauthorized
```bash
# Verificar se o token está sendo enviado corretamente
curl -X GET http://localhost:8002/auth/profile \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Verificar se o token não expirou
# Tokens duram 5 minutos por padrão
```

## 📝 Comandos Úteis

### Keycloak
```bash
make keycloak              # Iniciar Keycloak
make keycloak-logs         # Ver logs
make keycloak-setup        # Configuração automática
make keycloak-secret       # Obter client secret
make keycloak-console      # Mostrar info do console
make keycloak-clean        # Limpar dados
make keycloak-restart      # Reiniciar
```

### Verificação
```bash
# Status dos serviços
make status

# Logs do auth service
make auth-logs

# Testar health check
curl http://localhost:8002/health
```

## 🔐 Credenciais Padrão

### Console Admin Keycloak
- URL: http://localhost:8080/admin
- Usuário: `admin`
- Senha: `admin123`

### Usuário da Aplicação
- Username: `admin`
- Password: `admin123`
- Role: `ADMIN`

## 🌐 URLs Importantes

- **Keycloak Admin**: http://localhost:8080/admin
- **Realm vehicle-sales**: http://localhost:8080/realms/vehicle-sales
- **Auth Service**: http://localhost:8002
- **Auth Service Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:3000

## 📊 Validação da Configuração

### Checklist
- [ ] Keycloak está rodando na porta 8080
- [ ] Realm `vehicle-sales` existe
- [ ] Client `vehicle-sales-app` existe
- [ ] Client secret foi obtido
- [ ] Usuário admin existe com role ADMIN
- [ ] Auth service consegue se comunicar com Keycloak
- [ ] Frontend consegue fazer login

### Script de Validação
```bash
#!/bin/bash
echo "🔍 Validando configuração do Keycloak..."

# 1. Verificar se Keycloak está rodando
if curl -s http://localhost:8080/realms/master > /dev/null; then
    echo "✅ Keycloak está rodando"
else
    echo "❌ Keycloak não está acessível"
    exit 1
fi

# 2. Verificar se realm existe
if curl -s http://localhost:8080/realms/vehicle-sales > /dev/null; then
    echo "✅ Realm vehicle-sales existe"
else
    echo "❌ Realm vehicle-sales não existe"
    exit 1
fi

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "✅ Client secret foi obtido"
else
    echo "❌ Client secret não foi obtido"
    exit 1
fi

# 4. Testar autenticação
if curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | grep -q "access_token"; then
    echo "✅ Autenticação funcionando"
else
    echo "❌ Erro na autenticação"
    exit 1
fi

echo "🎉 Configuração do Keycloak está correta!"
```

## 🔄 Próximos Passos

Após configurar o Keycloak:

1. **Iniciar todos os serviços**:
   ```bash
   make up
   ```

2. **Acessar o frontend**:
   ```bash
   # Abrir http://localhost:3000
   # Fazer login com admin/admin123
   ```

3. **Testar funcionalidades**:
   - Criar veículos
   - Gerenciar clientes
   - Processar vendas

4. **Configurar para produção**:
   - Seguir [Guia de Produção](KEYCLOAK_PRODUCTION_GUIDE.md)
   - Configurar HTTPS
   - Usar senhas seguras 