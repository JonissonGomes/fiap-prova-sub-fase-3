#!/usr/bin/env python3
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script de teste simples para verificar conectividade dos serviços
"""

import asyncio
import httpx
import json

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

async def test_service_connectivity():
    """Testa conectividade com todos os serviços"""
    print("🔍 Testando conectividade com serviços...")
    
    async with httpx.AsyncClient() as client:
        for service_name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name.upper()} Service: {e}")

async def test_core_service_endpoints():
    """Testa endpoints do core service sem autenticação"""
    print("\n🚗 Testando endpoints do Core Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de veículos
            response = await client.get(f"{SERVICES['core']}/vehicles", timeout=5)
            print(f"GET /vehicles: {response.status_code}")
            
            if response.status_code == 200:
                vehicles = response.json()
                print(f"Veículos encontrados: {len(vehicles)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar core service: {e}")

async def test_customer_service_endpoints():
    """Testa endpoints do customer service sem autenticação"""
    print("\n👥 Testando endpoints do Customer Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de clientes
            response = await client.get(f"{SERVICES['customer']}/customers", timeout=5)
            print(f"GET /customers: {response.status_code}")
            
            if response.status_code == 200:
                customers = response.json()
                print(f"Clientes encontrados: {len(customers)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar customer service: {e}")

async def test_sales_service_endpoints():
    """Testa endpoints do sales service sem autenticação"""
    print("\n💰 Testando endpoints do Sales Service...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Testa listagem de vendas
            response = await client.get(f"{SERVICES['sales']}/sales", timeout=5)
            print(f"GET /sales: {response.status_code}")
            
            if response.status_code == 200:
                sales = response.json()
                print(f"Vendas encontradas: {len(sales)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar sales service: {e}")

async def main():
    """Função principal"""
    print("🧪 Teste simples de conectividade dos serviços")
    print("=" * 50)
    
    await test_service_connectivity()
    await test_core_service_endpoints()
    await test_customer_service_endpoints()
    await test_sales_service_endpoints()
    
    print("\n✅ Teste de conectividade concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 