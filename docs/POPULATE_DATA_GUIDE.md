# Guia de População de Dados

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 

Este guia explica como usar o sistema de população de dados para criar dados de teste similares a dados reais no sistema de vendas de veículos.

## 🚀 Início Rápido

### 1. Certifique-se que os serviços estão rodando
```bash
make up
```

### 2. Teste o sistema de população
```bash
make test-populate-data
```

### 3. Popule os dados
```bash
make populate-data
```

## 📋 Comandos Disponíveis

### `make populate-data`
- Popula dados de teste nos serviços
- Executa completamente dentro do Docker
- Não requer instalação de dependências no host
- Cria aproximadamente:
  - 20 usuários
  - 50 clientes
  - 100 veículos
  - 30 vendas

### `make populate-data-clean`
- Limpa todos os bancos de dados antes de popular
- Executa `populate-data` após limpeza
- Recomendado para ambiente de desenvolvimento

### `make test-populate-data`
- Testa se o sistema de população está funcionando
- Verifica conectividade com serviços
- Não popula dados reais

## 🎯 Dados Gerados

### Usuários
- **Admin padrão**: username `admin`, password `admin123`
- **Usuários de teste**: `user001` a `user020`, password `password123`
- **Roles**: ADMIN, CUSTOMER, SALES (distribuição aleatória)

### Clientes
- **Nomes**: Combinação de nomes brasileiros comuns
- **CPF**: Gerados com algoritmo de validação
- **Telefone**: Números válidos com DDD brasileiro
- **Email**: Gerados baseados no nome
- **Endereço**: Cidades e estados brasileiros

### Veículos
- **Marcas**: Toyota, Volkswagen, Chevrolet, Ford, Hyundai, Fiat, Honda, Nissan, Renault, Peugeot
- **Modelos**: Específicos por marca (ex: Toyota Corolla, VW Golf)
- **Anos**: 2015 a 2024
- **Preços**: Baseados em ano e quilometragem
- **Status**: 75% disponíveis, 25% vendidos

### Vendas
- **Período**: Últimos 6 meses
- **Métodos de pagamento**: Dinheiro, Financiamento, Cartão, PIX
- **Preços**: Variação de ±10% do preço original do veículo

## 🐳 Execução no Docker

O sistema foi projetado para rodar completamente dentro do Docker:

1. **Container usado**: `auth-service` (contém todas as dependências)
2. **Dependências**: `httpx` é instalado automaticamente
3. **Conectividade**: Usa rede interna do Docker Compose
4. **Limpeza**: Arquivos temporários são removidos automaticamente

## 🔧 Estrutura dos Scripts

### `scripts/populate-data.sh`
- Script principal em Bash
- Verifica serviços antes de executar
- Executa o script Python dentro do container
- Não requer instalação no host

### `scripts/populate-data.py`
- Script Python com lógica de população
- Usa `httpx` para comunicação com APIs
- Gera dados realistas com algoritmos de validação
- Arquitetura assíncrona para melhor performance

### `scripts/test-populate-data.sh`
- Script de teste e validação
- Verifica conectividade com serviços
- Testa instalação de dependências
- Não popula dados reais

## 🚨 Troubleshooting

### Problema Conhecido: Sistema de Autenticação

**Sintoma**: O script falha ao tentar fazer login do admin ou criar dados.

**Causa**: O sistema atual requer autenticação para criar dados, mas o usuário admin não está sendo criado automaticamente.

**Solução Temporária**:
1. Acesse o Keycloak: http://localhost:8080/admin
2. Login: admin / admin123
3. Vá para Users > Add User
4. Crie um usuário com:
   - Username: admin@vehiclesales.com
   - Email: admin@vehiclesales.com
   - Email Verified: ON
   - Enabled: ON
5. Vá para Credentials e defina senha: admin123
6. Vá para Role Mappings e atribua role: ADMIN

### Erro: "Container auth-service não está rodando"
```bash
make up
# Aguarde todos os serviços iniciarem
make test-populate-data
```

### Erro: "Serviço não está respondendo"
```bash
# Verifique o status dos serviços
make status

# Veja os logs para identificar problemas
make logs

# Reinicie se necessário
make restart
```

### Erro: "Falha ao instalar httpx"
```bash
# Rebuild do container
make rebuild

# Ou force a reconstrução
docker-compose build --no-cache auth-service
```

### Erro: "Falha ao criar usuário admin"
```bash
# Limpe o banco de auth e tente novamente
make clean-auth-db
make populate-data
```

## 🔐 Credenciais de Acesso

### Admin
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `ADMIN`

### Usuários de Teste
- **Username**: `user001`, `user002`, ..., `user020`
- **Password**: `password123`
- **Roles**: Aleatórias (ADMIN, CUSTOMER, SALES)

## 📊 Monitoramento

### Verificar dados criados
```bash
# Usuários
curl -H "Authorization: Bearer $TOKEN" http://localhost:8002/auth/users

# Clientes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8003/customers/

# Veículos
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/vehicles/

# Vendas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/sales/
```

### Logs de execução
```bash
# Logs do auth-service durante população
make auth-logs

# Logs de todos os serviços
make logs
```

## 🧹 Limpeza

### Limpar dados específicos
```bash
make clean-auth-db      # Limpa usuários
make clean-customer-db  # Limpa clientes
make clean-core-db      # Limpa veículos
make clean-sales-db     # Limpa vendas
make clean-redis        # Limpa cache
```

### Limpeza completa
```bash
make clean              # Remove containers e volumes
make up                 # Reinicia sistema
make populate-data      # Popula novamente
```

## 🔄 Integração com CI/CD

O sistema pode ser integrado em pipelines de CI/CD:

```yaml
# Exemplo GitHub Actions
- name: Setup test data
  run: |
    make up
    make populate-data
    
- name: Run integration tests
  run: |
    make test
```

## 📈 Performance

### Tempos esperados
- **Usuários (20)**: ~30 segundos
- **Clientes (50)**: ~60 segundos
- **Veículos (100)**: ~120 segundos
- **Vendas (30)**: ~45 segundos
- **Total**: ~4-5 minutos

### Otimizações
- Requisições assíncronas com `httpx`
- Processamento em lotes
- Validação de dados otimizada
- Conexões reutilizadas

## 🛡️ Segurança

### Dados sensíveis
- CPFs gerados são válidos mas fictícios
- Senhas são simples (apenas para desenvolvimento)
- Tokens de autenticação são temporários

### Ambientes
- **Desenvolvimento**: Dados podem ser populados livremente
- **Staging**: Use `populate-data-clean` para ambiente limpo
- **Produção**: NÃO use este sistema em produção

## 📚 Referências

- [Documentação da API](./API_DOCUMENTATION.md)
- [Guia de Arquitetura](./ARCHITECTURE.md)
- [Configuração de Ambiente](./ENVIRONMENT_VARIABLES.md)
- [Guia de Deployment](./DEPLOYMENT.md) 