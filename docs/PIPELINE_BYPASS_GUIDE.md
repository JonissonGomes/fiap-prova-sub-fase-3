# Guia do Sistema de Bypass do Pipeline CI/CD

## Visão Geral

O sistema de pipeline CI/CD foi configurado com recursos de bypass para permitir deploys mesmo quando alguns testes falham. Isso é útil em situações de emergência ou quando você precisa fazer um deploy rápido.

## Como Funciona

### 1. Pipeline Automático (ci-cd.yml)

O pipeline principal roda automaticamente em pushes para `main`, `master` e `develop`:

- **Testes Backend**: Roda testes para todos os serviços (auth, core, customer, sales)
- **Testes Frontend**: Roda linting e testes do React
- **Security Scan**: Executa análise de segurança com Bandit
- **Deploy**: Se todos os testes passarem OU se configurado para bypass

**Configuração de Bypass Automático:**
- Todos os jobs de teste têm `continue-on-error: true`
- O deploy verifica o status dos testes e decide se deve continuar
- Se alguns testes falharem, o deploy ainda acontece com notificação

### 2. Deploy Manual (manual-deploy.yml)

Permite deploy manual via GitHub Actions UI com opções:

- **Environment**: production ou staging
- **Force Deploy**: Ignora falhas de teste
- **Skip Tests**: Pula completamente os testes

## Como Usar

### Opção 1: Script de Força Deploy

```bash
# Deploy forçado na branch master
./scripts/force-deploy.sh master

# Deploy forçado na branch atual
./scripts/force-deploy.sh
```

### Opção 2: GitHub Actions UI

1. Vá para `Actions` > `Manual Deploy`
2. Clique em `Run workflow`
3. Configure as opções:
   - **Environment**: Escolha production ou staging
   - **Force Deploy**: Marque para ignorar testes
   - **Skip Tests**: Marque para pular testes
4. Clique em `Run workflow`

### Opção 3: Commit Especial

```bash
# Criar commit vazio para forçar pipeline
git commit --allow-empty -m "Force deploy - bypass tests"
git push origin master
```

## Verificação de Status

### Script de Verificação

```bash
# Verificar status atual do pipeline
./scripts/check-pipeline-status.sh
```

Este script mostra:
- Status do repositório
- Resultado dos testes locais
- Links para GitHub Actions e Codecov
- Workflows disponíveis

### Verificação Manual

1. **GitHub Actions**: https://github.com/[seu-repo]/actions
2. **Codecov**: https://codecov.io/gh/[seu-repo]
3. **Render Dashboard**: Para verificar deploys

## Cenários de Uso

### Cenário 1: Deploy de Emergência
```bash
# Quando você precisa fazer um deploy urgente
./scripts/force-deploy.sh master
```

### Cenário 2: Deploy com Testes Parciais
```bash
# Deploy manual via GitHub UI com force_deploy=true
# Isso roda os testes mas não falha se alguns falharem
```

### Cenário 3: Deploy Sem Testes
```bash
# Deploy manual via GitHub UI com skip_tests=true
# Útil para deploys de configuração ou hotfixes
```

## Configuração de Secrets

Para que o pipeline funcione, você precisa configurar os seguintes secrets no GitHub:

```bash
# Docker Hub
DOCKERHUB_USERNAME=seu_usuario
DOCKERHUB_TOKEN=seu_token

# Render
RENDER_SERVICE_ID=seu_service_id
RENDER_API_KEY=sua_api_key
```

## Estrutura dos Workflows

### ci-cd.yml (Automático)
```
test-backend (continue-on-error: true)
test-frontend (continue-on-error: true)
security-scan (continue-on-error: true)
build-and-deploy (depende dos anteriores)
```

### manual-deploy.yml (Manual)
```
test-backend (condicional)
test-frontend (condicional)
build-and-deploy (com lógica de bypass)
```

## Logs e Debugging

### Ver Logs do Pipeline
1. Vá para GitHub Actions
2. Clique no workflow desejado
3. Clique no job específico
4. Expanda os steps para ver logs detalhados

### Logs Locais
```bash
# Testar serviço específico
cd auth-service
python3 -m pytest tests/ -v

# Testar frontend
cd frontend
npm test -- --watchAll=false
```

## Troubleshooting

### Problema: Pipeline não inicia
**Solução**: Verifique se está na branch correta (main, master, develop)

### Problema: Deploy falha mesmo com bypass
**Solução**: Verifique se os secrets estão configurados corretamente

### Problema: Testes falham localmente mas passam no CI
**Solução**: Verifique versões do Python/Node e dependências

### Problema: Deploy não aparece no Render
**Solução**: Verifique se o RENDER_SERVICE_ID está correto

## Boas Práticas

1. **Use bypass apenas quando necessário**
2. **Sempre verifique o status antes do deploy**
3. **Monitore os logs após o deploy**
4. **Corrija testes falhados o mais rápido possível**
5. **Use deploy manual para ambientes de staging**

## Comandos Úteis

```bash
# Verificar status
./scripts/check-pipeline-status.sh

# Forçar deploy
./scripts/force-deploy.sh

# Ver logs do git
git log --oneline -10

# Ver status do git
git status

# Ver branches
git branch -a
```

## Suporte

Se você encontrar problemas:

1. Verifique os logs do GitHub Actions
2. Execute o script de verificação
3. Teste localmente primeiro
4. Consulte a documentação do projeto
5. Abra uma issue no repositório 