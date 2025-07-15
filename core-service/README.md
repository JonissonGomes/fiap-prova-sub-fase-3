# Core Service

Serviço responsável pelo gerenciamento de veículos.

## Requisitos

- Python 3.11+
- MongoDB
- Docker (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd core-service
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

## Executando

### Desenvolvimento
```bash
uvicorn app.adapters.api.main:app --reload
```

### Produção
```bash
docker-compose up -d
```

## Testes

### Executando testes
```bash
pytest
```

### Cobertura de testes
```bash
pytest --cov=app --cov-report=term-missing
```

## CI/CD

O projeto utiliza GitHub Actions para CI/CD:

- **CI**: Executa testes, linting e type checking em cada PR
- **CD**: Faz deploy automático para produção quando o PR é mergeado na main

## Documentação da API

A documentação da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contribuição

1. Crie uma branch para sua feature:
```bash
git checkout -b feature/nova-feature
```

2. Faça commit das suas alterações:
```bash
git commit -m "feat: adiciona nova feature"
```

3. Push para a branch:
```bash
git push origin feature/nova-feature
```

4. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT.