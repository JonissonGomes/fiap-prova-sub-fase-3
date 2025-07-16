#!/usr/bin/env python3
"""
Script para adicionar endpoints de health check nos serviços
"""

import os
import sys
from pathlib import Path

def add_health_check_to_service(service_path: str, main_file: str):
    """Adiciona endpoint de health check ao serviço"""
    
    main_file_path = Path(service_path) / main_file
    
    if not main_file_path.exists():
        print(f"⚠️  Arquivo {main_file_path} não encontrado")
        return False
    
    # Lê o conteúdo atual
    with open(main_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se já existe o endpoint de health check
    if '@app.get("/health")' in content or '@app.get("/health/")' in content:
        print(f"✅ Health check já existe em {service_path}")
        return True
    
    # Adiciona o endpoint de health check
    health_check_code = '''
@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do serviço"""
    return {
        "status": "healthy",
        "service": "''' + service_path + '''",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
'''
    
    # Encontra onde adicionar o código (após os imports e antes das rotas)
    lines = content.split('\n')
    
    # Adiciona import do datetime se não existir
    datetime_import = "import datetime"
    if datetime_import not in content:
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                continue
            elif line.strip() == '':
                continue
            else:
                lines.insert(i, datetime_import)
                break
    
    # Adiciona o endpoint de health check
    for i, line in enumerate(lines):
        if '@app.get(' in line or '@app.post(' in line or '@app.put(' in line or '@app.delete(' in line:
            lines.insert(i, health_check_code)
            break
    else:
        # Se não encontrou rotas, adiciona no final
        lines.append(health_check_code)
    
    # Escreve o arquivo atualizado
    with open(main_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Health check adicionado em {service_path}")
    return True

def main():
    """Função principal"""
    
    services = [
        ("auth-service", "app/main.py"),
        ("core-service", "app/adapters/api/main.py"),
        ("customer-service", "app/main.py"),
        ("payment-service", "app/main.py"),
        ("sales-service", "app/main.py"),
    ]
    
    print("🔧 Configurando endpoints de health check...")
    
    success_count = 0
    total_count = len(services)
    
    for service_path, main_file in services:
        if add_health_check_to_service(service_path, main_file):
            success_count += 1
    
    print(f"\n📊 Resumo:")
    print(f"   ✅ Sucessos: {success_count}")
    print(f"   ❌ Falhas: {total_count - success_count}")
    print(f"   📈 Taxa de sucesso: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 Todos os serviços foram configurados com sucesso!")
        return 0
    else:
        print("\n⚠️  Alguns serviços não puderam ser configurados.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 