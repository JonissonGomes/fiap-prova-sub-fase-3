#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente no Render
"""

import os
import sys
import requests
import json
from typing import Dict, List

class RenderConfig:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_services(self) -> List[Dict]:
        """Obtém lista de serviços"""
        response = requests.get(f"{self.base_url}/services", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_service_env_vars(self, service_id: str, env_vars: Dict[str, str]):
        """Atualiza variáveis de ambiente do serviço"""
        url = f"{self.base_url}/services/{service_id}/env-vars"
        
        # Converte para formato do Render
        env_vars_list = []
        for key, value in env_vars.items():
            env_vars_list.append({
                "key": key,
                "value": value
            })
        
        data = {"envVars": env_vars_list}
        
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

def main():
    """Função principal"""
    
    # Verifica se a API key foi fornecida
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print("❌ RENDER_API_KEY não encontrada nas variáveis de ambiente")
        print("   Exporte a variável: export RENDER_API_KEY=sua_api_key")
        return 1
    
    config = RenderConfig(api_key)
    
    # Configurações de variáveis de ambiente por serviço (usando as variáveis existentes)
    service_configs = {
        "fiap-auth-service": {
            "KEYCLOAK_URL": "http://keycloak:8080",
            "KEYCLOAK_REALM": "vehicle-sales",
            "KEYCLOAK_CLIENT_ID": "vehicle-sales-app",
            "KEYCLOAK_CLIENT_SECRET": "BCzhpesgtiAQENgLRuO2tlsLBdUPPMTv",
            "MONGODB_URL": "mongodb://auth-mongodb:27017",
            "MONGODB_DB_NAME": "auth_db",
            "MONGODB_COLLECTION": "users",
            "REDIS_URL": "redis://redis:6379"
        },
        "fiap-core-service": {
            "MONGODB_URL": "mongodb://core-mongodb:27017",
            "MONGODB_DB_NAME": "core_db",
            "MONGODB_COLLECTION": "vehicles",
            "AUTH_SERVICE_URL": "http://auth-service:8002",
            "REDIS_URL": "redis://redis:6379"
        },
        "fiap-customer-service": {
            "MONGODB_URL": "mongodb://customer-mongodb:27017",
            "MONGODB_DB_NAME": "customer_db",
            "MONGODB_COLLECTION": "customers",
            "AUTH_SERVICE_URL": "http://auth-service:8002",
            "REDIS_URL": "redis://redis:6379"
        },
        "fiap-payment-service": {
            "MONGODB_URL": "mongodb://payment-mongodb:27017",
            "MONGODB_DB_NAME": "payment_db",
            "MONGODB_COLLECTION": "payments",
            "AUTH_SERVICE_URL": "http://auth-service:8002",
            "REDIS_URL": "redis://redis:6379"
        },
        "fiap-sales-service": {
            "MONGODB_URL": "mongodb://sales-mongodb:27017",
            "MONGODB_DB_NAME": "sales_db",
            "MONGODB_COLLECTION": "sales",
            "CORE_SERVICE_URL": "http://core-service:8000",
            "AUTH_SERVICE_URL": "http://auth-service:8002",
            "REDIS_URL": "redis://redis:6379",
            "KEYCLOAK_URL": "http://keycloak:8080",
            "KEYCLOAK_REALM": "vehicle-sales",
            "KEYCLOAK_CLIENT_ID": "vehicle-sales-app"
        },
        "fiap-frontend": {
            "REACT_APP_API_URL": "http://localhost:8000",
            "REACT_APP_CORE_SERVICE_URL": "http://localhost:8000",
            "REACT_APP_SALES_SERVICE_URL": "http://localhost:8001",
            "REACT_APP_AUTH_SERVICE_URL": "http://localhost:8002",
            "REACT_APP_CUSTOMER_SERVICE_URL": "http://localhost:8003",
            "REACT_APP_APP_NAME": "Sistema de Vendas de Veículos",
            "REACT_APP_ENABLE_AUTH": "true",
            "REACT_APP_RETRY_ATTEMPTS": "3",
            "REACT_APP_RETRY_DELAY": "1000",
            "CHOKIDAR_USEPOLLING": "true"
        }
    }
    
    print("🔧 Configurando variáveis de ambiente no Render...")
    
    try:
        # Obtém lista de serviços
        services = config.get_services()
        
        success_count = 0
        total_count = len(service_configs)
        
        for service_name, env_vars in service_configs.items():
            # Encontra o serviço pelo nome
            service = None
            for s in services:
                if s.get("name") == service_name:
                    service = s
                    break
            
            if not service:
                print(f"⚠️  Serviço {service_name} não encontrado")
                continue
            
            service_id = service["id"]
            
            try:
                # Atualiza variáveis de ambiente
                config.update_service_env_vars(service_id, env_vars)
                print(f"✅ {service_name} configurado com sucesso")
                success_count += 1
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro ao configurar {service_name}: {e}")
        
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
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com a API do Render: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 