require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { logger } = require('../src/utils/logger');

// Importar modelos
const User = require('../src/models/User');
const Vehicle = require('../src/models/Vehicle');
const Customer = require('../src/models/Customer');
const Sale = require('../src/models/Sale');

// Conectar usando a mesma configuração da API
const connectToCloudDatabase = async () => {
  try {
    const mongoUrl = process.env.MONGODB_URL || 'mongodb://localhost:27017';
    const dbName = process.env.MONGODB_DB_NAME || 'unified_vehicle_db';
    
    const connectionString = `${mongoUrl}/${dbName}`;
    
    const options = {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
      bufferCommands: false
    };

    await mongoose.connect(connectionString, options);
    
    logger.info(`Conectado ao MongoDB (mesmo da API): ${connectionString}`);
    
  } catch (error) {
    logger.error('Erro ao conectar ao MongoDB:', error);
    throw error;
  }
};

// Dados para geração realística
const vehicleData = {
  brands: {
    'Toyota': ['Corolla', 'Camry', 'Prius', 'RAV4'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Fit'],
    'Volkswagen': ['Jetta', 'Passat', 'Golf', 'Tiguan'],
    'Ford': ['Focus', 'Fusion', 'EcoSport', 'Ka'],
    'Chevrolet': ['Cruze', 'Onix', 'Tracker', 'Equinox']
  },
  colors: ['Branco', 'Prata', 'Preto', 'Vermelho', 'Azul', 'Cinza'],
  years: [2021, 2022, 2023, 2024]
};

const customerNames = [
  'Ana Clara Silva', 'Bruno Santos Costa', 'Carla Oliveira Lima', 'Daniel Pereira Souza',
  'Eduarda Ferreira Alves', 'Felipe Rodrigues Dias', 'Gabriela Martins Santos'
];

// Função para gerar CPF válido
const generateValidCPF = (base) => {
  const cpf = base.padStart(9, '0');
  
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf[i]) * (10 - i);
  }
  const digit1 = 11 - (sum % 11);
  const firstDigit = digit1 >= 10 ? 0 : digit1;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt((cpf + firstDigit)[i]) * (11 - i);
  }
  const digit2 = 11 - (sum % 11);
  const secondDigit = digit2 >= 10 ? 0 : digit2;
  
  return cpf + firstDigit + secondDigit;
};

// Função para gerar email baseado no nome
const generateEmail = (name) => {
  const cleanName = name.toLowerCase()
    .replace(/\s+/g, '.')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
  const domains = ['gmail.com', 'hotmail.com', 'yahoo.com.br'];
  const domain = domains[Math.floor(Math.random() * domains.length)];
  return `${cleanName}@${domain}`;
};

// Função para calcular preço baseado no ano e marca
const calculateVehiclePrice = (brand, year) => {
  const basePrices = {
    'Toyota': 90000, 'Honda': 85000, 'Volkswagen': 75000, 'Ford': 65000, 'Chevrolet': 60000
  };
  
  const basePrice = basePrices[brand] || 60000;
  const yearFactor = (year - 2020) * 5000;
  const variation = Math.random() * 20000 - 10000;
  
  return Math.max(30000, Math.floor(basePrice + yearFactor + variation));
};

const populateCloudData = async () => {
  try {
    logger.info('🚀 Populando dados no banco da API (cloud)...');
    
    // Conectar ao banco correto (mesmo da API)
    await connectToCloudDatabase();
    
    // 1. Criar usuários
    const users = [
      {
        email: 'admin@fiap.com',
        name: 'Administrador FIAP',
        password: 'admin123',
        role: 'ADMIN',
        status: 'ACTIVE'
      },
      {
        email: 'carlos.vendedor@fiap.com',
        name: 'Carlos Silva Vendedor',
        password: 'vendedor123',
        role: 'SALES',
        status: 'ACTIVE'
      },
      {
        email: 'ana.vendedora@fiap.com',
        name: 'Ana Costa Vendedora',
        password: 'vendedor123',
        role: 'SALES',
        status: 'ACTIVE'
      },
      {
        email: 'cliente.joao@fiap.com',
        name: 'João Paulo Cliente',
        password: 'cliente123',
        role: 'CUSTOMER',
        status: 'ACTIVE'
      },
      {
        email: 'cliente.maria@fiap.com',
        name: 'Maria Silva Cliente',
        password: 'cliente123',
        role: 'CUSTOMER',
        status: 'ACTIVE'
      }
    ];

    console.log('👥 Criando usuários...');
    for (const userData of users) {
      const existingUser = await User.findOne({ email: userData.email });
      if (!existingUser) {
        const user = new User(userData);
        await user.save();
        console.log(`  ✅ Criado: ${userData.email}`);
      } else {
        console.log(`  ➡️ Já existe: ${userData.email}`);
      }
    }

    // 2. Criar veículos
    console.log('🚗 Criando veículos...');
    const vehicles = [];
    let vehicleCount = 0;

    for (const [brand, models] of Object.entries(vehicleData.brands)) {
      if (vehicleCount >= 15) break;
      
      for (const model of models) {
        if (vehicleCount >= 15) break;
        
        const year = vehicleData.years[Math.floor(Math.random() * vehicleData.years.length)];
        const color = vehicleData.colors[Math.floor(Math.random() * vehicleData.colors.length)];
        const price = calculateVehiclePrice(brand, year);
        
        // Status distribuído
        let status = 'DISPONÍVEL';
        const rand = Math.random();
        if (rand < 0.2) status = 'VENDIDO';
        else if (rand < 0.3) status = 'RESERVADO';
        
        vehicles.push({
          brand,
          model,
          year,
          color,
          price,
          status
        });
        
        vehicleCount++;
      }
    }

    const existingVehicles = await Vehicle.countDocuments();
    if (existingVehicles < 10) {
      await Vehicle.insertMany(vehicles);
      console.log(`  ✅ ${vehicles.length} veículos criados`);
    } else {
      console.log(`  ➡️ Já existem ${existingVehicles} veículos`);
    }

    // 3. Criar clientes
    console.log('👤 Criando clientes...');
    const customers = [];
    
    for (let i = 0; i < 7; i++) {
      const name = customerNames[i];
      const email = generateEmail(name);
      const cpf = generateValidCPF((123456780 + i).toString());
      
      customers.push({
        name,
        email,
        phone: `119${String(Math.floor(Math.random() * 100000000)).padStart(8, '0')}`,
        cpf,
        address: `Rua Exemplo, ${100 + i * 10}`,
        city: 'São Paulo',
        state: 'SP',
        zipCode: `${String(Math.floor(Math.random() * 90000) + 10000)}000`
      });
    }

    const existingCustomers = await Customer.countDocuments();
    if (existingCustomers < 5) {
      await Customer.insertMany(customers);
      console.log(`  ✅ ${customers.length} clientes criados`);
    } else {
      console.log(`  ➡️ Já existem ${existingCustomers} clientes`);
    }

    // 4. Estatísticas finais
    const finalStats = {
      users: await User.countDocuments(),
      vehicles: await Vehicle.countDocuments(),
      customers: await Customer.countDocuments(),
      sales: await Sale.countDocuments()
    };
    
    console.log('\n📊 === POPULAÇÃO CONCLUÍDA ===');
    console.log(`👥 Usuários: ${finalStats.users}`);
    console.log(`🚗 Veículos: ${finalStats.vehicles}`);
    console.log(`👤 Clientes: ${finalStats.customers}`);
    console.log(`💰 Vendas: ${finalStats.sales}`);
    
    console.log('\n🔑 === CREDENCIAIS PARA TESTE ===');
    console.log('👑 Admin: admin@fiap.com / admin123');
    console.log('💼 Vendedor: carlos.vendedor@fiap.com / vendedor123');
    console.log('👤 Cliente: cliente.joao@fiap.com / cliente123');
    
  } catch (error) {
    logger.error('❌ Erro na população:', error);
    throw error;
  } finally {
    await mongoose.disconnect();
    logger.info('🔌 Conexão encerrada');
    process.exit(0);
  }
};

if (require.main === module) {
  populateCloudData();
}

module.exports = populateCloudData;
