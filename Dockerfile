# Dockerfile principal para o sistema FIAP
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    make \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar Makefile e arquivos de configuração
COPY Makefile .
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Instalar dependências Node.js (se existir) - movido para depois de copiar o código
RUN if [ -f package.json ]; then npm install; fi

# Expor porta
EXPOSE 8000

# Comando de inicialização usando Makefile
CMD ["make", "start-production"] 