#!/bin/bash

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 

# Script de validação do Keycloak
# Verifica se a configuração está correta

set -e

echo "🔍 Validando configuração do Keycloak..."
echo "================================="

# Função para mostrar status
show_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
        return 1
    fi
}

# Função para testar conectividade
test_connection() {
    local url=$1
    local description=$2
    
    if curl -s --connect-timeout 5 "$url" > /dev/null 2>&1; then
        show_status 0 "$description"
        return 0
    else
        show_status 1 "$description"
        return 1
    fi
}

# Contador de erros
ERRORS=0

echo ""
echo "📡 Testando conectividade..."
echo "----------------------------"

# 1. Verificar se Keycloak está rodando
if test_connection "http://localhost:8080/realms/master" "Keycloak está acessível"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak"
fi

# 2. Verificar se realm existe
if test_connection "http://localhost:8080/realms/vehicle-sales" "Realm 'vehicle-sales' existe"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-setup"
fi

echo ""
echo "📁 Verificando arquivos..."
echo "-------------------------"

# 3. Verificar se client secret existe
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    show_status 0 "Client secret foi obtido"
    
    # Verificar se o arquivo não está vazio
    if [ -s "/tmp/keycloak-credentials-development.env" ]; then
        show_status 0 "Arquivo de credenciais não está vazio"
    else
        show_status 1 "Arquivo de credenciais está vazio"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make keycloak-secret"
    fi
else
    show_status 1 "Client secret não foi obtido"
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make keycloak-secret"
fi

echo ""
echo "🔧 Verificando serviços..."
echo "-------------------------"

# 4. Verificar se auth service está rodando
if test_connection "http://localhost:8002/health" "Auth Service está rodando"; then
    :
else
    ERRORS=$((ERRORS + 1))
    echo "💡 Solução: make auth ou make up"
fi

# 5. Verificar se Redis está rodando (para rate limiting)
if test_connection "http://localhost:6379" "Redis está acessível" 2>/dev/null; then
    show_status 0 "Redis está rodando"
else
    # Redis pode não estar rodando em HTTP, tentar ping
    if docker-compose ps redis | grep -q "Up"; then
        show_status 0 "Redis está rodando (via Docker)"
    else
        show_status 1 "Redis não está rodando"
        ERRORS=$((ERRORS + 1))
        echo "💡 Solução: make redis"
    fi
fi

echo ""
echo "🔐 Testando autenticação..."
echo "---------------------------"

# 6. Testar autenticação
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' 2>/dev/null)

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    show_status 0 "Autenticação funcionando"
    
    # Extrair token para testes adicionais
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
    
    if [ -n "$TOKEN" ]; then
        # Testar endpoint protegido
        PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8002/auth/profile \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            show_status 0 "Endpoint protegido funcionando"
        else
            show_status 1 "Endpoint protegido não funcionando"
            ERRORS=$((ERRORS + 1))
        fi
    fi
else
    show_status 1 "Erro na autenticação"
    ERRORS=$((ERRORS + 1))
    echo "💡 Resposta: $AUTH_RESPONSE"
    echo "💡 Soluções:"
    echo "   - Verificar se usuário admin existe no Keycloak"
    echo "   - Verificar se client secret está correto"
    echo "   - Verificar logs: make auth-logs"
fi

echo ""
echo "🌐 Verificando URLs importantes..."
echo "--------------------------------"

# URLs importantes
URLS=(
    "http://localhost:8080/admin|Console Admin Keycloak"
    "http://localhost:8002/docs|Auth Service Swagger"
    "http://localhost:8000/docs|Core Service Swagger"
    "http://localhost:8001/docs|Sales Service Swagger"
    "http://localhost:8003/docs|Customer Service Swagger"
)

for url_info in "${URLS[@]}"; do
    IFS='|' read -r url description <<< "$url_info"
    if test_connection "$url" "$description"; then
        :
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📊 Resumo da validação"
echo "====================="

if [ $ERRORS -eq 0 ]; then
    echo "🎉 Configuração do Keycloak está CORRETA!"
    echo ""
    echo "✅ Todos os testes passaram"
    echo "✅ Sistema pronto para uso"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Acessar frontend: http://localhost:3000"
    echo "   2. Fazer login com admin/admin123"
    echo "   3. Testar funcionalidades"
    echo ""
    echo "📚 Documentação:"
    echo "   - README.md"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/API_DOCUMENTATION.md"
else
    echo "❌ Encontrados $ERRORS problema(s)"
    echo ""
    echo "🔧 Soluções rápidas:"
    echo "   1. Reiniciar Keycloak: make keycloak-restart"
    echo "   2. Reconfigurar: make keycloak-setup"
    echo "   3. Obter novo secret: make keycloak-secret"
    echo "   4. Verificar logs: make keycloak-logs"
    echo "   5. Limpar e recriar: make keycloak-clean && make keycloak"
    echo ""
    echo "📖 Guias de ajuda:"
    echo "   - docs/KEYCLOAK_QUICKSTART.md"
    echo "   - docs/KEYCLOAK_PRODUCTION_GUIDE.md"
    
    exit 1
fi

echo ""
echo "🔐 Credenciais importantes:"
echo "=========================="
echo "Keycloak Admin Console:"
echo "  URL: http://localhost:8080/admin"
echo "  Usuário: admin"
echo "  Senha: admin123"
echo ""
echo "Usuário da aplicação:"
echo "  Username: admin"
echo "  Password: admin123"
echo "  Role: ADMIN"
echo ""
echo "Client credentials:"
if [ -f "/tmp/keycloak-credentials-development.env" ]; then
    echo "  Arquivo: /tmp/keycloak-credentials-development.env"
    echo "  Conteúdo:"
    cat /tmp/keycloak-credentials-development.env | sed 's/^/    /'
else
    echo "  ❌ Arquivo não encontrado"
fi 