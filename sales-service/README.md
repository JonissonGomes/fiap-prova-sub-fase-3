# Serviço de Vendas

## Visão Geral
Serviço responsável pelo gerenciamento de vendas de veículos, incluindo cadastro, atualização e controle de status de pagamento.

## Status de Pagamento
- PENDING: Pagamento pendente
- PAID: Pagamento confirmado
- CANCELLED: Venda cancelada

## Fluxo de Venda
1. Venda é criada com status PENDING
2. Após confirmação do pagamento, status muda para PAID
3. Em caso de cancelamento, status muda para CANCELLED
4. Ao confirmar pagamento, status do veículo muda automaticamente para VENDIDO

## Endpoints
- GET /sales - Lista todas as vendas
- GET /sales/{id} - Obtém uma venda específica
- POST /sales - Cria uma nova venda
- PUT /sales/{id} - Atualiza uma venda
- PATCH /sales/{id}/status - Atualiza o status de pagamento
- DELETE /sales/{id} - Remove uma venda

## Requisitos
- Python 3.8+
- FastAPI
- MongoDB
- Pydantic
- Motor

## Instalação
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure as variáveis de ambiente no arquivo `.env`
3. Execute o serviço: `uvicorn app.main:app --reload`

## Comandos de Execução

### Desenvolvimento
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor de desenvolvimento
uvicorn app.main:app --reload

# Iniciar com configurações específicas
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Docker
```bash
# Construir a imagem
docker build -t sales-service .

# Executar o container
docker run -p 8001:8001 sales-service

# Executar com variáveis de ambiente
docker run -p 8001:8001 \
  -e MONGODB_URL=mongodb://localhost:27017 \
  -e DATABASE_NAME=sales_db \
  -e VEHICLE_SERVICE_URL=http://vehicle-service:8000 \
  sales-service
```

### Docker Compose
```bash
# Iniciar o serviço com os outros serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar os serviços
docker-compose down
```

### Testes
```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=app tests/

# Executar testes específicos
pytest tests/test_sales.py

# Executar testes com relatório HTML
pytest --cov=app --cov-report=html tests/
```

### Qualidade de Código
```bash
# Executar linter
flake8 app tests

# Verificar tipos
mypy app tests

# Formatar código
black app tests

# Verificar imports
isort app tests
```

## Estrutura do Projeto
```
app/
  ├── main.py        # Configuração do FastAPI
  ├── models/        # Modelos do MongoDB
  ├── schemas/       # Schemas Pydantic
  ├── services/      # Lógica de negócio
  ├── controllers/   # Controladores da API
  └── utils/         # Funções utilitárias
```

## Tecnologias

- Python 3.11
- FastAPI
- MongoDB
- Docker
- Pytest

## Estrutura do Projeto

```
sales-service/
├── app/
│   ├── adapters/
│   │   └── mongodb_sale_repository.py
│   ├── domain/
│   │   └── sale.py
│   ├── ports/
│   │   └── sale_repository.py
│   ├── schemas/
│   │   └── sale_schema.py
│   └── services/
│       └── sale_service_impl.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_sale.py
├── .env.example
├── .env.test
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Configuração do Ambiente

1. Clone o repositório
2. Copie o arquivo `.env.example` para `.env` e configure as variáveis de ambiente
3. Execute `make setup` para configurar o ambiente
4. Execute `make install` para instalar as dependências

## Comandos Disponíveis

- `make setup`: Configura o ambiente
- `make install`: Instala as dependências
- `make up`: Inicia os serviços em background
- `make down`: Para os serviços
- `make test`: Executa os testes
- `make test-sales`: Executa os testes do sales-service
- `make logs`: Mostra os logs dos serviços
- `make clean`: Limpa o ambiente
- `make run`: Inicia os serviços em primeiro plano
- `make stop`: Para os serviços
- `make mongodb`: Inicia o MongoDB
- `make mongodb-logs`: Mostra os logs do MongoDB
- `make sales`: Inicia o sales-service
- `make sales-logs`: Mostra os logs do sales-service
- `make lint`: Executa o linter
- `make type-check`: Executa a verificação de tipos
- `make rebuild`: Reconstrui os containers
- `make status`: Mostra o status dos serviços
- `make restart`: Reinicia os serviços

## API

### Vendas

- `GET /sales`: Lista todas as vendas
- `GET /sales/{id}`: Obtém uma venda pelo ID
- `GET /sales/vehicle/{vehicle_id}`: Obtém vendas por veículo
- `GET /sales/payment/{payment_code}`: Obtém vendas por código de pagamento
- `GET /sales/status/{status}`: Obtém vendas por status
- `POST /sales`: Cria uma nova venda
- `PUT /sales/{id}`: Atualiza uma venda
- `PUT /sales/{id}/payment-status`: Atualiza o status de pagamento
- `DELETE /sales/{id}`: Remove uma venda

## Testes

Para executar os testes:

```bash
make test
```

Para executar os testes com cobertura:

```bash
docker-compose run --rm sales-service pytest tests/ --cov=app --cov-report=term-missing -v
```

## Docker

O projeto usa Docker para desenvolvimento e produção. Existem dois Dockerfiles:

- `Dockerfile`: Para produção
- `Dockerfile.dev`: Para desenvolvimento

Para desenvolvimento:

```bash
make up
```

Para produção:

```bash
docker-compose -f docker-compose.prod.yml up -d
``` 