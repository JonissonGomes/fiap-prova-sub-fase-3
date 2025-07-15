# Script PowerShell para configuração completa do sistema (Windows)
# Uso: powershell -ExecutionPolicy Bypass -File scripts/setup-complete.ps1

param(
    [string]$Environment = "development"
)

# Função para logging com cores
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Função para verificar se comando existe
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Função para verificar se Docker está rodando
function Test-Docker {
    try {
        $result = docker info 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# Função para aguardar serviço
function Wait-ForService {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 120
    )
    
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 5
            $elapsed += 5
        }
    }
    return $false
}

# Cabeçalho
Write-Host "🚀 Configuração Completa do Sistema de Vendas de Veículos" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Verificar pré-requisitos
Write-Info "Verificando pré-requisitos..."

if (-not (Test-Command "docker")) {
    Write-Error "Docker não está instalado ou não está no PATH"
    Write-Info "Instale Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

if (-not (Test-Command "docker-compose")) {
    Write-Error "Docker Compose não está instalado"
    Write-Info "Instale Docker Compose ou use Docker Desktop"
    exit 1
}

if (-not (Test-Docker)) {
    Write-Error "Docker não está rodando"
    Write-Info "Inicie Docker Desktop e tente novamente"
    exit 1
}

if (-not (Test-Command "python")) {
    Write-Error "Python não está instalado ou não está no PATH"
    Write-Info "Instale Python 3.8+ via Microsoft Store ou python.org"
    exit 1
}

Write-Success "Todos os pré-requisitos estão disponíveis!"

# Passo 1: Iniciar serviços
Write-Info "Passo 1: Iniciando serviços Docker..."
try {
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao iniciar serviços"
    }
    Write-Success "Serviços iniciados com sucesso"
} catch {
    Write-Error "Erro ao iniciar serviços: $($_.Exception.Message)"
    exit 1
}

# Passo 2: Aguardar Keycloak
Write-Info "Passo 2: Aguardando Keycloak inicializar..."
if (Wait-ForService "http://localhost:8080/health" 300) {
    Write-Success "Keycloak está disponível"
} else {
    Write-Error "Keycloak não iniciou a tempo"
    exit 1
}

# Passo 3: Configurar Keycloak
Write-Info "Passo 3: Configurando Keycloak..."
try {
    python scripts/setup-admin-user.py
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na configuração do Keycloak"
    }
    Write-Success "Keycloak configurado com sucesso"
} catch {
    Write-Error "Erro ao configurar Keycloak: $($_.Exception.Message)"
    exit 1
}

# Passo 4: Aguardar todos os serviços
Write-Info "Passo 4: Aguardando todos os serviços..."

$services = @{
    "Auth Service" = "http://localhost:8002/health"
    "Core Service" = "http://localhost:8000/health"
    "Sales Service" = "http://localhost:8001/health"
    "Customer Service" = "http://localhost:8003/health"
}

foreach ($service in $services.GetEnumerator()) {
    Write-Info "Aguardando $($service.Key)..."
    if (Wait-ForService $service.Value 120) {
        Write-Success "$($service.Key) está disponível"
    } else {
        Write-Warning "$($service.Key) não respondeu a tempo"
    }
}

# Passo 5: Popular dados
Write-Info "Passo 5: Populando dados de teste..."
try {
    python scripts/populate-data.py
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao popular dados"
    }
    Write-Success "Dados populados com sucesso"
} catch {
    Write-Error "Erro ao popular dados: $($_.Exception.Message)"
    Write-Warning "Você pode tentar novamente mais tarde com: python scripts/populate-data.py"
}

# Resultado final
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ CONFIGURAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host ""
Write-Host "🔐 Credenciais do Admin:" -ForegroundColor Yellow
Write-Host "   Email: admin@vehiclesales.com" -ForegroundColor White
Write-Host "   Senha: admin123" -ForegroundColor White

Write-Host ""
Write-Host "🔗 Acesse o sistema:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - Auth Service: http://localhost:8002" -ForegroundColor White
Write-Host "   - Core Service: http://localhost:8000" -ForegroundColor White
Write-Host "   - Sales Service: http://localhost:8001" -ForegroundColor White
Write-Host "   - Customer Service: http://localhost:8003" -ForegroundColor White
Write-Host "   - Keycloak: http://localhost:8080/admin" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Comandos úteis:" -ForegroundColor Yellow
Write-Host "   - Parar serviços: docker-compose down" -ForegroundColor White
Write-Host "   - Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   - Reiniciar: docker-compose restart" -ForegroundColor White
Write-Host "   - Verificar status: docker-compose ps" -ForegroundColor White

Write-Host ""
Write-Host "📚 Documentação:" -ForegroundColor Yellow
Write-Host "   - README.md" -ForegroundColor White
Write-Host "   - docs/CROSS_PLATFORM_COMPATIBILITY.md" -ForegroundColor White
Write-Host "   - docs/API_DOCUMENTATION.md" -ForegroundColor White

Write-Host ""
Write-Success "Sistema pronto para uso!" 