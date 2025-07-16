#!/usr/bin/env python3
"""
Script para verificar dependências e compatibilidade entre sistemas operacionais
Uso: python3 scripts/check-dependencies.py
"""

import subprocess
import sys
import platform
import os
import json
from pathlib import Path

def check_command(command, args=None):
    """Verifica se um comando está disponível no sistema"""
    try:
        if args is None:
            args = ['--version']
        
        result = subprocess.run(
            [command] + args, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False, None

def check_docker():
    """Verifica se Docker está funcionando"""
    try:
        result = subprocess.run(
            ['docker', 'info'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def check_python_packages():
    """Verifica pacotes Python essenciais"""
    packages = ['requests', 'httpx', 'asyncio']
    results = {}
    
    for package in packages:
        try:
            __import__(package)
            results[package] = True
        except ImportError:
            results[package] = False
    
    return results

def check_ports():
    """Verifica se portas essenciais estão disponíveis"""
    import socket
    
    ports = {
        3000: 'Frontend',
        8000: 'Core Service',
        8001: 'Sales Service', 
        8002: 'Auth Service',
        8003: 'Customer Service',
        8080: 'Keycloak',
        6379: 'Redis',
        27017: 'MongoDB'
    }
    
    results = {}
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            results[port] = f"OCUPADA ({service})"
        else:
            results[port] = "DISPONÍVEL"
    
    return results

def check_scripts():
    """Verifica se scripts críticos existem"""
    scripts_dir = Path('scripts')
    
    bash_scripts = [
        'setup-complete.sh',
        'setup-env.sh',
        'populate-data.sh',
        'test-rate-limiting.sh'
    ]
    
    python_scripts = [
        'populate-data.py',
        'setup-admin-user.py'
    ]
    
    results = {
        'bash': {},
        'python': {}
    }
    
    for script in bash_scripts:
        script_path = scripts_dir / script
        results['bash'][script] = script_path.exists()
    
    for script in python_scripts:
        script_path = scripts_dir / script
        results['python'][script] = script_path.exists()
    
    return results

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(item, status, details=None):
    """Imprime status formatado"""
    if status:
        symbol = "✅"
        status_text = "DISPONÍVEL"
    else:
        symbol = "❌"
        status_text = "NÃO DISPONÍVEL"
    
    print(f"{symbol} {item:<30} {status_text}")
    if details:
        print(f"   └─ {details}")

def main():
    print_header("VERIFICAÇÃO DE COMPATIBILIDADE ENTRE SISTEMAS")
    
    # Informações do sistema
    os_name = platform.system()
    os_version = platform.release()
    python_version = platform.python_version()
    
    print(f"\n🖥️  Sistema Operacional: {os_name} {os_version}")
    print(f"🐍 Python: {python_version}")
    
    # Verificar comandos essenciais
    print_header("COMANDOS ESSENCIAIS")
    
    essential_commands = [
        ('docker', ['--version']),
        ('docker-compose', ['--version']),
        ('git', ['--version']),
        ('python3', ['--version']),
        ('pip3', ['--version'])
    ]
    
    all_essential = True
    for cmd, args in essential_commands:
        available, version = check_command(cmd, args)
        print_status(cmd, available, version)
        if not available:
            all_essential = False
    
    # Verificar comandos opcionais
    print_header("COMANDOS OPCIONAIS")
    
    optional_commands = [
        ('curl', ['--version']),
        ('mongosh', ['--version']),
        ('make', ['--version']),
        ('jq', ['--version'])
    ]
    
    for cmd, args in optional_commands:
        available, version = check_command(cmd, args)
        print_status(cmd, available, version)
    
    # Verificar Docker
    print_header("VERIFICAÇÃO DO DOCKER")
    
    docker_running = check_docker()
    print_status("Docker Engine", docker_running)
    
    # Verificar pacotes Python
    print_header("PACOTES PYTHON")
    
    python_packages = check_python_packages()
    for package, available in python_packages.items():
        print_status(package, available)
    
    # Verificar portas
    print_header("PORTAS DE SERVIÇO")
    
    ports = check_ports()
    for port, status in ports.items():
        is_available = "DISPONÍVEL" in status
        print_status(f"Porta {port}", is_available, status)
    
    # Verificar scripts
    print_header("SCRIPTS DO PROJETO")
    
    scripts = check_scripts()
    
    print("\n📜 Scripts Bash:")
    for script, exists in scripts['bash'].items():
        print_status(script, exists)
    
    print("\n🐍 Scripts Python:")
    for script, exists in scripts['python'].items():
        print_status(script, exists)
    
    # Recomendações por sistema
    print_header("RECOMENDAÇÕES POR SISTEMA")
    
    if os_name == "Windows":
        print("🪟 WINDOWS:")
        print("   1. Instalar Git Bash para scripts .sh")
        print("   2. Usar Docker Desktop")
        print("   3. Considerar WSL2 para desenvolvimento")
        print("   4. Instalar Python 3.8+ via Microsoft Store")
        
    elif os_name == "Darwin":
        print("🍎 MacOS:")
        print("   1. Instalar Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("   2. Instalar Docker Desktop")
        print("   3. brew install curl (se necessário)")
        print("   4. Scripts bash devem funcionar nativamente")
        
    elif os_name == "Linux":
        print("🐧 LINUX:")
        print("   1. Instalar Docker e Docker Compose")
        print("   2. sudo apt-get install curl (Ubuntu/Debian)")
        print("   3. Scripts bash devem funcionar nativamente")
        print("   4. Verificar se user está no grupo docker")
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    if all_essential and docker_running:
        print("✅ SISTEMA PRONTO PARA DESENVOLVIMENTO!")
        print("   Todos os comandos essenciais estão disponíveis.")
    else:
        print("⚠️  SISTEMA PRECISA DE CONFIGURAÇÃO")
        print("   Alguns comandos essenciais não estão disponíveis.")
    
    print(f"\n📖 Para mais informações, consulte:")
    print(f"   - docs/CROSS_PLATFORM_COMPATIBILITY.md")
    print(f"   - README.md")
    
    # Comando de teste rápido
    print_header("TESTE RÁPIDO")
    print("Para testar o sistema rapidamente:")
    print("   make up")
    print("   make populate-data")
    print("   make test")

if __name__ == "__main__":
    main() 