FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verifica se python-jose foi instalado
RUN python -c "import jose; print('python-jose instalado com sucesso')"

# Copia o código fonte
COPY . .

# Se estiver rodando testes, use o .env.test
ARG ENV_FILE=.env
COPY ${ENV_FILE} .env

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"] 