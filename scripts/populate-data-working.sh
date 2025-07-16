#!/bin/bash

# Script para popular dados funcionais (apenas veículos)

set -e

echo "🚀 Populando dados (versão funcional)..."

# Função para converter para maiúsculas (compatível com todos os shells)
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Verifica se os serviços estão rodando
echo "🔍 Verificando se os serviços estão rodando..."

services=(
    "core-service:8000"
    "auth-service:8002"
    "customer-service:8003"
    "sales-service:8001"
)

all_running=true
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        echo "✅ $(to_uppercase "$name") Service: OK"
    else
        echo "❌ $(to_uppercase "$name") Service: NOT RUNNING"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo "❌ Alguns serviços não estão rodando. Execute 'make up' primeiro."
    exit 1
fi

echo ""
echo "🔧 Populando dados de veículos..."

# Script Python para popular dados
python3 - << 'EOF'
import json
import requests
import time

# Configurações
BASE_URL = "http://localhost:8000"
VEHICLES_ENDPOINT = f"{BASE_URL}/vehicles"

def create_vehicle(vehicle_data):
    """Cria um veículo via API"""
    try:
        response = requests.post(VEHICLES_ENDPOINT, json=vehicle_data)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"❌ Erro ao criar veículo: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def main():
    print("🚗 Criando veículos de teste...")
    
    # Lista de veículos para popular
    vehicles = [
        {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2023,
            "color": "Branco",
            "price": 85000.00,
            "engine": "1.8L",
            "fuel_type": "Flex",
            "mileage": 0,
            "transmission": "Automático",
            "condition": "Novo",
            "category": "Sedan",
            "description": "Toyota Corolla 2023 - Carro popular com excelente custo-benefício"
        },
        {
            "brand": "Honda",
            "model": "Civic",
            "year": 2023,
            "color": "Preto",
            "price": 95000.00,
            "engine": "1.5L Turbo",
            "fuel_type": "Flex",
            "mileage": 0,
            "transmission": "Automático",
            "condition": "Novo",
            "category": "Sedan",
            "description": "Honda Civic 2023 - Sedan esportivo com tecnologia avançada"
        },
        {
            "brand": "Volkswagen",
            "model": "Golf",
            "year": 2022,
            "color": "Azul",
            "price": 75000.00,
            "engine": "1.4L TSI",
            "fuel_type": "Flex",
            "mileage": 15000,
            "transmission": "Automático",
            "condition": "Seminovo",
            "category": "Hatchback",
            "description": "Volkswagen Golf 2022 - Compacto premium com baixa quilometragem"
        },
        {
            "brand": "Ford",
            "model": "Ka",
            "year": 2021,
            "color": "Vermelho",
            "price": 45000.00,
            "engine": "1.0L",
            "fuel_type": "Flex",
            "mileage": 25000,
            "transmission": "Manual",
            "condition": "Seminovo",
            "category": "Hatchback",
            "description": "Ford Ka 2021 - Carro econômico ideal para cidade"
        },
        {
            "brand": "Chevrolet",
            "model": "Onix",
            "year": 2023,
            "color": "Prata",
            "price": 55000.00,
            "engine": "1.0L Turbo",
            "fuel_type": "Flex",
            "mileage": 0,
            "transmission": "Automático",
            "condition": "Novo",
            "category": "Hatchback",
            "description": "Chevrolet Onix 2023 - Líder em vendas com motor turbo"
        },
        {
            "brand": "Hyundai",
            "model": "HB20",
            "year": 2022,
            "color": "Branco",
            "price": 50000.00,
            "engine": "1.0L",
            "fuel_type": "Flex",
            "mileage": 12000,
            "transmission": "Manual",
            "condition": "Seminovo",
            "category": "Hatchback",
            "description": "Hyundai HB20 2022 - Compacto confiável com baixa quilometragem"
        },
        {
            "brand": "Nissan",
            "model": "Kicks",
            "year": 2023,
            "color": "Laranja",
            "price": 90000.00,
            "engine": "1.6L",
            "fuel_type": "Flex",
            "mileage": 0,
            "transmission": "Automático",
            "condition": "Novo",
            "category": "SUV",
            "description": "Nissan Kicks 2023 - SUV urbano com design moderno"
        },
        {
            "brand": "Jeep",
            "model": "Compass",
            "year": 2022,
            "color": "Preto",
            "price": 120000.00,
            "engine": "1.3L Turbo",
            "fuel_type": "Flex",
            "mileage": 8000,
            "transmission": "Automático",
            "condition": "Seminovo",
            "category": "SUV",
            "description": "Jeep Compass 2022 - SUV premium com baixa quilometragem"
        },
        {
            "brand": "BMW",
            "model": "320i",
            "year": 2021,
            "color": "Azul",
            "price": 180000.00,
            "engine": "2.0L Turbo",
            "fuel_type": "Gasolina",
            "mileage": 30000,
            "transmission": "Automático",
            "condition": "Seminovo",
            "category": "Sedan",
            "description": "BMW 320i 2021 - Sedan de luxo com performance esportiva"
        },
        {
            "brand": "Audi",
            "model": "A3",
            "year": 2022,
            "color": "Cinza",
            "price": 150000.00,
            "engine": "1.4L TFSI",
            "fuel_type": "Gasolina",
            "mileage": 18000,
            "transmission": "Automático",
            "condition": "Seminovo",
            "category": "Sedan",
            "description": "Audi A3 2022 - Sedan premium com tecnologia avançada"
        }
    ]
    
    created_count = 0
    for vehicle in vehicles:
        print(f"   Criando: {vehicle['brand']} {vehicle['model']} {vehicle['year']}...")
        result = create_vehicle(vehicle)
        if result:
            created_count += 1
            print(f"   ✅ Criado com ID: {result.get('id', 'N/A')}")
        else:
            print(f"   ❌ Falha ao criar veículo")
        time.sleep(0.5)  # Evita sobrecarregar a API
    
    print(f"\n🎉 População concluída! {created_count}/{len(vehicles)} veículos criados com sucesso.")
    
    if created_count > 0:
        print("\n📋 Para verificar os dados criados, acesse:")
        print("   • Frontend: http://localhost:3000")
        print("   • API: http://localhost:8000/vehicles/")
    else:
        print("\n❌ Nenhum veículo foi criado. Verifique os logs dos serviços.")

if __name__ == "__main__":
    main()
EOF

echo ""
echo "✅ Script de população concluído!" 