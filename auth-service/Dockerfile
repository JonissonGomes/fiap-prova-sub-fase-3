FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --force-reinstall email-validator==2.1.0 && \
    pip install --no-cache-dir --force-reinstall "pydantic[email]==2.5.0" && \
    pip install --no-cache-dir -r requirements.txt

# Verificar se email-validator foi instalado
RUN python -c "import email_validator; print('email-validator instalado:', email_validator.__version__)"

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 