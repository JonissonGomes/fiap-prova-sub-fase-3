#!/usr/bin/env python3
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script simplificado para popular dados básicos nos serviços
Funciona sem autenticação para testar a conectividade
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração
NOMES = ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Pereira"]
MARCAS_VEICULOS = ["Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai"]
MODELOS = ["Corolla", "Golf", "Onix", "Focus", "HB20"]

class SimpleDataPopulator:
    def __init__(self):
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def create_simple_customers(self, count: int = 10):
        """Cria clientes simples"""
        print(f"👥 Criando {count} clientes...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                customer_data = {
                    "name": f"{random.choice(NOMES)} {i+1:03d}",
                    "email": f"customer{i+1:03d}@example.com",
                    "phone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "cpf": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
                    "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz'])} {random.randint(1, 999)}",
                    "city": random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte"]),
                    "state": random.choice(["SP", "RJ", "MG"]),
                    "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.customers.append(response.json())
                        print(f"✅ Cliente criado: {customer_data['name']}")
                    else:
                        print(f"❌ Erro ao criar cliente: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar cliente: {e}")

    async def create_simple_vehicles(self, count: int = 20):
        """Cria veículos simples"""
        print(f"🚗 Criando {count} veículos...")
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(count):
                vehicle_data = {
                    "brand": random.choice(MARCAS_VEICULOS),
                    "model": random.choice(MODELOS),
                    "year": random.randint(2018, 2024),
                    "color": random.choice(["Branco", "Preto", "Prata", "Azul", "Vermelho"]),
                    "price": float(random.randint(30000, 80000)),
                    "mileage": random.randint(0, 50000),
                    "fuel_type": random.choice(["Flex", "Gasolina", "Etanol"]),
                    "transmission": random.choice(["Manual", "Automático"]),
                    "status": "available"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.vehicles.append(response.json())
                        print(f"✅ Veículo criado: {vehicle_data['brand']} {vehicle_data['model']}")
                    else:
                        print(f"❌ Erro ao criar veículo: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar veículo: {e}")

    async def create_simple_sales(self, count: int = 5):
        """Cria vendas simples"""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Não há clientes ou veículos para criar vendas")
            return
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for i in range(min(count, len(self.customers), len(self.vehicles))):
                customer = self.customers[i]
                vehicle = self.vehicles[i]
                
                sale_data = {
                    "customer_id": customer.get("id", f"customer_{i}"),
                    "vehicle_id": vehicle.get("id", f"vehicle_{i}"),
                    "sale_price": float(vehicle.get("price", 50000)) * random.uniform(0.9, 1.1),
                    "sale_date": datetime.now().isoformat(),
                    "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão"]),
                    "status": "completed"
                }
                
                try:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.sales.append(response.json())
                        print(f"✅ Venda criada: {vehicle.get('brand', 'Veículo')} para {customer.get('name', 'Cliente')}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Erro ao criar venda: {e}")

    async def generate_summary(self):
        """Gera resumo dos dados criados"""
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")

async def main():
    """Função principal"""
    print("🚀 Iniciando população simplificada de dados...")
    print("=" * 50)
    
    populator = SimpleDataPopulator()
    
    # Testa conectividade primeiro
    print("🔍 Testando conectividade...")
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
    
    print("\n🎯 Iniciando população de dados...")
    
    # Cria dados
    await populator.create_simple_customers(10)
    await populator.create_simple_vehicles(20)
    await populator.create_simple_sales(5)
    
    # Gera resumo
    await populator.generate_summary()
    
    print("\n✅ População simplificada concluída!")

if __name__ == "__main__":
    asyncio.run(main()) 