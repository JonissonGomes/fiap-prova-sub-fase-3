FROM python:3.11-slim

WORKDIR /app

# Copia os arquivos de requisitos e setup
COPY requirements.txt .
COPY setup.py .

# Instala o pacote
RUN pip install -e .

# Copia o código fonte
COPY . .

# Se estiver rodando testes, use o .env.test
ARG ENV_FILE=.env
COPY ${ENV_FILE} .env

EXPOSE 8001

CMD ["uvicorn", "app.adapters.api.main:app", "--host", "0.0.0.0", "--port", "8001"] 