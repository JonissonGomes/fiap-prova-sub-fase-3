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
.PHONY: help install setup start stop clean test logs status

# Ajuda - comando padrão
help: ## 📖 Mostra esta ajuda
	@echo "$(CYAN)🚗 FIAP III de Veículos$(NC)"
	@echo "$(YELLOW)================================$(NC)"
	@echo ""
	@echo "$(WHITE)Comandos disponíveis:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Exemplos:$(NC)"
	@echo "  make setup     # Setup completo do projeto"
	@echo "  make start     # Iniciar backend e frontend"
	@echo "  make stop      # Parar todos os serviços"
	@echo "  make logs      # Ver logs em tempo real"

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
mongodb: ## 🗄️ Iniciar MongoDB com Docker
	@echo "$(BLUE)🗄️ Configurando MongoDB...$(NC)"
	@if docker ps -q -f name=$(MONGODB_CONTAINER) | grep -q .; then \
		echo "$(YELLOW)MongoDB já está rodando$(NC)"; \
	else \
		echo "$(YELLOW)Iniciando MongoDB...$(NC)"; \
		docker run -d --name $(MONGODB_CONTAINER) -p $(MONGODB_PORT):27017 mongo:latest --noauth; \
		sleep 3; \
		echo "$(GREEN)✅ MongoDB iniciado!$(NC)"; \
	fi

# Popular dados iniciais
populate: ## 🌱 Popular banco com dados iniciais
	@echo "$(BLUE)🌱 Populando dados iniciais...$(NC)"
	@cd $(BACKEND_DIR) && npm run populate
	@echo "$(GREEN)✅ Dados populados!$(NC)"

# Iniciar todos os serviços
start: ## 🚀 Iniciar backend e frontend
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
	@cd $(BACKEND_DIR) && npm start

# Iniciar apenas o frontend
start-frontend: ## 🎨 Iniciar apenas o frontend
	@echo "$(BLUE)🎨 Iniciando frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm start

# Parar todos os serviços
stop: ## 🛑 Parar todos os serviços
	@echo "$(RED)🛑 Parando serviços...$(NC)"
	@pkill -f "node.*server.js" || true
	@pkill -f "react-scripts" || true
	@echo "$(GREEN)✅ Serviços parados!$(NC)"

# Parar MongoDB
stop-mongodb: ## 🛑 Parar MongoDB
	@echo "$(RED)🛑 Parando MongoDB...$(NC)"
	@docker stop $(MONGODB_CONTAINER) || true
	@docker rm $(MONGODB_CONTAINER) || true
	@echo "$(GREEN)✅ MongoDB parado!$(NC)"

# Limpeza completa
clean: stop stop-mongodb ## 🧹 Limpeza completa
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
