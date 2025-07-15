#!/bin/bash

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 

# Script completo para configurar o sistema de vendas de veículos

set -e

echo "🚀 Configuração Completa do Sistema de Vendas de Veículos"
echo "=" * 60

# Passo 1: Configurar usuário admin no Keycloak
echo "🔧 Passo 1: Configurando usuário admin no Keycloak..."
./scripts/setup-admin.sh

echo ""
echo "🔧 Passo 2: Corrigindo configuração do client no Keycloak..."
./scripts/fix-keycloak.sh

echo ""
echo "🔧 Passo 3: Sincronizando usuário admin no MongoDB..."
docker-compose exec -T auth-service bash -c "
    pip install motor passlib --quiet
    cat > /tmp/sync_admin.py << 'EOF'
$(cat "$(dirname "$0")/sync-admin-user.py")
EOF
    cd /app && python3 /tmp/sync_admin.py
    rm -f /tmp/sync_admin.py
"

echo ""
echo "🔧 Passo 4: Populando dados de teste..."
./scripts/populate-data-working.sh

echo ""
echo "=" * 60
echo "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!"
echo "=" * 60
echo ""
echo "🔐 Credenciais do Admin:"
echo "   Email: admin@vehiclesales.com"
echo "   Senha: admin123"
echo ""
echo "🔗 Acesse o sistema:"
echo "   - Frontend: http://localhost:3000"
echo "   - Auth Service: http://localhost:8002"
echo "   - Core Service: http://localhost:8000"
echo "   - Sales Service: http://localhost:8001"
echo "   - Customer Service: http://localhost:8003"
echo "   - Keycloak: http://localhost:8080/admin"
echo ""
echo "📊 Dados criados:"
echo "   - 100 veículos com dados realistas"
echo "   - Usuário admin configurado"
echo "   - Sistema de autenticação funcionando"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Acesse o frontend em http://localhost:3000"
echo "   2. Faça login com as credenciais do admin"
echo "   3. Explore os veículos criados"
echo "   4. Teste as funcionalidades do sistema"
echo ""
echo "=" * 60 