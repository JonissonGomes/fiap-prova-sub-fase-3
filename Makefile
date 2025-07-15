.PHONY: setup install up down test test-core test-sales test-auth test-customer logs clean run stop mongodb mongodb-logs core sales auth customer frontend core-logs sales-logs auth-logs customer-logs frontend-logs keycloak keycloak-logs lint type-check rebuild status restart clean-sales-db clean-core-db clean-auth-db clean-customer-db coverage coverage-core coverage-sales coverage-auth coverage-customer coverage-report setup-env validate-env docs redis redis-logs redis-cli clean-redis test-rate-limiting test-frontend populate-data populate-data-clean test-populate-data frontend-build frontend-test frontend-lint frontend-format

setup:
	@echo "Configurando ambiente..."
	docker-compose build

install:
	@echo "Instalando dependências..."
	docker-compose run --rm core-service pip install -r requirements.txt
	docker-compose run --rm sales-service pip install -r requirements.txt
	docker-compose run --rm auth-service pip install -r requirements.txt
	docker-compose run --rm customer-service pip install -r requirements.txt
	docker-compose run --rm frontend npm install

up:
	docker-compose up -d
	@echo "🚀 Serviços iniciados:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Core Service: http://localhost:8000"
	@echo "   Sales Service: http://localhost:8001"
	@echo "   Auth Service: http://localhost:8002"
	@echo "   Customer Service: http://localhost:8003"
	@echo "   Keycloak: http://localhost:8080"
	@echo "   Redis: localhost:6379"
	@echo ""
	@echo "📋 Para ver logs: make logs"
	@echo "🔧 Para configurar Keycloak: make keycloak-setup"
	docker-compose logs -f

down:
	docker-compose down

# População de dados
populate-data:
	@echo "🚀 Populando dados de teste..."
	@./scripts/populate-data.sh

populate-data-working:
	@echo "🚀 Populando dados (versão funcional)..."
	@./scripts/populate-data-working.sh

populate-data-clean: clean-dbs populate-data-working

test-populate-data:
	@echo "🧪 Testando sistema de população de dados..."
	@./scripts/test-populate-data.sh

test:
	@echo "Executando testes..."
	docker-compose run --rm core-service pytest tests/ -v
	docker-compose run --rm sales-service pytest tests/ -v
	docker-compose run --rm auth-service pytest tests/ -v
	docker-compose run --rm customer-service pytest tests/ -v

test-core:
	@echo "Executando testes do core-service..."
	docker-compose run --rm core-service pytest tests/ -v

test-sales:
	@echo "Executando testes do sales-service..."
	docker-compose run --rm sales-service pytest tests/ -v

test-auth:
	@echo "Executando testes do auth-service..."
	docker-compose run --rm auth-service pytest tests/ -v

test-customer:
	@echo "Executando testes do customer-service..."
	docker-compose run --rm customer-service pytest tests/ -v

test-rate-limiting:
	@echo "Testando rate limiting..."
	@chmod +x scripts/test-rate-limiting.sh
	@./scripts/test-rate-limiting.sh

test-frontend:
	@echo "Testando frontend..."
	@chmod +x scripts/test-frontend.sh
	@./scripts/test-frontend.sh

logs:
	docker-compose logs -f

clean:
	@echo "Limpando ambiente..."
	docker-compose down -v
	docker system prune -f

run:
	docker-compose up

stop:
	docker-compose stop

mongodb:
	docker-compose up -d core-mongodb sales-mongodb auth-mongodb customer-mongodb

mongodb-logs:
	docker-compose logs -f core-mongodb sales-mongodb auth-mongodb customer-mongodb

redis:
	docker-compose up -d redis

redis-logs:
	docker-compose logs -f redis

redis-cli:
	@echo "Conectando ao Redis CLI..."
	docker-compose exec redis redis-cli

clean-redis:
	@echo "Limpando dados do Redis..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "Dados do Redis limpos com sucesso!"

keycloak:
	@echo "🔑 Iniciando Keycloak..."
	docker-compose up -d keycloak

keycloak-logs:
	@echo "📋 Mostrando logs do Keycloak..."
	docker-compose logs -f keycloak

keycloak-setup:
	@echo "🚀 Configurando Keycloak..."
	./scripts/setup-keycloak.sh

keycloak-secret:
	@echo "🔐 Obtendo client secret do Keycloak..."
	./scripts/get-keycloak-client-secret.sh

keycloak-secret-prod:
	@echo "🔐 Obtendo client secret do Keycloak (Produção)..."
	@chmod +x scripts/get-keycloak-client-secret-prod.sh
	./scripts/get-keycloak-client-secret-prod.sh production

keycloak-secret-staging:
	@echo "🔐 Obtendo client secret do Keycloak (Staging)..."
	@chmod +x scripts/get-keycloak-client-secret-prod.sh
	./scripts/get-keycloak-client-secret-prod.sh staging

keycloak-secret-dev:
	@echo "🔐 Obtendo client secret do Keycloak (Development)..."
	@chmod +x scripts/get-keycloak-client-secret-prod.sh
	./scripts/get-keycloak-client-secret-prod.sh development

keycloak-console:
	@echo "🌐 Console Admin do Keycloak:"
	@echo "   URL: http://localhost:8080/admin"
	@echo "   Usuário: admin"
	@echo "   Senha: admin123"
	@echo ""
	@echo "📖 Para configuração manual, consulte:"
	@echo "   scripts/manual-keycloak-setup.md"
	@echo ""
	@echo "🚀 Para produção, use:"
	@echo "   make keycloak-secret-prod"
	@echo "   make keycloak-secret-staging"

keycloak-validate:
	@echo "🔍 Validando configuração do Keycloak..."
	@chmod +x scripts/validate-keycloak.sh
	@./scripts/validate-keycloak.sh

keycloak-quickstart:
	@echo "🚀 Guia de Início Rápido do Keycloak:"
	@echo "   1. make keycloak"
	@echo "   2. make keycloak-setup"
	@echo "   3. make keycloak-secret"
	@echo "   4. make keycloak-validate"
	@echo ""
	@echo "📖 Documentação completa:"
	@echo "   - docs/KEYCLOAK_QUICKSTART.md"
	@echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"

keycloak-stop:
	@echo "🛑 Parando Keycloak..."
	docker-compose stop keycloak

keycloak-restart:
	@echo "🔄 Reiniciando Keycloak..."
	docker-compose restart keycloak

keycloak-clean:
	@echo "🧹 Limpando dados do Keycloak..."
	docker-compose down
	docker volume rm fiap-prova-sub-fase-3_keycloak-data 2>/dev/null || true
	@echo "✅ Dados do Keycloak removidos!"

core:
	docker-compose up -d core-service

sales:
	docker-compose up -d sales-service

auth:
	docker-compose up -d auth-service

customer:
	docker-compose up -d customer-service

frontend:
	docker-compose up -d frontend

core-logs:
	docker-compose logs -f core-service

sales-logs:
	docker-compose logs -f sales-service

auth-logs:
	docker-compose logs -f auth-service

customer-logs:
	docker-compose logs -f customer-service

frontend-logs:
	docker-compose logs -f frontend

frontend-build:
	@echo "Fazendo build do frontend..."
	docker-compose run --rm frontend npm run build

frontend-test:
	@echo "Executando testes do frontend..."
	docker-compose run --rm frontend npm test -- --coverage --watchAll=false

frontend-lint:
	@echo "Executando linter do frontend..."
	docker-compose run --rm frontend npm run lint

frontend-format:
	@echo "Formatando código do frontend..."
	docker-compose run --rm frontend npm run format

lint:
	@echo "Executando linter..."
	docker-compose run --rm core-service flake8 app/
	docker-compose run --rm sales-service flake8 app/
	docker-compose run --rm auth-service flake8 app/
	docker-compose run --rm customer-service flake8 app/
	docker-compose run --rm frontend npm run lint

type-check:
	@echo "Verificando tipos..."
	docker-compose run --rm core-service mypy app/
	docker-compose run --rm sales-service mypy app/
	docker-compose run --rm auth-service mypy app/
	docker-compose run --rm customer-service mypy app/

rebuild:
	@echo "Reconstruindo containers..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

status:
	@echo "Status dos serviços:"
	docker-compose ps

restart:
	@echo "Reiniciando serviços..."
	docker-compose restart
	docker-compose logs -f

clean-sales-db:
	@echo "Limpando banco de dados do sales-service..."
	docker-compose exec sales-mongodb mongosh sales_db --eval "db.sales.deleteMany({})"
	@echo "Banco de dados limpo com sucesso!"

clean-core-db:
	@echo "Limpando banco de dados do core-service..."
	docker-compose exec core-mongodb mongosh core_db --eval "db.vehicles.deleteMany({})"
	@echo "Banco de dados limpo com sucesso!"

clean-auth-db:
	@echo "Limpando banco de dados do auth-service..."
	docker-compose exec auth-mongodb mongosh auth_db --eval "db.users.deleteMany({})"
	@echo "Banco de dados limpo com sucesso!"

clean-customer-db:
	@echo "Limpando banco de dados do customer-service..."
	docker-compose exec customer-mongodb mongosh customer_db --eval "db.customers.deleteMany({})"
	@echo "Banco de dados limpo com sucesso!"

clean-dbs: clean-sales-db clean-core-db clean-auth-db clean-customer-db

coverage:
	@echo "Executando cobertura de testes para todos os serviços..."
	docker-compose run --rm core-service pytest tests/ --cov=app --cov-report=term-missing
	docker-compose run --rm sales-service pytest tests/ --cov=app --cov-report=term-missing
	docker-compose run --rm auth-service pytest tests/ --cov=app --cov-report=term-missing
	docker-compose run --rm customer-service pytest tests/ --cov=app --cov-report=term-missing

coverage-core:
	@echo "Executando cobertura de testes do core-service..."
	docker-compose run --rm core-service pytest tests/ --cov=app --cov-report=term-missing

coverage-sales:
	@echo "Executando cobertura de testes do sales-service..."
	docker-compose run --rm sales-service pytest tests/ --cov=app --cov-report=term-missing

coverage-auth:
	@echo "Executando cobertura de testes do auth-service..."
	docker-compose run --rm auth-service pytest tests/ --cov=app --cov-report=term-missing

coverage-customer:
	@echo "Executando cobertura de testes do customer-service..."
	docker-compose run --rm customer-service pytest tests/ --cov=app --cov-report=term-missing

coverage-report:
	@echo "Gerando relatório de cobertura..."
	docker-compose run --rm core-service pytest tests/ --cov=app --cov-report=html
	docker-compose run --rm sales-service pytest tests/ --cov=app --cov-report=html
	docker-compose run --rm auth-service pytest tests/ --cov=app --cov-report=html
	docker-compose run --rm customer-service pytest tests/ --cov=app --cov-report=html
	@echo "Relatórios gerados em:"
	@echo "core-service: htmlcov/index.html"
	@echo "sales-service: htmlcov/index.html" 
	@echo "auth-service: htmlcov/index.html"
	@echo "customer-service: htmlcov/index.html" 

setup-env:
	@echo "Configurando ambiente..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh development

setup-env-staging:
	@echo "Configurando ambiente de staging..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh staging

setup-env-production:
	@echo "Configurando ambiente de produção..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh production

validate-env:
	@echo "Validando configuração do ambiente..."
	@if [ -f "scripts/validate-env.sh" ]; then \
		chmod +x scripts/validate-env.sh && ./scripts/validate-env.sh; \
	else \
		echo "Script de validação não encontrado"; \
	fi

docs:
	@echo "Abrindo documentação..."
	@echo "Documentação disponível em:"
	@echo "- README.md"
	@echo "- docs/ARCHITECTURE.md"
	@echo "- docs/DEPLOYMENT.md"
	@echo "- docs/API_DOCUMENTATION.md"
	@echo "- docs/ENVIRONMENT_VARIABLES.md"
	@echo "- docs/KEYCLOAK_QUICKSTART.md"
	@echo "- docs/KEYCLOAK_PRODUCTION_GUIDE.md"
	@echo ""
	@echo "Swagger UI disponível em:"
	@echo "- Auth Service: http://localhost:8002/docs"
	@echo "- Core Service: http://localhost:8000/docs"
	@echo "- Sales Service: http://localhost:8001/docs"
	@echo "- Customer Service: http://localhost:8003/docs"
	@echo ""
	@echo "População de Dados:"
	@echo "- Dados de teste: make populate-data"
	@echo "- Dados limpos: make populate-data-clean"
	@echo "- Testar sistema: make test-populate-data"
	@echo ""
	@echo "Rate Limiting Management:"
	@echo "- Stats: http://localhost:8002/rate-limit/stats"
	@echo "- Config: http://localhost:8002/rate-limit/config"
	@echo "- Test: make test-rate-limiting"
	@echo ""
	@echo "Keycloak:"
	@echo "- Console: http://localhost:8080/admin"
	@echo "- Validate: make keycloak-validate"
	@echo "- Quickstart: make keycloak-quickstart" 

# Configuração do Keycloak e Admin
setup-admin:
	@echo "🔧 Configurando usuário admin no Keycloak..."
	@./scripts/setup-admin.sh

fix-keycloak:
	@echo "🔧 Corrigindo configuração do client no Keycloak..."
	@./scripts/fix-keycloak.sh

setup-complete:
	@echo "🚀 Configuração completa do sistema..."
	@./scripts/setup-complete.sh 