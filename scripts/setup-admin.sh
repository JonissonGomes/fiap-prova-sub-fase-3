#!/bin/bash

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 

# Script para configurar o usuário admin no Keycloak
# Resolve problemas de roles não encontradas e usuário admin não criado

set -e

echo "🔧 Configurando usuário admin no Keycloak..."

# Verifica se o Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker para continuar."
    exit 1
fi

# Verifica se o docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não encontrado. Instale o docker-compose para continuar."
    exit 1
fi

# Verifica se o Keycloak está rodando
echo "🔍 Verificando se o Keycloak está rodando..."
if ! curl -s -f "http://localhost:8080/" > /dev/null 2>&1; then
    echo "❌ Keycloak não está rodando. Execute 'make up' primeiro."
    exit 1
fi

echo "✅ Keycloak está rodando!"

# Aguarda o Keycloak estar completamente inicializado
echo "⏳ Aguardando Keycloak inicializar completamente..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "http://localhost:8080/admin/" > /dev/null 2>&1; then
        echo "✅ Keycloak está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Timeout aguardando Keycloak inicializar"
    exit 1
fi

# Executa o script de configuração dentro do container
echo "🐳 Executando configuração do admin..."
docker-compose exec -T auth-service bash -c "
    # Instala dependências necessárias
    pip install python-keycloak --quiet
    
    # Cria o script Python temporário
    cat > /tmp/setup_admin.py << 'EOF'
$(cat "$(dirname "$0")/setup-admin-user.py")
EOF
    
    # Executa o script
    cd /app && python3 /tmp/setup_admin.py
    
    # Remove o arquivo temporário
    rm -f /tmp/setup_admin.py
"

echo ""
echo "✅ Configuração do admin concluída!"
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo "   Role: ADMIN"
echo ""
echo "🔗 Acesse o sistema:"
echo "   Frontend: http://localhost:3000"
echo "   Keycloak: http://localhost:8080/admin"
echo ""
echo "🚀 Agora você pode executar:"
echo "   make populate-data"
echo "" 