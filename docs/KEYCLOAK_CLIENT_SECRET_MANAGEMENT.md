# Gerenciamento do Client Secret do Keycloak

## 🔑 Sobre o Client Secret

### É Fixo ou Dinâmico?

O **client_secret** do Keycloak é **DINÂMICO** e pode ser:

1. **Gerado automaticamente** pelo Keycloak quando um client é criado
2. **Regenerado** manualmente pelo administrador
3. **Rotacionado** por questões de segurança

### Problemas da Configuração Atual

❌ **Problema identificado**: O `docker-compose.yml` tem um client_secret hardcoded que não corresponde ao secret real gerado pelo Keycloak.

```yaml
# docker-compose.yml - INCORRETO
environment:
  - KEYCLOAK_CLIENT_SECRET=T14LidpfzazUfpvn6GsrlDyGooT8p0s6  # ❌ Fixo e incorreto
```

```bash
# Keycloak real - CORRETO
CLIENT_SECRET=BCzhpesgtiAQENgLRuO2tlsLBdUPPMTv  # ✅ Dinâmico e correto
```

## 🔧 Soluções Implementadas

### 1. Script de Sincronização Automática

Criamos o script `scripts/setup-env-from-keycloak.sh` que:

- ✅ Obtém o client_secret **dinamicamente** do Keycloak
- ✅ Atualiza o `docker-compose.yml` automaticamente
- ✅ Cria um arquivo `.env` com as configurações corretas
- ✅ Faz backup do arquivo original

### 2. Comando Makefile

```bash
# Sincronizar client_secret do Keycloak
make sync-keycloak-env
```

### 3. Template de Configuração

Arquivo `env.example` com todas as variáveis necessárias:

```env
# Configurações do Keycloak
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=# Obtido dinamicamente via script
```

## 🚀 Como Usar

### Método 1: Comando Makefile (Recomendado)

```bash
# Após o Keycloak estar rodando
make sync-keycloak-env

# Reiniciar o auth-service
docker-compose restart auth-service
```

### Método 2: Script Direto

```bash
# Executar o script diretamente
./scripts/setup-env-from-keycloak.sh

# Reiniciar o auth-service
docker-compose restart auth-service
```

### Método 3: Obter Apenas o Secret

```bash
# Apenas obter o client_secret
./scripts/get-keycloak-client-secret.sh
```

## 📋 Fluxo Recomendado

1. **Setup Inicial**:
   ```bash
   make setup-complete
   ```

2. **Sincronizar Client Secret**:
   ```bash
   make sync-keycloak-env
   ```

3. **Reiniciar Serviços**:
   ```bash
   docker-compose restart auth-service
   ```

4. **Testar Login**:
   ```bash
   curl -X POST "http://localhost:8002/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@vehiclesales.com", "password": "admin123"}'
   ```

## 🔒 Segurança

### Boas Práticas

1. **Nunca committar** o client_secret no código
2. **Usar variáveis de ambiente** para configurações sensíveis
3. **Rotacionar** o client_secret periodicamente
4. **Monitorar** logs de autenticação

### Ambientes

- **Development**: Client_secret obtido dinamicamente
- **Production**: Client_secret deve ser gerenciado via secrets manager
- **CI/CD**: Usar variáveis de ambiente seguras

## 🔄 Rotação do Client Secret

### Quando Rotacionar

- ✅ Compromisso de segurança
- ✅ Mudança de ambiente
- ✅ Política de segurança da empresa
- ✅ Periodicamente (ex: a cada 90 dias)

### Como Rotacionar

1. **Gerar novo secret** no Keycloak Admin Console
2. **Executar script** de sincronização:
   ```bash
   make sync-keycloak-env
   ```
3. **Reiniciar serviços**:
   ```bash
   docker-compose restart auth-service
   ```

## 🐛 Troubleshooting

### Erro "Invalid client credentials"

```bash
# Verificar client_secret atual
make sync-keycloak-env

# Verificar variável no container
docker exec -it fiap-prova-sub-fase-3-auth-service-1 env | grep KEYCLOAK_CLIENT_SECRET

# Reiniciar serviço
docker-compose restart auth-service
```

### Cliente não encontrado

```bash
# Verificar se o client existe
./scripts/get-keycloak-client-secret.sh
```

### Keycloak não acessível

```bash
# Verificar se o Keycloak está rodando
docker-compose ps keycloak

# Verificar logs
docker logs fiap-prova-sub-fase-3-keycloak-1
```

## 📚 Referências

- [Keycloak Admin REST API](https://www.keycloak.org/docs-api/latest/rest-api/index.html)
- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Secure Secrets Management](https://docs.docker.com/compose/compose-file/compose-file-v3/#secrets) 