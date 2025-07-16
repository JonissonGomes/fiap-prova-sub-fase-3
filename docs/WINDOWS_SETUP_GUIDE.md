# Guia de Configuração para Windows

## 📋 Pré-requisitos

### 1. Instalar Docker Desktop
- Baixar em: https://www.docker.com/products/docker-desktop
- Instalar e garantir que está rodando
- Verificar: `docker --version`

### 2. Instalar Python 3.8+
- **Opção 1 (Recomendada)**: Microsoft Store
  - Abrir Microsoft Store
  - Buscar "Python 3.11" ou "Python 3.12"
  - Instalar

- **Opção 2**: Python.org
  - Baixar em: https://www.python.org/downloads/
  - Marcar "Add Python to PATH"

### 3. Instalar Git
- Baixar em: https://git-scm.com/download/win
- Instalar com Git Bash (importante!)

## 🚀 Configuração Rápida

### Método 1: Script PowerShell (Recomendado)
```powershell
# Abrir PowerShell como Administrador
# Navegar até o diretório do projeto
cd fiap-prova-sub-fase-3

# Executar script de configuração
powershell -ExecutionPolicy Bypass -File scripts/setup-complete.ps1
```

### Método 2: Git Bash
```bash
# Abrir Git Bash
# Navegar até o diretório do projeto
cd fiap-prova-sub-fase-3

# Executar script bash
./scripts/setup-complete.sh
```

### Método 3: Python Direto
```cmd
# Abrir Prompt de Comando
# Navegar até o diretório do projeto
cd fiap-prova-sub-fase-3

# Verificar dependências
python scripts/check-dependencies.py

# Iniciar serviços
docker-compose up -d

# Configurar sistema
python scripts/setup-admin-user.py
python scripts/populate-data.py
```

## 🔧 Comandos Úteis

### Verificar Sistema
```cmd
# Verificar compatibilidade
python scripts/check-dependencies.py

# Verificar com Make (se disponível)
make check-dependencies
```

### Gerenciar Serviços
```cmd
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Ver logs
docker-compose logs -f

# Status dos serviços
docker-compose ps
```

### Popular Dados
```cmd
# Método recomendado
python scripts/populate-data.py

# Ou com Make
make populate-data
```

## 🐛 Resolução de Problemas

### Problema: "docker não é reconhecido"
**Solução**: 
- Verificar se Docker Desktop está rodando
- Adicionar Docker ao PATH do sistema
- Reiniciar terminal

### Problema: "python não é reconhecido"
**Solução**:
- Instalar Python via Microsoft Store
- Ou adicionar Python ao PATH
- Usar `py` ao invés de `python`

### Problema: "Scripts .sh não funcionam"
**Solução**:
- Usar Git Bash
- Ou usar scripts PowerShell equivalentes
- Ou executar comandos Python diretamente

### Problema: "Execution Policy"
**Solução**:
```powershell
# Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser

# Ou executar com parâmetro
powershell -ExecutionPolicy Bypass -File script.ps1
```

### Problema: Portas em uso
**Solução**:
```cmd
# Verificar portas em uso
netstat -an | findstr :8000

# Parar processos se necessário
taskkill /F /PID <PID>

# Ou usar diferentes portas no docker-compose.yml
```

## 📚 Alternativas de Terminal

### 1. Git Bash (Recomendado)
- Vem com Git for Windows
- Suporta comandos Unix
- Roda scripts .sh nativamente

### 2. PowerShell
- Nativo do Windows
- Scripts .ps1 funcionam bem
- Melhor integração com Windows

### 3. WSL2 (Avançado)
- Subsistema Linux completo
- Ideal para desenvolvimento
- Requer configuração adicional

### 4. Command Prompt
- Terminal padrão do Windows
- Limitado mas funcional
- Usar apenas comandos Python/Docker

## 🎯 Configuração Recomendada

### Para Usuários Iniciantes:
1. Instalar Docker Desktop
2. Instalar Python via Microsoft Store
3. Usar scripts PowerShell
4. Usar interface gráfica do Docker Desktop

### Para Desenvolvedores:
1. Instalar Docker Desktop
2. Instalar Git com Git Bash
3. Instalar Python
4. Usar Git Bash para scripts
5. Considerar WSL2 para projetos maiores

## 🔗 Links Úteis

- [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)
- [Python no Microsoft Store](https://www.microsoft.com/store/productId/9PJPW5LDXLZ5)
- [Git for Windows](https://git-scm.com/download/win)
- [WSL2 Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)

## ✅ Checklist de Verificação

- [ ] Docker Desktop instalado e rodando
- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Portas 3000, 8000-8003, 8080 disponíveis
- [ ] Scripts executando sem erro
- [ ] Serviços respondendo corretamente
- [ ] Dados populados com sucesso

## 💡 Dicas Extras

1. **Use Docker Desktop GUI** para monitorar containers
2. **Configure aliases** para comandos frequentes
3. **Use VS Code** com extensões Docker e Python
4. **Mantenha Docker Desktop atualizado**
5. **Configure anti-vírus** para excluir pasta do projeto (performance)

## 🆘 Suporte

Se ainda tiver problemas:
1. Verificar logs: `docker-compose logs -f`
2. Consultar documentação: `docs/CROSS_PLATFORM_COMPATIBILITY.md`
3. Executar diagnóstico: `python scripts/check-dependencies.py`
4. Verificar issues no GitHub do projeto 