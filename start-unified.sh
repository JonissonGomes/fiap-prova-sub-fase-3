#!/bin/bash
set -e

echo "🚀 Iniciando FIAP Unified Backend Service..."

# Configurar variáveis de ambiente padrão
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}

# Aguardar dependências externas (MongoDB, Redis)
echo "⏳ Aguardando dependências externas..."

# Função para aguardar serviço
wait_for_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Aguardando $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "$service_url" > /dev/null 2>&1; then
            echo "✅ $service_name está disponível"
            return 0
        fi
        
        echo "⏳ Tentativa $attempt/$max_attempts - $service_name não está pronto"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Timeout aguardando $service_name"
    return 1
}

# Aguardar MongoDB se configurado
if [ -n "$MONGODB_URL" ]; then
    echo "🔍 Verificando MongoDB..."
    # Não aguardar MongoDB pois pode não estar disponível em desenvolvimento
    # wait_for_service "MongoDB" "$MONGODB_URL"
fi

# Aguardar Redis se configurado
if [ -n "$REDIS_URL" ]; then
    echo "🔍 Verificando Redis..."
    # Não aguardar Redis pois pode não estar disponível em desenvolvimento
    # wait_for_service "Redis" "$REDIS_URL"
fi

# Configurar Nginx
echo "🔧 Configurando Nginx..."
nginx -t || {
    echo "❌ Erro na configuração do Nginx"
    exit 1
}

# Mostrar informações do serviço
echo "📋 Configuração do serviço:"
echo "   - Porta: $PORT"
echo "   - Ambiente: $ENVIRONMENT"
echo "   - MongoDB: ${MONGODB_URL:-'Não configurado'}"
echo "   - Redis: ${REDIS_URL:-'Não configurado'}"
echo "   - Frontend: Servido pela Vercel"

# Iniciar Supervisor
echo "🎯 Iniciando todos os microserviços backend..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 