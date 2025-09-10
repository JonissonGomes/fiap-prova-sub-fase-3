# 🚗 FIAP III de Veículos - Makefile
# Facilita o setup, execução e gerenciamento do projeto

# Cores para output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
WHITE=\033[1;37m
NC=\033[0m # No Color

# Variáveis
BACKEND_DIR=backend
FRONTEND_DIR=frontend
MONGODB_CONTAINER=mongodb-unified-dev
BACKEND_PORT=3002
FRONTEND_PORT=3000
MONGODB_PORT=27017

# Comandos padrão
.PHONY: help install setup start stop clean test logs status populate-basic populate-full populate-advanced populate-interactive populate-admin db-status db-clean db-validate fix-users check-users

# Ajuda - comando padrão
help: ## 📖 Mostra esta ajuda
	@echo "$(CYAN)🚗 FIAP III de Veículos$(NC)"
	@echo "$(YELLOW)================================$(NC)"
	@echo ""
	@echo "$(WHITE)Comandos disponíveis:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_][a-zA-Z0-9_-]*:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Exemplos:$(NC)"
	@echo "  make setup             # Setup completo do projeto"
	@echo "  make populate-advanced # Popular banco com dados completos"
	@echo "  make start             # Iniciar backend e frontend"
	@echo "  make db-status         # Ver estatísticas do banco"
	@echo "  make stop              # Parar todos os serviços"
	@echo ""
	@echo "$(WHITE)🌱 Comandos de População:$(NC)"
	@echo "  $(GREEN)populate-cloud$(NC)         # Popular banco da API (USAR ESTE!)"
	@echo "  $(GREEN)populate-advanced$(NC)      # Dados completos (local)"
	@echo "  $(GREEN)populate-interactive$(NC)   # Escolher opção interativamente"
	@echo "  $(GREEN)populate-full$(NC)          # Dados abrangentes"
	@echo "  $(GREEN)populate-basic$(NC)         # Dados mínimos"
	@echo "  $(GREEN)populate-admin$(NC)         # Apenas administrador"
	@echo ""
	@echo "$(WHITE)📊 Comandos do Banco:$(NC)"
	@echo "  $(GREEN)db-status$(NC)              # Estatísticas do banco"
	@echo "  $(GREEN)db-validate$(NC)            # Validar integridade dos dados"
	@echo "  $(GREEN)db-clean$(NC)               # Limpar banco de dados"

# Instalação de dependências
install: ## 📦 Instalar dependências do backend e frontend
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@cd $(BACKEND_DIR) && npm install
	@echo "$(YELLOW)Frontend:$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

# Setup completo do projeto
setup: install mongodb populate ## 🚀 Setup completo do projeto
	@echo "$(GREEN)🎉 Setup completo realizado!$(NC)"
	@echo "$(WHITE)Para iniciar o sistema, execute:$(NC)"
	@echo "  $(CYAN)make start$(NC)"

# Configuração do MongoDB
mongodb: ## 🗄️ Verificar conexão com MongoDB
	@echo "$(BLUE)🗄️ Verificando MongoDB...$(NC)"
	@echo "$(YELLOW)Certifique-se de que o MongoDB está rodando localmente ou use MongoDB Atlas$(NC)"
	@echo "$(YELLOW)URL padrão: mongodb://localhost:27017$(NC)"
	@echo "$(YELLOW)Para usar MongoDB Atlas, configure a variável MONGODB_URL$(NC)"

# Verificar se MongoDB está rodando
check-mongodb: ## 🔍 Verificar se MongoDB está rodando
	@echo "$(BLUE)🔍 Verificando MongoDB...$(NC)"
	@if nc -z localhost 27017 2>/dev/null; then \
		echo "$(GREEN)✅ MongoDB está rodando na porta 27017$(NC)"; \
	else \
		echo "$(RED)❌ MongoDB não está rodando$(NC)"; \
		echo "$(YELLOW)Para iniciar MongoDB local:$(NC)"; \
		echo "$(YELLOW)  brew services start mongodb-community$(NC)"; \
		echo "$(YELLOW)  ou$(NC)"; \
		echo "$(YELLOW)  mongod --config /usr/local/etc/mongod.conf$(NC)"; \
	fi

# Popular dados iniciais (mantido para compatibilidade)
populate: populate-advanced ## 🌱 Popular banco com dados completos (padrão)

# População básica
populate-basic: ## 🌱 População básica (dados mínimos)
	@echo "$(BLUE)🌱 Populando dados básicos...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/populate-data.js
	@echo "$(GREEN)✅ Dados básicos populados!$(NC)"

# População abrangente
populate-full: ## 📊 População abrangente (dados moderados)
	@echo "$(BLUE)📊 Populando dados abrangentes...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/populate-comprehensive-data.js
	@echo "$(GREEN)✅ Dados abrangentes populados!$(NC)"

# População avançada (RECOMENDADO)
populate-advanced: ## 🎯 População avançada (dados completos - RECOMENDADO)
	@echo "$(BLUE)🎯 Populando dados avançados...$(NC)"
	@echo "$(YELLOW)⚠️  Este comando limpa dados existentes!$(NC)"
	@cd $(BACKEND_DIR) && node scripts/populate-advanced-data.js
	@echo "$(GREEN)✅ Dados avançados populados!$(NC)"
	@echo ""
	@echo "$(WHITE)🔑 Credenciais de acesso:$(NC)"
	@echo "  $(CYAN)👑 Admin: admin@fiap.com / admin123$(NC)"
	@echo "  $(CYAN)💼 Vendedor: carlos.vendedor@fiap.com / vendedor123$(NC)"
	@echo "  $(CYAN)👤 Cliente: cliente.joao@fiap.com / cliente123$(NC)"

# População interativa
populate-interactive: ## 🎮 População interativa (escolher opção)
	@echo "$(BLUE)🎮 População interativa...$(NC)"
	@cd $(BACKEND_DIR) && ./scripts/populate.sh

# Criar apenas admin
populate-admin: ## 👑 Criar apenas usuário administrador
	@echo "$(BLUE)👑 Criando administrador...$(NC)"
	@cd $(BACKEND_DIR) && echo "4" | ./scripts/populate.sh
	@echo "$(GREEN)✅ Administrador criado!$(NC)"

# Status do banco de dados
db-status: ## 📊 Verificar status e estatísticas do banco
	@echo "$(BLUE)📊 Status do banco de dados...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/db-status.js

# Limpar banco de dados
db-clean: ## 🧹 Limpar todos os dados do banco
	@echo "$(RED)🧹 Limpando banco de dados...$(NC)"
	@echo "$(YELLOW)⚠️  Isso removerá TODOS os dados!$(NC)"
	@read -p "Confirma? (s/N): " confirm && [ "$$confirm" = "s" ] || (echo "$(YELLOW)Operação cancelada$(NC)" && exit 1)
	@cd $(BACKEND_DIR) && node -e " \
		require('dotenv').config({ path: './config.env' }); \
		const mongoose = require('mongoose'); \
		const { connectDatabase } = require('./src/config/database'); \
		(async () => { \
			try { \
				await connectDatabase(); \
				await mongoose.connection.db.dropDatabase(); \
				console.log('$(GREEN)✅ Banco limpo com sucesso!$(NC)'); \
			} catch (error) { \
				console.error('$(RED)❌ Erro:', error.message, '$(NC)'); \
			} finally { \
				await mongoose.disconnect(); \
				process.exit(0); \
			} \
		})(); \
	"

# Validar dados do banco
db-validate: ## ✅ Validar integridade dos dados
	@echo "$(BLUE)✅ Validando integridade dos dados...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/db-validate.js

# Verificar usuários
check-users: ## 👥 Verificar usuários no banco
	@echo "$(BLUE)👥 Verificando usuários...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/check-users.js

# Corrigir usuários
fix-users: ## 🔧 Corrigir e recriar usuários FIAP
	@echo "$(BLUE)🔧 Corrigindo usuários...$(NC)"
	@cd $(BACKEND_DIR) && node scripts/fix-users.js

# Popular banco da API (cloud)
populate-cloud: ## ☁️ Popular banco que a API está usando
	@echo "$(BLUE)☁️ Populando banco da API...$(NC)"
	@echo "$(YELLOW)⚠️  Isso criará dados no mesmo banco da API$(NC)"
	@cd $(BACKEND_DIR) && node scripts/populate-cloud-data.js

# Iniciar todos os serviços
start: check-mongodb ## 🚀 Iniciar backend e frontend
	@echo "$(BLUE)🚀 Iniciando sistema...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo ""
	@echo "$(WHITE)Pressione Ctrl+C para parar$(NC)"
	@echo ""
	@$(MAKE) start-backend & $(MAKE) start-frontend & wait

# Iniciar apenas o backend
start-backend: ## 🔧 Iniciar apenas o backend
	@echo "$(BLUE)🔧 Iniciando backend...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Health: http://localhost:$(BACKEND_PORT)/health$(NC)"
	@echo ""
	@cd $(BACKEND_DIR) && npm start

# Iniciar apenas o frontend
start-frontend: ## 🎨 Iniciar apenas o frontend
	@echo "$(BLUE)🎨 Iniciando frontend...$(NC)"
	@cd $(FRONTEND_DIR) && REACT_APP_BACKEND_URL=http://localhost:3002 npm start

# Build do frontend para produção
build-frontend: ## 🏗️ Build do frontend para produção
	@echo "$(BLUE)🏗️ Building frontend para produção...$(NC)"
	@cd $(FRONTEND_DIR) && npm run build

# Build do frontend para desenvolvimento local
build-frontend-local: ## 🏗️ Build do frontend para desenvolvimento local
	@echo "$(BLUE)🏗️ Building frontend para desenvolvimento local...$(NC)"
	@cd $(FRONTEND_DIR) && npm run build:local

# Parar todos os serviços
stop: ## 🛑 Parar todos os serviços
	@echo "$(RED)🛑 Parando serviços...$(NC)"
	@pkill -f "node.*server.js" || true
	@pkill -f "react-scripts" || true
	@pkill -f "npm.*start" || true
	@echo "$(GREEN)✅ Serviços parados!$(NC)"

# Parar MongoDB
stop-mongodb: ## 🛑 Parar MongoDB
	@echo "$(RED)🛑 Parando MongoDB...$(NC)"
	@echo "$(YELLOW)Para parar MongoDB local, use: brew services stop mongodb-community$(NC)"
	@echo "$(YELLOW)Ou pare o processo manualmente$(NC)"

# Limpeza completa
clean: stop ## 🧹 Limpeza completa
	@echo "$(RED)🧹 Limpando projeto...$(NC)"
	@cd $(BACKEND_DIR) && rm -rf node_modules package-lock.json
	@cd $(FRONTEND_DIR) && rm -rf node_modules package-lock.json build
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

# Testes
test: ## 🧪 Executar testes
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@cd $(BACKEND_DIR) && npm test || echo "$(YELLOW)Testes do backend não configurados$(NC)"
	@echo "$(YELLOW)Frontend:$(NC)"
	@cd $(FRONTEND_DIR) && npm test || echo "$(YELLOW)Testes do frontend não configurados$(NC)"

# Logs em tempo real
logs: ## 📋 Ver logs em tempo real
	@echo "$(BLUE)📋 Logs do sistema...$(NC)"
	@echo "$(WHITE)Pressione Ctrl+C para sair$(NC)"
	@echo ""
	@tail -f $(BACKEND_DIR)/logs/*.log 2>/dev/null || echo "$(YELLOW)Logs não encontrados$(NC)"

# Status dos serviços
status: ## 📊 Status dos serviços
	@echo "$(BLUE)📊 Status dos serviços:$(NC)"
	@echo ""
	@echo "$(YELLOW)MongoDB:$(NC)"
	@if docker ps -q -f name=$(MONGODB_CONTAINER) | grep -q .; then \
		echo "  $(GREEN)✅ Rodando$(NC)"; \
	else \
		echo "  $(RED)❌ Parado$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Backend:$(NC)"
	@if pgrep -f "node.*server.js" > /dev/null; then \
		echo "  $(GREEN)✅ Rodando na porta $(BACKEND_PORT)$(NC)"; \
	else \
		echo "  $(RED)❌ Parado$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC)"
	@if pgrep -f "react-scripts" > /dev/null; then \
		echo "  $(GREEN)✅ Rodando na porta $(FRONTEND_PORT)$(NC)"; \
	else \
		echo "  $(RED)❌ Parado$(NC)"; \
	fi

# Health check
health: ## 🏥 Verificar saúde dos serviços
	@echo "$(BLUE)🏥 Verificando saúde dos serviços...$(NC)"
	@echo ""
	@echo "$(YELLOW)API Health Check:$(NC)"
	@curl -s http://localhost:$(BACKEND_PORT)/health | jq . || echo "$(RED)❌ API não está respondendo$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC)"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:$(FRONTEND_PORT) | grep -q "200" && echo "$(GREEN)✅ Frontend OK$(NC)" || echo "$(RED)❌ Frontend não está respondendo$(NC)"

# Build para produção
build: ## 🏗️ Build para produção
	@echo "$(BLUE)🏗️ Build para produção...$(NC)"
	@cd $(FRONTEND_DIR) && npm run build
	@echo "$(GREEN)✅ Build concluído!$(NC)"

# Deploy local
deploy: build ## 🚀 Deploy local
	@echo "$(BLUE)🚀 Deploy local...$(NC)"
	@$(MAKE) start-backend
	@echo "$(GREEN)✅ Deploy concluído!$(NC)"

# Reset completo
reset: clean setup ## 🔄 Reset completo do projeto
	@echo "$(GREEN)🔄 Reset completo realizado!$(NC)"

# Desenvolvimento
dev: ## 💻 Modo desenvolvimento (backend + frontend)
	@echo "$(BLUE)💻 Iniciando modo desenvolvimento...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:$(FRONTEND_PORT)$(NC)"
	@echo ""
	@$(MAKE) start

# Produção
prod: build ## 🏭 Modo produção
	@echo "$(BLUE)🏭 Iniciando modo produção...$(NC)"
	@NODE_ENV=production $(MAKE) start-backend

# Backup do banco
backup: ## 💾 Backup do banco de dados
	@echo "$(BLUE)💾 Fazendo backup do banco...$(NC)"
	@mkdir -p backups
	@docker exec $(MONGODB_CONTAINER) mongodump --db vehicle_sales --out /tmp/backup
	@docker cp $(MONGODB_CONTAINER):/tmp/backup ./backups/backup-$(shell date +%Y%m%d-%H%M%S)
	@echo "$(GREEN)✅ Backup concluído!$(NC)"

# Restaurar backup
restore: ## 🔄 Restaurar backup do banco
	@echo "$(BLUE)🔄 Restaurando backup...$(NC)"
	@echo "$(YELLOW)Backups disponíveis:$(NC)"
	@ls -la backups/ 2>/dev/null || echo "$(RED)Nenhum backup encontrado$(NC)"

# Informações do projeto
info: ## ℹ️ Informações do projeto
	@echo "$(CYAN)🚗 FIAP III de Veículos$(NC)"
	@echo "$(YELLOW)================================$(NC)"
	@echo ""
	@echo "$(WHITE)Versões:$(NC)"
	@echo "  Node.js: $(shell node --version 2>/dev/null || echo 'Não instalado')"
	@echo "  npm: $(shell npm --version 2>/dev/null || echo 'Não instalado')"
	@echo "  Docker: $(shell docker --version 2>/dev/null || echo 'Não instalado')"
	@echo ""
	@echo "$(WHITE)Portas:$(NC)"
	@echo "  Backend: $(BACKEND_PORT)"
	@echo "  Frontend: $(FRONTEND_PORT)"
	@echo "  MongoDB: $(MONGODB_PORT)"
	@echo ""
	@echo "$(WHITE)Credenciais padrão:$(NC)"
	@echo "  Email: admin@vehiclesales.com"
	@echo "  Senha: admin123"


# Comando padrão
.DEFAULT_GOAL := help
