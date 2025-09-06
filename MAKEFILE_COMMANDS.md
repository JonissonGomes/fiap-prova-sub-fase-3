# 🛠️ Comandos Make - FIAP III de Veículos

Este documento descreve todos os comandos make disponíveis para o projeto, incluindo os novos comandos de população de dados.

## 🚀 Execução Rápida

```bash
# Setup completo + dados completos
make setup

# Popular dados completos (RECOMENDADO)
make populate-advanced

# Verificar status do banco
make db-status

# Iniciar sistema
make start
```

## 📋 Lista Completa de Comandos

### 🌱 População de Dados

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make populate` | População padrão (dados completos) | ✅ **Recomendado** |
| `make populate-advanced` | População avançada (20 veículos, 15 clientes, 25 vendas) | ⭐ **Mais completo** |
| `make populate-interactive` | População interativa (escolher opção) | 🎮 **Interface amigável** |
| `make populate-full` | População abrangente (dados moderados) | 📊 **Intermediário** |
| `make populate-basic` | População básica (dados mínimos) | 🌱 **Rápido** |
| `make populate-admin` | Criar apenas administrador | 👑 **Apenas admin** |

### 📊 Gerenciamento do Banco

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make db-status` | Verificar estatísticas do banco | 📊 **Monitoramento** |
| `make db-validate` | Validar integridade dos dados | ✅ **Verificação** |
| `make db-clean` | Limpar todos os dados (com confirmação) | 🧹 **Reset** |

### 🏗️ Setup e Desenvolvimento

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make install` | Instalar dependências | 📦 **Inicial** |
| `make setup` | Setup completo do projeto | 🚀 **Tudo junto** |
| `make mongodb` | Iniciar MongoDB com Docker | 🗄️ **Banco** |

### 🔧 Execução

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make start` | Iniciar backend + frontend | 🚀 **Completo** |
| `make start-backend` | Iniciar apenas backend | 🔧 **API** |
| `make start-frontend` | Iniciar apenas frontend | 🎨 **Interface** |
| `make dev` | Modo desenvolvimento | 💻 **Dev** |
| `make prod` | Modo produção | 🏭 **Produção** |

### 🛑 Controle

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make stop` | Parar todos os serviços | 🛑 **Parar** |
| `make stop-mongodb` | Parar MongoDB | 🛑 **Banco** |
| `make clean` | Limpeza completa | 🧹 **Reset total** |
| `make reset` | Reset completo do projeto | 🔄 **Recomeçar** |

### 📊 Monitoramento

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make status` | Status dos serviços | 📊 **Estado** |
| `make health` | Health check das APIs | 🏥 **Saúde** |
| `make logs` | Ver logs em tempo real | 📋 **Debug** |
| `make info` | Informações do projeto | ℹ️ **Info** |

### 🏗️ Build e Deploy

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make build` | Build para produção | 🏗️ **Build** |
| `make deploy` | Deploy local | 🚀 **Deploy** |
| `make test` | Executar testes | 🧪 **Testes** |

### 💾 Backup

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `make backup` | Backup do banco | 💾 **Segurança** |
| `make restore` | Restaurar backup | 🔄 **Recuperar** |

## 🎯 Fluxos de Trabalho Recomendados

### 🚀 Primeiro Setup
```bash
# 1. Setup inicial completo
make setup

# 2. Verificar se está tudo funcionando
make status
make db-status

# 3. Iniciar desenvolvimento
make dev
```

### 🔄 Desenvolvimento Diário
```bash
# 1. Verificar status
make status

# 2. Iniciar serviços
make start

# 3. (Opcional) Popular novos dados
make populate-advanced
```

### 🧹 Reset Completo
```bash
# 1. Limpar tudo
make clean

# 2. Setup novamente
make setup

# 3. Popular dados
make populate-advanced
```

### 📊 Monitoramento
```bash
# 1. Status geral
make status

# 2. Status do banco
make db-status

# 3. Validar integridade
make db-validate

# 4. Health check
make health
```

## 📋 Detalhes dos Comandos de População

### `make populate-advanced` (RECOMENDADO)
- **20 veículos** de 10 marcas diferentes
- **15 clientes** com dados completos
- **25 vendas** com cenários variados
- **6 usuários** (admin + vendedores + clientes)
- **Receita**: ~R$ 1.000.000+
- **⚠️ Limpa dados existentes**

### `make populate-interactive`
```
Opções:
1) População básica (dados mínimos)
2) População abrangente (dados moderados)  
3) População avançada (dados completos - RECOMENDADO)
4) Apenas criar admin padrão
```

### `make db-status`
Mostra:
- 📊 Contadores de cada entidade
- 💵 Receita total
- 🚗 Status dos veículos
- 💰 Status das vendas
- 💳 Métodos de pagamento

### `make db-validate`
Verifica:
- ✅ Valores negativos
- ✅ Descontos inválidos
- ✅ Vendas órfãs
- ✅ Datas inconsistentes
- ✅ Integridade referencial

## 🔑 Credenciais Padrão

Após executar qualquer comando de população:

| Perfil | Email | Senha | Acesso |
|--------|--------|--------|--------|
| **Admin** | `admin@fiap.com` | `admin123` | 👑 Total |
| **Vendedor** | `carlos.vendedor@fiap.com` | `vendedor123` | 💼 Vendas |
| **Cliente** | `cliente.joao@fiap.com` | `cliente123` | 👤 Compras |

## 🚨 Comandos Destrutivos

⚠️ **Cuidado com estes comandos:**

- `make populate-advanced` - **Limpa dados existentes**
- `make db-clean` - **Remove TODOS os dados**
- `make clean` - **Remove node_modules e builds**
- `make reset` - **Reset completo do projeto**

## 🎛️ Configuração

### Portas Padrão
- **Backend**: `3002`
- **Frontend**: `3000`
- **MongoDB**: `27017`

### Variáveis de Ambiente
```env
MONGODB_URI=mongodb://localhost:27017/unified_vehicle_db
BACKEND_PORT=3002
FRONTEND_PORT=3000
```

## 🆘 Solução de Problemas

### MongoDB não conecta
```bash
make mongodb          # Iniciar MongoDB
make status          # Verificar status
```

### Dependências desatualizadas
```bash
make clean           # Limpar tudo
make install         # Reinstalar
```

### Dados corrompidos
```bash
make db-validate     # Verificar problemas
make db-clean        # Limpar banco
make populate-advanced  # Popular novamente
```

### Portas em uso
```bash
make stop            # Parar serviços
make status          # Verificar se parou
make start           # Iniciar novamente
```

## 💡 Dicas

1. **Use sempre** `make populate-advanced` para dados completos
2. **Verifique o status** com `make db-status` após popular
3. **Valide os dados** com `make db-validate` periodicamente  
4. **Faça backup** com `make backup` antes de mudanças grandes
5. **Use** `make help` para ver todos os comandos

---

**🎯 Comando mais útil:** `make populate-advanced && make start`
