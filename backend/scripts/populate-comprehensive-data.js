require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const { logger } = require('../src/utils/logger');

// Importar modelos
const User = require('../src/models/User');
const Vehicle = require('../src/models/Vehicle');
const Customer = require('../src/models/Customer');
const Sale = require('../src/models/Sale');

// Função para gerar CPF válido
const generateValidCPF = (base) => {
  const cpf = base.padStart(9, '0');
  
  // Primeiro dígito verificador
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf[i]) * (10 - i);
  }
  const digit1 = 11 - (sum % 11);
  const firstDigit = digit1 >= 10 ? 0 : digit1;
  
  // Segundo dígito verificador
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt((cpf + firstDigit)[i]) * (11 - i);
  }
  const digit2 = 11 - (sum % 11);
  const secondDigit = digit2 >= 10 ? 0 : digit2;
  
  return cpf + firstDigit + secondDigit;
};

// Função para gerar datas aleatórias
const getRandomDate = (start, end) => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
};

// Função para gerar preço aleatório em uma faixa
const getRandomPrice = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const createUsers = async () => {
  try {
    const existingUsers = await User.countDocuments();
    if (existingUsers > 3) {
      logger.info('Usuários já existem no banco');
      return;
    }

    const users = [
      {
        email: 'admin@fiap.com',
        name: 'Administrator FIAP',
        password: 'admin123',
        role: 'ADMIN',
        status: 'ACTIVE'
      },
      {
        email: 'vendedor1@fiap.com',
        name: 'Carlos Vendedor',
        password: 'vendedor123',
        role: 'SALES',
        status: 'ACTIVE'
      },
      {
        email: 'vendedor2@fiap.com',
        name: 'Ana Vendedora',
        password: 'vendedor123',
        role: 'SALES',
        status: 'ACTIVE'
      },
      {
        email: 'cliente1@fiap.com',
        name: 'João Cliente',
        password: 'cliente123',
        role: 'CUSTOMER',
        status: 'ACTIVE'
      },
      {
        email: 'cliente2@fiap.com',
        name: 'Maria Cliente',
        password: 'cliente123',
        role: 'CUSTOMER',
        status: 'ACTIVE'
      }
    ];

    for (const userData of users) {
      const existingUser = await User.findOne({ email: userData.email });
      if (!existingUser) {
        const user = new User(userData);
        await user.save();
        logger.info(`Usuário criado: ${userData.email}`);
      }
    }

    logger.info('Usuários criados com sucesso');
  } catch (error) {
    logger.error('Erro ao criar usuários:', error);
    throw error;
  }
};

const createVehicles = async () => {
  try {
    const existingVehicles = await Vehicle.countDocuments();
    if (existingVehicles > 5) {
      logger.info('Veículos já existem no banco');
      return;
    }

    const vehicles = [
      {
        brand: 'Toyota',
        model: 'Corolla',
        year: 2023,
        color: 'Prata',
        price: 98500,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Honda',
        model: 'Civic',
        year: 2022,
        color: 'Preto',
        price: 112000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Volkswagen',
        model: 'Jetta',
        year: 2023,
        color: 'Branco',
        price: 89900,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Ford',
        model: 'Focus',
        year: 2021,
        color: 'Azul',
        price: 72000,
        status: 'VENDIDO'
      },
      {
        brand: 'Chevrolet',
        model: 'Cruze',
        year: 2022,
        color: 'Vermelho',
        price: 85000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Nissan',
        model: 'Sentra',
        year: 2023,
        color: 'Cinza',
        price: 95000,
        status: 'RESERVADO'
      },
      {
        brand: 'Hyundai',
        model: 'Elantra',
        year: 2022,
        color: 'Branco',
        price: 88000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Renault',
        model: 'Fluence',
        year: 2021,
        color: 'Prata',
        price: 65000,
        status: 'VENDIDO'
      },
      {
        brand: 'Peugeot',
        model: '408',
        year: 2023,
        color: 'Preto',
        price: 105000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Fiat',
        model: 'Cronos',
        year: 2022,
        color: 'Azul',
        price: 68000,
        status: 'DISPONÍVEL'
      }
    ];

    await Vehicle.insertMany(vehicles);
    logger.info(`${vehicles.length} veículos criados com sucesso`);
  } catch (error) {
    logger.error('Erro ao criar veículos:', error);
    throw error;
  }
};

const createCustomers = async () => {
  try {
    const existingCustomers = await Customer.countDocuments();
    if (existingCustomers > 5) {
      logger.info('Clientes já existem no banco');
      return;
    }

    const customers = [
      {
        name: 'João Silva Santos',
        email: 'joao.silva@email.com',
        phone: '11987654321',
        cpf: generateValidCPF('123456789'),
        address: 'Rua das Flores, 123, Apt 45',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01234567'
      },
      {
        name: 'Maria Oliveira Costa',
        email: 'maria.oliveira@email.com',
        phone: '11876543210',
        cpf: generateValidCPF('987654321'),
        address: 'Avenida Paulista, 456, Conjunto 12',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01310100'
      },
      {
        name: 'Pedro Henrique Lima',
        email: 'pedro.lima@email.com',
        phone: '11765432109',
        cpf: generateValidCPF('456789123'),
        address: 'Rua Augusta, 789',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01305000'
      },
      {
        name: 'Ana Carolina Souza',
        email: 'ana.souza@email.com',
        phone: '11654321098',
        cpf: generateValidCPF('789123456'),
        address: 'Alameda Santos, 321',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01419000'
      },
      {
        name: 'Carlos Eduardo Pereira',
        email: 'carlos.pereira@email.com',
        phone: '11543210987',
        cpf: generateValidCPF('321654987'),
        address: 'Rua Oscar Freire, 654',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01426000'
      },
      {
        name: 'Fernanda Alves Rodrigues',
        email: 'fernanda.alves@email.com',
        phone: '11432109876',
        cpf: generateValidCPF('654987321'),
        address: 'Rua Consolação, 987',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01301000'
      },
      {
        name: 'Roberto José Martins',
        email: 'roberto.martins@email.com',
        phone: '11321098765',
        cpf: generateValidCPF('147258369'),
        address: 'Avenida Faria Lima, 1234',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01452000'
      },
      {
        name: 'Juliana Ferreira Dias',
        email: 'juliana.dias@email.com',
        phone: '11210987654',
        cpf: generateValidCPF('963852741'),
        address: 'Rua Haddock Lobo, 567',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01414000'
      },
      {
        name: 'Ricardo Mendes Silva',
        email: 'ricardo.mendes@email.com',
        phone: '11109876543',
        cpf: generateValidCPF('852741963'),
        address: 'Rua Bela Cintra, 890',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01415000'
      },
      {
        name: 'Luciana Santos Oliveira',
        email: 'luciana.santos@email.com',
        phone: '11098765432',
        cpf: generateValidCPF('741963852'),
        address: 'Avenida Rebouças, 2345',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '05402000'
      }
    ];

    await Customer.insertMany(customers);
    logger.info(`${customers.length} clientes criados com sucesso`);
  } catch (error) {
    logger.error('Erro ao criar clientes:', error);
    throw error;
  }
};

const createSales = async () => {
  try {
    const existingSales = await Sale.countDocuments();
    if (existingSales > 3) {
      logger.info('Vendas já existem no banco');
      return;
    }

    // Buscar dados necessários para as vendas
    const customers = await Customer.find().limit(10);
    const vehicles = await Vehicle.find();
    const sellers = await User.find({ role: { $in: ['ADMIN', 'SALES'] } });

    if (customers.length === 0 || vehicles.length === 0 || sellers.length === 0) {
      logger.error('Dados insuficientes para criar vendas');
      return;
    }

    const sales = [];
    const paymentMethods = ['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX'];
    const statuses = ['PENDENTE', 'PAGO', 'CANCELADO'];

    // Criar 10 vendas variadas
    for (let i = 0; i < 10; i++) {
      const customer = customers[i % customers.length];
      const vehicle = vehicles[i % vehicles.length];
      const seller = sellers[i % sellers.length];
      const status = statuses[i % statuses.length];
      const paymentMethod = paymentMethods[i % paymentMethods.length];
      
      // Calcular desconto aleatório (0-15%)
      const discountPercent = Math.random() * 15;
      const discount = Math.floor(vehicle.price * (discountPercent / 100));
      
      // Data da venda (últimos 3 meses)
      const saleDate = getRandomDate(
        new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // 90 dias atrás
        new Date()
      );

      const sale = {
        customerId: customer._id,
        vehicleId: vehicle._id,
        sellerId: seller._id,
        saleDate: saleDate,
        totalAmount: vehicle.price,
        status: status,
        paymentMethod: paymentMethod,
        discount: discount,
        finalAmount: vehicle.price - discount,
        notes: `Venda ${i + 1} - ${paymentMethod} - Desconto de ${discountPercent.toFixed(1)}%`,
        paymentDate: status === 'PAGO' ? getRandomDate(saleDate, new Date()) : null
      };

      sales.push(sale);
    }

    await Sale.insertMany(sales);
    logger.info(`${sales.length} vendas criadas com sucesso`);

    // Atualizar status dos veículos vendidos
    for (const sale of sales) {
      if (sale.status === 'PAGO') {
        await Vehicle.findByIdAndUpdate(sale.vehicleId, { status: 'VENDIDO' });
      } else if (sale.status === 'PENDENTE') {
        await Vehicle.findByIdAndUpdate(sale.vehicleId, { status: 'RESERVADO' });
      }
    }

    logger.info('Status dos veículos atualizados conforme as vendas');

  } catch (error) {
    logger.error('Erro ao criar vendas:', error);
    throw error;
  }
};

const populateComprehensiveData = async () => {
  try {
    logger.info('🚀 Iniciando população abrangente de dados...');
    
    // Conectar ao banco
    await connectDatabase();
    
    // Limpar dados existentes (opcional - descomente se quiser resetar)
    // logger.info('Limpando dados existentes...');
    // await Sale.deleteMany({});
    // await Customer.deleteMany({});
    // await Vehicle.deleteMany({});
    // await User.deleteMany({ email: { $ne: 'admin@vehiclesales.com' } });
    
    // Criar dados em ordem de dependência
    await createUsers();
    await createVehicles();
    await createCustomers();
    await createSales();
    
    // Estatísticas finais
    const stats = {
      users: await User.countDocuments(),
      vehicles: await Vehicle.countDocuments(),
      customers: await Customer.countDocuments(),
      sales: await Sale.countDocuments()
    };
    
    logger.info('📊 População de dados concluída com sucesso!');
    logger.info('📈 Estatísticas finais:');
    logger.info(`   👥 Usuários: ${stats.users}`);
    logger.info(`   🚗 Veículos: ${stats.vehicles}`);
    logger.info(`   👤 Clientes: ${stats.customers}`);
    logger.info(`   💰 Vendas: ${stats.sales}`);
    
    // Informações de login
    logger.info('🔑 Credenciais de acesso:');
    logger.info('   Admin: admin@fiap.com / admin123');
    logger.info('   Vendedor: vendedor1@fiap.com / vendedor123');
    logger.info('   Cliente: cliente1@fiap.com / cliente123');
    
  } catch (error) {
    logger.error('❌ Erro na população de dados:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    logger.info('🔌 Conexão com banco encerrada');
    process.exit(0);
  }
};

// Executar se chamado diretamente
if (require.main === module) {
  populateComprehensiveData();
}

module.exports = populateComprehensiveData;
