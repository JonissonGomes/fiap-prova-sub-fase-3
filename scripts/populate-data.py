#!/usr/bin/env python3
"""
Script para popular dados similares a dados reais nos serviços.
Cria usuários, clientes, veículos e vendas com dados realistas.
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração de dados similares a reais
NOMES_MASCULINOS = [
    "João", "Carlos", "José", "Antonio", "Francisco", "Paulo", "Pedro", "Lucas", "Matheus", "Gabriel",
    "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe", "Rodrigo", "Gustavo", "Leonardo", "Thiago"
]

NOMES_FEMININOS = [
    "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", "Fernanda", "Patricia", "Aline",
    "Luciana", "Valeria", "Luana", "Mariana", "Leticia", "Camila", "Amanda", "Bruna", "Carla", "Daniela"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
]

MARCAS_VEICULOS = [
    "Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai", "Fiat", "Honda", "Nissan", "Renault", "Peugeot"
]

MODELOS_POR_MARCA = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Hilux", "Prius", "Yaris"],
    "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Polo", "Gol"],
    "Chevrolet": ["Onix", "Cruze", "Tracker", "S10", "Spin", "Cobalt"],
    "Ford": ["Focus", "Fiesta", "EcoSport", "Ranger", "Ka", "Edge"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Elantra", "i30", "Santa Fe"],
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi"],
    "Honda": ["Civic", "Fit", "HR-V", "City", "Accord", "CR-V"],
    "Nissan": ["March", "Versa", "Kicks", "Sentra", "X-Trail", "Frontier"],
    "Renault": ["Sandero", "Logan", "Duster", "Captur", "Kwid", "Oroch"],
    "Peugeot": ["208", "2008", "3008", "5008", "Partner", "Expert"]
}

CORES = ["Branco", "Preto", "Prata", "Azul", "Vermelho", "Cinza", "Bege", "Verde", "Amarelo", "Dourado"]

CIDADES_ESTADOS = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Salvador", "BA"),
    ("Brasília", "DF"), ("Fortaleza", "CE"), ("Curitiba", "PR"), ("Recife", "PE"),
    ("Porto Alegre", "RS"), ("Manaus", "AM"), ("Belém", "PA"), ("Goiânia", "GO"),
    ("Guarulhos", "SP"), ("Campinas", "SP"), ("Nova Iguaçu", "RJ"), ("Maceió", "AL")
]

class DataPopulator:
    def __init__(self):
        self.admin_token = None
        self.users = []
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def setup_admin_user(self):
        """Configura usuário admin e obtém token de autenticação."""
        print("🔐 Configurando usuário admin...")
        
        # Dados do admin padrão
        admin_data = {
            "email": "admin@vehiclesales.com",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Tenta fazer login primeiro
                login_response = await client.post(
                    f"{SERVICES['auth']}/auth/login",
                    json={"email": admin_data["email"], "password": admin_data["password"]}
                )
                
                if login_response.status_code == 200:
                    self.admin_token = login_response.json()["access_token"]
                    print("✅ Admin logado com sucesso!")
                else:
                    print("❌ Falha ao fazer login do admin")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao configurar admin: {e}")
            return False
        
        return True

    def generate_cpf(self) -> str:
        """Gera um CPF válido."""
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)
        
        # Gera os primeiros 9 dígitos
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula o primeiro dígito verificador
        weights1 = list(range(10, 1, -1))
        digit1 = calculate_digit(cpf, weights1)
        cpf.append(int(digit1))
        
        # Calcula o segundo dígito verificador
        weights2 = list(range(11, 1, -1))
        digit2 = calculate_digit(cpf, weights2)
        cpf.append(int(digit2))
        
        return ''.join(map(str, cpf))

    def generate_phone(self) -> str:
        """Gera um número de telefone válido."""
        ddd = random.choice([11, 21, 31, 41, 51, 61, 71, 81, 85, 47])
        number = f"9{random.randint(10000000, 99999999)}"
        return f"{ddd}{number}"

    def generate_email(self, name: str) -> str:
        """Gera um email baseado no nome."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "uol.com.br"]
        clean_name = name.lower().replace(" ", ".")
        domain = random.choice(domains)
        number = random.randint(1, 999)
        return f"{clean_name}{number}@{domain}"

    async def create_users(self, count: int = 20):
        """Cria usuários no sistema de autenticação."""
        print(f"👥 Criando {count} usuários...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do usuário
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            
            user_data = {
                "email": self.generate_email(full_name),
                "password": "password123",
                "name": full_name,  # Corrigido: usar "name" em vez de "full_name"
                "role": random.choice(["CUSTOMER", "SALES", "ADMIN"]),
                "status": "ACTIVE"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['auth']}/auth/register",
                        json=user_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        user = response.json()
                        self.users.append(user)
                        print(f"✅ Usuário criado: {user_data['email']} ({user_data['role']})")
                    else:
                        print(f"❌ Erro ao criar usuário {user_data['email']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar usuário {user_data['email']}: {e}")
        
        print(f"✅ {len(self.users)} usuários criados com sucesso!")

    async def create_customers(self, count: int = 50):
        """Cria clientes no sistema."""
        print(f"🏢 Criando {count} clientes...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do cliente
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            city, state = random.choice(CIDADES_ESTADOS)
            
            customer_data = {
                "name": full_name,
                "email": self.generate_email(full_name),
                "phone": self.generate_phone(),
                "cpf": self.generate_cpf(),
                "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz', 'Principal', 'Central'])}, {random.randint(1, 999)}",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        customer = response.json()
                        self.customers.append(customer)
                        print(f"✅ Cliente criado: {customer_data['name']} - {customer_data['cpf']}")
                    else:
                        print(f"❌ Erro ao criar cliente {customer_data['name']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar cliente {customer_data['name']}: {e}")
        
        print(f"✅ {len(self.customers)} clientes criados com sucesso!")

    async def create_vehicles(self, count: int = 100):
        """Cria veículos no sistema."""
        print(f"🚗 Criando {count} veículos...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do veículo
            brand = random.choice(MARCAS_VEICULOS)
            model = random.choice(MODELOS_POR_MARCA[brand])
            year = random.randint(2015, 2024)
            mileage = random.randint(0, 150000)
            
            # Preço baseado no ano e quilometragem
            base_price = random.randint(25000, 120000)
            age_factor = (2024 - year) * 0.1
            mileage_factor = mileage / 100000 * 0.2
            price = max(1000, int(base_price * (1 - age_factor - mileage_factor)))
            
            vehicle_data = {
                "brand": brand,
                "model": model,
                "year": year,
                "color": random.choice(CORES),
                "price": price,
                "mileage": mileage,
                "fuel_type": random.choice(["Flex", "Gasolina", "Etanol", "Diesel"]),
                "transmission": random.choice(["Manual", "Automático", "CVT"]),
                "description": f"{brand} {model} {year} em excelente estado de conservação.",
                "available": random.choice([True, True, True, False])  # 75% disponíveis
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        vehicle = response.json()
                        self.vehicles.append(vehicle)
                        print(f"✅ Veículo criado: {brand} {model} {year} - R$ {price:,}")
                    else:
                        print(f"❌ Erro ao criar veículo {brand} {model}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar veículo {brand} {model}: {e}")
        
        print(f"✅ {len(self.vehicles)} veículos criados com sucesso!")

    async def create_sales(self, count: int = 30):
        """Cria vendas no sistema."""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Necessário ter clientes e veículos para criar vendas")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Filtra apenas veículos disponíveis
        available_vehicles = [v for v in self.vehicles if v.get("available", True)]
        
        for i in range(min(count, len(available_vehicles))):
            # Seleciona cliente e veículo aleatórios
            customer = random.choice(self.customers)
            vehicle = available_vehicles[i]
            
            # Gera data de venda nos últimos 6 meses
            sale_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            sale_data = {
                "customer_cpf": customer["cpf"],
                "vehicle_id": vehicle["id"],
                "sale_date": sale_date.isoformat(),
                "sale_price": vehicle["price"] * random.uniform(0.9, 1.1),  # Variação de ±10%
                "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão", "PIX"]),
                "notes": f"Venda do veículo {vehicle['brand']} {vehicle['model']} para {customer['name']}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        sale = response.json()
                        self.sales.append(sale)
                        print(f"✅ Venda criada: {vehicle['brand']} {vehicle['model']} para {customer['name']}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar venda: {e}")
        
        print(f"✅ {len(self.sales)} vendas criadas com sucesso!")

    async def generate_summary(self):
        """Gera resumo dos dados criados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("="*60)
        print(f"👥 Usuários: {len(self.users)}")
        print(f"🏢 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")
        print("="*60)
        
        # Estatísticas por role
        if self.users:
            roles = {}
            for user in self.users:
                role = user.get("role", "UNKNOWN")
                roles[role] = roles.get(role, 0) + 1
            
            print("👥 Usuários por role:")
            for role, count in roles.items():
                print(f"   {role}: {count}")
        
        # Estatísticas de veículos
        if self.vehicles:
            available = sum(1 for v in self.vehicles if v.get("available", True))
            sold = len(self.vehicles) - available
            print(f"🚗 Veículos disponíveis: {available}")
            print(f"🚗 Veículos vendidos: {sold}")
        
        # Valor total das vendas
        if self.sales:
            total_sales = sum(sale.get("sale_price", 0) for sale in self.sales)
            print(f"💰 Valor total das vendas: R$ {total_sales:,.2f}")
        
        print("="*60)
        print("✅ População de dados concluída com sucesso!")

async def main():
    """Função principal."""
    print("🚀 Iniciando população de dados...")
    
    populator = DataPopulator()
    
    # Verifica se os serviços estão rodando
    print("🔍 Verificando serviços...")
    for service_name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name.upper()} Service: {e}")
            return
    
    # Configura admin
    if not await populator.setup_admin_user():
        print("❌ Falha ao configurar admin. Verifique se o auth-service está funcionando.")
        return
    
    # Popula dados
    await populator.create_users(20)
    await populator.create_customers(50)
    await populator.create_vehicles(100)
    await populator.create_sales(30)
    
    # Gera resumo
    await populator.generate_summary()

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script para popular dados similares a dados reais nos serviços.
Cria usuários, clientes, veículos e vendas com dados realistas.
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração de dados similares a reais
NOMES_MASCULINOS = [
    "João", "Carlos", "José", "Antonio", "Francisco", "Paulo", "Pedro", "Lucas", "Matheus", "Gabriel",
    "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe", "Rodrigo", "Gustavo", "Leonardo", "Thiago"
]

NOMES_FEMININOS = [
    "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", "Fernanda", "Patricia", "Aline",
    "Luciana", "Valeria", "Luana", "Mariana", "Leticia", "Camila", "Amanda", "Bruna", "Carla", "Daniela"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
]

MARCAS_VEICULOS = [
    "Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai", "Fiat", "Honda", "Nissan", "Renault", "Peugeot"
]

MODELOS_POR_MARCA = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Hilux", "Prius", "Yaris"],
    "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Polo", "Gol"],
    "Chevrolet": ["Onix", "Cruze", "Tracker", "S10", "Spin", "Cobalt"],
    "Ford": ["Focus", "Fiesta", "EcoSport", "Ranger", "Ka", "Edge"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Elantra", "i30", "Santa Fe"],
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi"],
    "Honda": ["Civic", "Fit", "HR-V", "City", "Accord", "CR-V"],
    "Nissan": ["March", "Versa", "Kicks", "Sentra", "X-Trail", "Frontier"],
    "Renault": ["Sandero", "Logan", "Duster", "Captur", "Kwid", "Oroch"],
    "Peugeot": ["208", "2008", "3008", "5008", "Partner", "Expert"]
}

CORES = ["Branco", "Preto", "Prata", "Azul", "Vermelho", "Cinza", "Bege", "Verde", "Amarelo", "Dourado"]

CIDADES_ESTADOS = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Salvador", "BA"),
    ("Brasília", "DF"), ("Fortaleza", "CE"), ("Curitiba", "PR"), ("Recife", "PE"),
    ("Porto Alegre", "RS"), ("Manaus", "AM"), ("Belém", "PA"), ("Goiânia", "GO"),
    ("Guarulhos", "SP"), ("Campinas", "SP"), ("Nova Iguaçu", "RJ"), ("Maceió", "AL")
]

class DataPopulator:
    def __init__(self):
        self.admin_token = None
        self.users = []
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def setup_admin_user(self):
        """Configura usuário admin e obtém token de autenticação."""
        print("🔐 Configurando usuário admin...")
        
        # Dados do admin padrão
        admin_data = {
            "email": "admin@vehiclesales.com",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Tenta fazer login primeiro
                login_response = await client.post(
                    f"{SERVICES['auth']}/auth/login",
                    json={"email": admin_data["email"], "password": admin_data["password"]}
                )
                
                if login_response.status_code == 200:
                    self.admin_token = login_response.json()["access_token"]
                    print("✅ Admin logado com sucesso!")
                else:
                    print("❌ Falha ao fazer login do admin")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao configurar admin: {e}")
            return False
        
        return True

    def generate_cpf(self) -> str:
        """Gera um CPF válido."""
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)
        
        # Gera os primeiros 9 dígitos
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula o primeiro dígito verificador
        weights1 = list(range(10, 1, -1))
        digit1 = calculate_digit(cpf, weights1)
        cpf.append(int(digit1))
        
        # Calcula o segundo dígito verificador
        weights2 = list(range(11, 1, -1))
        digit2 = calculate_digit(cpf, weights2)
        cpf.append(int(digit2))
        
        return ''.join(map(str, cpf))

    def generate_phone(self) -> str:
        """Gera um número de telefone válido."""
        ddd = random.choice([11, 21, 31, 41, 51, 61, 71, 81, 85, 47])
        number = f"9{random.randint(10000000, 99999999)}"
        return f"{ddd}{number}"

    def generate_email(self, name: str) -> str:
        """Gera um email baseado no nome."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "uol.com.br"]
        clean_name = name.lower().replace(" ", ".")
        domain = random.choice(domains)
        number = random.randint(1, 999)
        return f"{clean_name}{number}@{domain}"

    async def create_users(self, count: int = 20):
        """Cria usuários no sistema de autenticação."""
        print(f"👥 Criando {count} usuários...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do usuário
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            
            user_data = {
                "email": self.generate_email(full_name),
                "password": "password123",
                "name": full_name,  # Corrigido: usar "name" em vez de "full_name"
                "role": random.choice(["CUSTOMER", "SALES", "ADMIN"]),
                "status": "ACTIVE"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['auth']}/auth/register",
                        json=user_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        user = response.json()
                        self.users.append(user)
                        print(f"✅ Usuário criado: {user_data['email']} ({user_data['role']})")
                    else:
                        print(f"❌ Erro ao criar usuário {user_data['email']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar usuário {user_data['email']}: {e}")
        
        print(f"✅ {len(self.users)} usuários criados com sucesso!")

    async def create_customers(self, count: int = 50):
        """Cria clientes no sistema."""
        print(f"🏢 Criando {count} clientes...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do cliente
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            city, state = random.choice(CIDADES_ESTADOS)
            
            customer_data = {
                "name": full_name,
                "email": self.generate_email(full_name),
                "phone": self.generate_phone(),
                "cpf": self.generate_cpf(),
                "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz', 'Principal', 'Central'])}, {random.randint(1, 999)}",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        customer = response.json()
                        self.customers.append(customer)
                        print(f"✅ Cliente criado: {customer_data['name']} - {customer_data['cpf']}")
                    else:
                        print(f"❌ Erro ao criar cliente {customer_data['name']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar cliente {customer_data['name']}: {e}")
        
        print(f"✅ {len(self.customers)} clientes criados com sucesso!")

    async def create_vehicles(self, count: int = 100):
        """Cria veículos no sistema."""
        print(f"🚗 Criando {count} veículos...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do veículo
            brand = random.choice(MARCAS_VEICULOS)
            model = random.choice(MODELOS_POR_MARCA[brand])
            year = random.randint(2015, 2024)
            mileage = random.randint(0, 150000)
            
            # Preço baseado no ano e quilometragem
            base_price = random.randint(25000, 120000)
            age_factor = (2024 - year) * 0.1
            mileage_factor = mileage / 100000 * 0.2
            price = max(1000, int(base_price * (1 - age_factor - mileage_factor)))
            
            vehicle_data = {
                "brand": brand,
                "model": model,
                "year": year,
                "color": random.choice(CORES),
                "price": price,
                "mileage": mileage,
                "fuel_type": random.choice(["Flex", "Gasolina", "Etanol", "Diesel"]),
                "transmission": random.choice(["Manual", "Automático", "CVT"]),
                "description": f"{brand} {model} {year} em excelente estado de conservação.",
                "available": random.choice([True, True, True, False])  # 75% disponíveis
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        vehicle = response.json()
                        self.vehicles.append(vehicle)
                        print(f"✅ Veículo criado: {brand} {model} {year} - R$ {price:,}")
                    else:
                        print(f"❌ Erro ao criar veículo {brand} {model}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar veículo {brand} {model}: {e}")
        
        print(f"✅ {len(self.vehicles)} veículos criados com sucesso!")

    async def create_sales(self, count: int = 30):
        """Cria vendas no sistema."""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Necessário ter clientes e veículos para criar vendas")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Filtra apenas veículos disponíveis
        available_vehicles = [v for v in self.vehicles if v.get("available", True)]
        
        for i in range(min(count, len(available_vehicles))):
            # Seleciona cliente e veículo aleatórios
            customer = random.choice(self.customers)
            vehicle = available_vehicles[i]
            
            # Gera data de venda nos últimos 6 meses
            sale_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            sale_data = {
                "customer_cpf": customer["cpf"],
                "vehicle_id": vehicle["id"],
                "sale_date": sale_date.isoformat(),
                "sale_price": vehicle["price"] * random.uniform(0.9, 1.1),  # Variação de ±10%
                "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão", "PIX"]),
                "notes": f"Venda do veículo {vehicle['brand']} {vehicle['model']} para {customer['name']}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        sale = response.json()
                        self.sales.append(sale)
                        print(f"✅ Venda criada: {vehicle['brand']} {vehicle['model']} para {customer['name']}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar venda: {e}")
        
        print(f"✅ {len(self.sales)} vendas criadas com sucesso!")

    async def generate_summary(self):
        """Gera resumo dos dados criados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("="*60)
        print(f"👥 Usuários: {len(self.users)}")
        print(f"🏢 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")
        print("="*60)
        
        # Estatísticas por role
        if self.users:
            roles = {}
            for user in self.users:
                role = user.get("role", "UNKNOWN")
                roles[role] = roles.get(role, 0) + 1
            
            print("👥 Usuários por role:")
            for role, count in roles.items():
                print(f"   {role}: {count}")
        
        # Estatísticas de veículos
        if self.vehicles:
            available = sum(1 for v in self.vehicles if v.get("available", True))
            sold = len(self.vehicles) - available
            print(f"🚗 Veículos disponíveis: {available}")
            print(f"🚗 Veículos vendidos: {sold}")
        
        # Valor total das vendas
        if self.sales:
            total_sales = sum(sale.get("sale_price", 0) for sale in self.sales)
            print(f"💰 Valor total das vendas: R$ {total_sales:,.2f}")
        
        print("="*60)
        print("✅ População de dados concluída com sucesso!")

async def main():
    """Função principal."""
    print("🚀 Iniciando população de dados...")
    
    populator = DataPopulator()
    
    # Verifica se os serviços estão rodando
    print("🔍 Verificando serviços...")
    for service_name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name.upper()} Service: {e}")
            return
    
    # Configura admin
    if not await populator.setup_admin_user():
        print("❌ Falha ao configurar admin. Verifique se o auth-service está funcionando.")
        return
    
    # Popula dados
    await populator.create_users(20)
    await populator.create_customers(50)
    await populator.create_vehicles(100)
    await populator.create_sales(30)
    
    # Gera resumo
    await populator.generate_summary()

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script para popular dados similares a dados reais nos serviços.
Cria usuários, clientes, veículos e vendas com dados realistas.
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração de dados similares a reais
NOMES_MASCULINOS = [
    "João", "Carlos", "José", "Antonio", "Francisco", "Paulo", "Pedro", "Lucas", "Matheus", "Gabriel",
    "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe", "Rodrigo", "Gustavo", "Leonardo", "Thiago"
]

NOMES_FEMININOS = [
    "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", "Fernanda", "Patricia", "Aline",
    "Luciana", "Valeria", "Luana", "Mariana", "Leticia", "Camila", "Amanda", "Bruna", "Carla", "Daniela"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
]

MARCAS_VEICULOS = [
    "Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai", "Fiat", "Honda", "Nissan", "Renault", "Peugeot"
]

MODELOS_POR_MARCA = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Hilux", "Prius", "Yaris"],
    "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Polo", "Gol"],
    "Chevrolet": ["Onix", "Cruze", "Tracker", "S10", "Spin", "Cobalt"],
    "Ford": ["Focus", "Fiesta", "EcoSport", "Ranger", "Ka", "Edge"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Elantra", "i30", "Santa Fe"],
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi"],
    "Honda": ["Civic", "Fit", "HR-V", "City", "Accord", "CR-V"],
    "Nissan": ["March", "Versa", "Kicks", "Sentra", "X-Trail", "Frontier"],
    "Renault": ["Sandero", "Logan", "Duster", "Captur", "Kwid", "Oroch"],
    "Peugeot": ["208", "2008", "3008", "5008", "Partner", "Expert"]
}

CORES = ["Branco", "Preto", "Prata", "Azul", "Vermelho", "Cinza", "Bege", "Verde", "Amarelo", "Dourado"]

CIDADES_ESTADOS = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Salvador", "BA"),
    ("Brasília", "DF"), ("Fortaleza", "CE"), ("Curitiba", "PR"), ("Recife", "PE"),
    ("Porto Alegre", "RS"), ("Manaus", "AM"), ("Belém", "PA"), ("Goiânia", "GO"),
    ("Guarulhos", "SP"), ("Campinas", "SP"), ("Nova Iguaçu", "RJ"), ("Maceió", "AL")
]

class DataPopulator:
    def __init__(self):
        self.admin_token = None
        self.users = []
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def setup_admin_user(self):
        """Configura usuário admin e obtém token de autenticação."""
        print("🔐 Configurando usuário admin...")
        
        # Dados do admin padrão
        admin_data = {
            "email": "admin@vehiclesales.com",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Tenta fazer login primeiro
                login_response = await client.post(
                    f"{SERVICES['auth']}/auth/login",
                    json={"email": admin_data["email"], "password": admin_data["password"]}
                )
                
                if login_response.status_code == 200:
                    self.admin_token = login_response.json()["access_token"]
                    print("✅ Admin logado com sucesso!")
                else:
                    print("❌ Falha ao fazer login do admin")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao configurar admin: {e}")
            return False
        
        return True

    def generate_cpf(self) -> str:
        """Gera um CPF válido."""
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)
        
        # Gera os primeiros 9 dígitos
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula o primeiro dígito verificador
        weights1 = list(range(10, 1, -1))
        digit1 = calculate_digit(cpf, weights1)
        cpf.append(int(digit1))
        
        # Calcula o segundo dígito verificador
        weights2 = list(range(11, 1, -1))
        digit2 = calculate_digit(cpf, weights2)
        cpf.append(int(digit2))
        
        return ''.join(map(str, cpf))

    def generate_phone(self) -> str:
        """Gera um número de telefone válido."""
        ddd = random.choice([11, 21, 31, 41, 51, 61, 71, 81, 85, 47])
        number = f"9{random.randint(10000000, 99999999)}"
        return f"{ddd}{number}"

    def generate_email(self, name: str) -> str:
        """Gera um email baseado no nome."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "uol.com.br"]
        clean_name = name.lower().replace(" ", ".")
        domain = random.choice(domains)
        number = random.randint(1, 999)
        return f"{clean_name}{number}@{domain}"

    async def create_users(self, count: int = 20):
        """Cria usuários no sistema de autenticação."""
        print(f"👥 Criando {count} usuários...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do usuário
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            
            user_data = {
                "email": self.generate_email(full_name),
                "password": "password123",
                "name": full_name,  # Corrigido: usar "name" em vez de "full_name"
                "role": random.choice(["CUSTOMER", "SALES", "ADMIN"]),
                "status": "ACTIVE"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['auth']}/auth/register",
                        json=user_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        user = response.json()
                        self.users.append(user)
                        print(f"✅ Usuário criado: {user_data['email']} ({user_data['role']})")
                    else:
                        print(f"❌ Erro ao criar usuário {user_data['email']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar usuário {user_data['email']}: {e}")
        
        print(f"✅ {len(self.users)} usuários criados com sucesso!")

    async def create_customers(self, count: int = 50):
        """Cria clientes no sistema."""
        print(f"🏢 Criando {count} clientes...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do cliente
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            city, state = random.choice(CIDADES_ESTADOS)
            
            customer_data = {
                "name": full_name,
                "email": self.generate_email(full_name),
                "phone": self.generate_phone(),
                "cpf": self.generate_cpf(),
                "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz', 'Principal', 'Central'])}, {random.randint(1, 999)}",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        customer = response.json()
                        self.customers.append(customer)
                        print(f"✅ Cliente criado: {customer_data['name']} - {customer_data['cpf']}")
                    else:
                        print(f"❌ Erro ao criar cliente {customer_data['name']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar cliente {customer_data['name']}: {e}")
        
        print(f"✅ {len(self.customers)} clientes criados com sucesso!")

    async def create_vehicles(self, count: int = 100):
        """Cria veículos no sistema."""
        print(f"🚗 Criando {count} veículos...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do veículo
            brand = random.choice(MARCAS_VEICULOS)
            model = random.choice(MODELOS_POR_MARCA[brand])
            year = random.randint(2015, 2024)
            mileage = random.randint(0, 150000)
            
            # Preço baseado no ano e quilometragem
            base_price = random.randint(25000, 120000)
            age_factor = (2024 - year) * 0.1
            mileage_factor = mileage / 100000 * 0.2
            price = max(1000, int(base_price * (1 - age_factor - mileage_factor)))
            
            vehicle_data = {
                "brand": brand,
                "model": model,
                "year": year,
                "color": random.choice(CORES),
                "price": price,
                "mileage": mileage,
                "fuel_type": random.choice(["Flex", "Gasolina", "Etanol", "Diesel"]),
                "transmission": random.choice(["Manual", "Automático", "CVT"]),
                "description": f"{brand} {model} {year} em excelente estado de conservação.",
                "available": random.choice([True, True, True, False])  # 75% disponíveis
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        vehicle = response.json()
                        self.vehicles.append(vehicle)
                        print(f"✅ Veículo criado: {brand} {model} {year} - R$ {price:,}")
                    else:
                        print(f"❌ Erro ao criar veículo {brand} {model}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar veículo {brand} {model}: {e}")
        
        print(f"✅ {len(self.vehicles)} veículos criados com sucesso!")

    async def create_sales(self, count: int = 30):
        """Cria vendas no sistema."""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Necessário ter clientes e veículos para criar vendas")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Filtra apenas veículos disponíveis
        available_vehicles = [v for v in self.vehicles if v.get("available", True)]
        
        for i in range(min(count, len(available_vehicles))):
            # Seleciona cliente e veículo aleatórios
            customer = random.choice(self.customers)
            vehicle = available_vehicles[i]
            
            # Gera data de venda nos últimos 6 meses
            sale_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            sale_data = {
                "customer_cpf": customer["cpf"],
                "vehicle_id": vehicle["id"],
                "sale_date": sale_date.isoformat(),
                "sale_price": vehicle["price"] * random.uniform(0.9, 1.1),  # Variação de ±10%
                "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão", "PIX"]),
                "notes": f"Venda do veículo {vehicle['brand']} {vehicle['model']} para {customer['name']}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        sale = response.json()
                        self.sales.append(sale)
                        print(f"✅ Venda criada: {vehicle['brand']} {vehicle['model']} para {customer['name']}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar venda: {e}")
        
        print(f"✅ {len(self.sales)} vendas criadas com sucesso!")

    async def generate_summary(self):
        """Gera resumo dos dados criados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("="*60)
        print(f"👥 Usuários: {len(self.users)}")
        print(f"🏢 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")
        print("="*60)
        
        # Estatísticas por role
        if self.users:
            roles = {}
            for user in self.users:
                role = user.get("role", "UNKNOWN")
                roles[role] = roles.get(role, 0) + 1
            
            print("👥 Usuários por role:")
            for role, count in roles.items():
                print(f"   {role}: {count}")
        
        # Estatísticas de veículos
        if self.vehicles:
            available = sum(1 for v in self.vehicles if v.get("available", True))
            sold = len(self.vehicles) - available
            print(f"🚗 Veículos disponíveis: {available}")
            print(f"🚗 Veículos vendidos: {sold}")
        
        # Valor total das vendas
        if self.sales:
            total_sales = sum(sale.get("sale_price", 0) for sale in self.sales)
            print(f"💰 Valor total das vendas: R$ {total_sales:,.2f}")
        
        print("="*60)
        print("✅ População de dados concluída com sucesso!")

async def main():
    """Função principal."""
    print("🚀 Iniciando população de dados...")
    
    populator = DataPopulator()
    
    # Verifica se os serviços estão rodando
    print("🔍 Verificando serviços...")
    for service_name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name.upper()} Service: {e}")
            return
    
    # Configura admin
    if not await populator.setup_admin_user():
        print("❌ Falha ao configurar admin. Verifique se o auth-service está funcionando.")
        return
    
    # Popula dados
    await populator.create_users(20)
    await populator.create_customers(50)
    await populator.create_vehicles(100)
    await populator.create_sales(30)
    
    # Gera resumo
    await populator.generate_summary()

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Script para popular dados similares a dados reais nos serviços.
Cria usuários, clientes, veículos e vendas com dados realistas.
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Configurações dos serviços
SERVICES = {
    "auth": "http://auth-service:8002",
    "core": "http://core-service:8000", 
    "sales": "http://sales-service:8001",
    "customer": "http://customer-service:8003"
}

# Dados para geração de dados similares a reais
NOMES_MASCULINOS = [
    "João", "Carlos", "José", "Antonio", "Francisco", "Paulo", "Pedro", "Lucas", "Matheus", "Gabriel",
    "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe", "Rodrigo", "Gustavo", "Leonardo", "Thiago"
]

NOMES_FEMININOS = [
    "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", "Fernanda", "Patricia", "Aline",
    "Luciana", "Valeria", "Luana", "Mariana", "Leticia", "Camila", "Amanda", "Bruna", "Carla", "Daniela"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
]

MARCAS_VEICULOS = [
    "Toyota", "Volkswagen", "Chevrolet", "Ford", "Hyundai", "Fiat", "Honda", "Nissan", "Renault", "Peugeot"
]

MODELOS_POR_MARCA = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Hilux", "Prius", "Yaris"],
    "Volkswagen": ["Golf", "Jetta", "Passat", "Tiguan", "Polo", "Gol"],
    "Chevrolet": ["Onix", "Cruze", "Tracker", "S10", "Spin", "Cobalt"],
    "Ford": ["Focus", "Fiesta", "EcoSport", "Ranger", "Ka", "Edge"],
    "Hyundai": ["HB20", "Creta", "Tucson", "Elantra", "i30", "Santa Fe"],
    "Fiat": ["Uno", "Palio", "Strada", "Toro", "Argo", "Mobi"],
    "Honda": ["Civic", "Fit", "HR-V", "City", "Accord", "CR-V"],
    "Nissan": ["March", "Versa", "Kicks", "Sentra", "X-Trail", "Frontier"],
    "Renault": ["Sandero", "Logan", "Duster", "Captur", "Kwid", "Oroch"],
    "Peugeot": ["208", "2008", "3008", "5008", "Partner", "Expert"]
}

CORES = ["Branco", "Preto", "Prata", "Azul", "Vermelho", "Cinza", "Bege", "Verde", "Amarelo", "Dourado"]

CIDADES_ESTADOS = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Salvador", "BA"),
    ("Brasília", "DF"), ("Fortaleza", "CE"), ("Curitiba", "PR"), ("Recife", "PE"),
    ("Porto Alegre", "RS"), ("Manaus", "AM"), ("Belém", "PA"), ("Goiânia", "GO"),
    ("Guarulhos", "SP"), ("Campinas", "SP"), ("Nova Iguaçu", "RJ"), ("Maceió", "AL")
]

class DataPopulator:
    def __init__(self):
        self.admin_token = None
        self.users = []
        self.customers = []
        self.vehicles = []
        self.sales = []

    async def setup_admin_user(self):
        """Configura usuário admin e obtém token de autenticação."""
        print("🔐 Configurando usuário admin...")
        
        # Dados do admin padrão
        admin_data = {
            "email": "admin@vehiclesales.com",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Tenta fazer login primeiro
                login_response = await client.post(
                    f"{SERVICES['auth']}/auth/login",
                    json={"email": admin_data["email"], "password": admin_data["password"]}
                )
                
                if login_response.status_code == 200:
                    self.admin_token = login_response.json()["access_token"]
                    print("✅ Admin logado com sucesso!")
                else:
                    print("❌ Falha ao fazer login do admin")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro ao configurar admin: {e}")
            return False
        
        return True

    def generate_cpf(self) -> str:
        """Gera um CPF válido."""
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)
        
        # Gera os primeiros 9 dígitos
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula o primeiro dígito verificador
        weights1 = list(range(10, 1, -1))
        digit1 = calculate_digit(cpf, weights1)
        cpf.append(int(digit1))
        
        # Calcula o segundo dígito verificador
        weights2 = list(range(11, 1, -1))
        digit2 = calculate_digit(cpf, weights2)
        cpf.append(int(digit2))
        
        return ''.join(map(str, cpf))

    def generate_phone(self) -> str:
        """Gera um número de telefone válido."""
        ddd = random.choice([11, 21, 31, 41, 51, 61, 71, 81, 85, 47])
        number = f"9{random.randint(10000000, 99999999)}"
        return f"{ddd}{number}"

    def generate_email(self, name: str) -> str:
        """Gera um email baseado no nome."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "uol.com.br"]
        clean_name = name.lower().replace(" ", ".")
        domain = random.choice(domains)
        number = random.randint(1, 999)
        return f"{clean_name}{number}@{domain}"

    async def create_users(self, count: int = 20):
        """Cria usuários no sistema de autenticação."""
        print(f"👥 Criando {count} usuários...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do usuário
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            
            user_data = {
                "email": self.generate_email(full_name),
                "password": "password123",
                "name": full_name,  # Corrigido: usar "name" em vez de "full_name"
                "role": random.choice(["CUSTOMER", "SALES", "ADMIN"]),
                "status": "ACTIVE"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['auth']}/auth/register",
                        json=user_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        user = response.json()
                        self.users.append(user)
                        print(f"✅ Usuário criado: {user_data['email']} ({user_data['role']})")
                    else:
                        print(f"❌ Erro ao criar usuário {user_data['email']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar usuário {user_data['email']}: {e}")
        
        print(f"✅ {len(self.users)} usuários criados com sucesso!")

    async def create_customers(self, count: int = 50):
        """Cria clientes no sistema."""
        print(f"🏢 Criando {count} clientes...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do cliente
            is_male = random.choice([True, False])
            first_name = random.choice(NOMES_MASCULINOS if is_male else NOMES_FEMININOS)
            last_name = random.choice(SOBRENOMES)
            full_name = f"{first_name} {last_name}"
            city, state = random.choice(CIDADES_ESTADOS)
            
            customer_data = {
                "name": full_name,
                "email": self.generate_email(full_name),
                "phone": self.generate_phone(),
                "cpf": self.generate_cpf(),
                "address": f"Rua {random.choice(['das Flores', 'do Sol', 'da Paz', 'Principal', 'Central'])}, {random.randint(1, 999)}",
                "city": city,
                "state": state,
                "zip_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['customer']}/customers/",
                        json=customer_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        customer = response.json()
                        self.customers.append(customer)
                        print(f"✅ Cliente criado: {customer_data['name']} - {customer_data['cpf']}")
                    else:
                        print(f"❌ Erro ao criar cliente {customer_data['name']}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar cliente {customer_data['name']}: {e}")
        
        print(f"✅ {len(self.customers)} clientes criados com sucesso!")

    async def create_vehicles(self, count: int = 100):
        """Cria veículos no sistema."""
        print(f"🚗 Criando {count} veículos...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for i in range(count):
            # Gera dados do veículo
            brand = random.choice(MARCAS_VEICULOS)
            model = random.choice(MODELOS_POR_MARCA[brand])
            year = random.randint(2015, 2024)
            mileage = random.randint(0, 150000)
            
            # Preço baseado no ano e quilometragem
            base_price = random.randint(25000, 120000)
            age_factor = (2024 - year) * 0.1
            mileage_factor = mileage / 100000 * 0.2
            price = max(1000, int(base_price * (1 - age_factor - mileage_factor)))
            
            vehicle_data = {
                "brand": brand,
                "model": model,
                "year": year,
                "color": random.choice(CORES),
                "price": price,
                "mileage": mileage,
                "fuel_type": random.choice(["Flex", "Gasolina", "Etanol", "Diesel"]),
                "transmission": random.choice(["Manual", "Automático", "CVT"]),
                "description": f"{brand} {model} {year} em excelente estado de conservação.",
                "available": random.choice([True, True, True, False])  # 75% disponíveis
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['core']}/vehicles/",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        vehicle = response.json()
                        self.vehicles.append(vehicle)
                        print(f"✅ Veículo criado: {brand} {model} {year} - R$ {price:,}")
                    else:
                        print(f"❌ Erro ao criar veículo {brand} {model}: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar veículo {brand} {model}: {e}")
        
        print(f"✅ {len(self.vehicles)} veículos criados com sucesso!")

    async def create_sales(self, count: int = 30):
        """Cria vendas no sistema."""
        print(f"💰 Criando {count} vendas...")
        
        if not self.customers or not self.vehicles:
            print("❌ Necessário ter clientes e veículos para criar vendas")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Filtra apenas veículos disponíveis
        available_vehicles = [v for v in self.vehicles if v.get("available", True)]
        
        for i in range(min(count, len(available_vehicles))):
            # Seleciona cliente e veículo aleatórios
            customer = random.choice(self.customers)
            vehicle = available_vehicles[i]
            
            # Gera data de venda nos últimos 6 meses
            sale_date = datetime.now() - timedelta(days=random.randint(0, 180))
            
            sale_data = {
                "customer_cpf": customer["cpf"],
                "vehicle_id": vehicle["id"],
                "sale_date": sale_date.isoformat(),
                "sale_price": vehicle["price"] * random.uniform(0.9, 1.1),  # Variação de ±10%
                "payment_method": random.choice(["Dinheiro", "Financiamento", "Cartão", "PIX"]),
                "notes": f"Venda do veículo {vehicle['brand']} {vehicle['model']} para {customer['name']}"
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICES['sales']}/sales/",
                        json=sale_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        sale = response.json()
                        self.sales.append(sale)
                        print(f"✅ Venda criada: {vehicle['brand']} {vehicle['model']} para {customer['name']}")
                    else:
                        print(f"❌ Erro ao criar venda: {response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao criar venda: {e}")
        
        print(f"✅ {len(self.sales)} vendas criadas com sucesso!")

    async def generate_summary(self):
        """Gera resumo dos dados criados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("="*60)
        print(f"👥 Usuários: {len(self.users)}")
        print(f"🏢 Clientes: {len(self.customers)}")
        print(f"🚗 Veículos: {len(self.vehicles)}")
        print(f"💰 Vendas: {len(self.sales)}")
        print("="*60)
        
        # Estatísticas por role
        if self.users:
            roles = {}
            for user in self.users:
                role = user.get("role", "UNKNOWN")
                roles[role] = roles.get(role, 0) + 1
            
            print("👥 Usuários por role:")
            for role, count in roles.items():
                print(f"   {role}: {count}")
        
        # Estatísticas de veículos
        if self.vehicles:
            available = sum(1 for v in self.vehicles if v.get("available", True))
            sold = len(self.vehicles) - available
            print(f"🚗 Veículos disponíveis: {available}")
            print(f"🚗 Veículos vendidos: {sold}")
        
        # Valor total das vendas
        if self.sales:
            total_sales = sum(sale.get("sale_price", 0) for sale in self.sales)
            print(f"💰 Valor total das vendas: R$ {total_sales:,.2f}")
        
        print("="*60)
        print("✅ População de dados concluída com sucesso!")

async def main():
    """Função principal."""
    print("🚀 Iniciando população de dados...")
    
    populator = DataPopulator()
    
    # Verifica se os serviços estão rodando
    print("🔍 Verificando serviços...")
    for service_name, url in SERVICES.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name.upper()} Service: OK")
                else:
                    print(f"❌ {service_name.upper()} Service: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name.upper()} Service: {e}")
            return
    
    # Configura admin
    if not await populator.setup_admin_user():
        print("❌ Falha ao configurar admin. Verifique se o auth-service está funcionando.")
        return
    
    # Popula dados
    await populator.create_users(20)
    await populator.create_customers(50)
    await populator.create_vehicles(100)
    await populator.create_sales(30)
    
    # Gera resumo
    await populator.generate_summary()

if __name__ == "__main__":
    asyncio.run(main()) 