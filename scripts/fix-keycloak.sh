#!/bin/bash

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para corrigir a configuração do client no Keycloak

set -e

echo "🔧 Corrigindo configuração do client no Keycloak..."

# Executa o script de correção dentro do container
echo "🐳 Executando correção do client..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/fix_client.py << 'EOF'
$(cat "$(dirname "$0")/fix-keycloak-client.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/fix_client.py
    
    # Remove o arquivo temporário
    rm -f /tmp/fix_client.py
"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 