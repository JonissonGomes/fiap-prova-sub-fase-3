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
COPY package*.json ./

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependências Node.js (se existir)
RUN if [ -f package.json ]; then npm ci; fi

# Copiar todo o código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização usando Makefile
CMD ["make", "start-production"] 