require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const { logger } = require('../src/utils/logger');

// Importar modelos
const User = require('../src/models/User');
const Vehicle = require('../src/models/Vehicle');
const Customer = require('../src/models/Customer');
const Sale = require('../src/models/Sale');

// Dados para geração realística
const vehicleData = {
  brands: {
    'Toyota': ['Corolla', 'Camry', 'Prius', 'RAV4'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Fit'],
    'Volkswagen': ['Jetta', 'Passat', 'Golf', 'Tiguan'],
    'Ford': ['Focus', 'Fusion', 'EcoSport', 'Ka'],
    'Chevrolet': ['Cruze', 'Onix', 'Tracker', 'Equinox'],
    'Nissan': ['Sentra', 'Altima', 'Kicks', 'X-Trail'],
    'Hyundai': ['Elantra', 'Tucson', 'HB20', 'Creta'],
    'Renault': ['Fluence', 'Sandero', 'Duster', 'Captur'],
    'Peugeot': ['408', '308', '2008', '3008'],
    'Fiat': ['Cronos', 'Argo', 'Toro', 'Pulse']
  },
  colors: ['Branco', 'Prata', 'Preto', 'Vermelho', 'Azul', 'Cinza', 'Dourado', 'Verde', 'Marrom'],
  years: [2020, 2021, 2022, 2023, 2024]
};

const customerNames = [
  'Ana Clara Silva', 'Bruno Santos Costa', 'Carla Oliveira Lima', 'Daniel Pereira Souza',
  'Eduarda Ferreira Alves', 'Felipe Rodrigues Dias', 'Gabriela Martins Santos', 'Henrique Costa Lima',
  'Isabela Alves Pereira', 'João Paulo Silva', 'Karla Souza Oliveira', 'Lucas Dias Santos',
  'Marina Lima Costa', 'Nathan Santos Silva', 'Patrícia Oliveira Souza', 'Rafael Costa Alves',
  'Sofia Silva Santos', 'Thiago Pereira Lima', 'Valentina Costa Silva', 'Wesley Santos Oliveira'
];

const addresses = [
  'Rua das Palmeiras, 123', 'Avenida Brasil, 456', 'Rua São João, 789',
  'Alameda Santos, 321', 'Rua Augusta, 654', 'Avenida Paulista, 987',
  'Rua Oscar Freire, 147', 'Rua Consolação, 258', 'Avenida Faria Lima, 369',
  'Rua Haddock Lobo, 741', 'Rua Bela Cintra, 852', 'Avenida Rebouças, 963',
  'Rua Estados Unidos, 159', 'Avenida Angélica, 357', 'Rua Teodoro Sampaio, 486',
  'Rua da Consolação, 753', 'Avenida São João, 951', 'Rua Barão de Capanema, 624',
  'Alameda Jaú, 137', 'Rua Pamplona, 248'
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

// Função para gerar telefone
const generatePhone = () => {
  const ddd = ['11', '21', '31', '41', '51', '61', '71', '81', '85', '11'];
  const selectedDDD = ddd[Math.floor(Math.random() * ddd.length)];
  const number = Math.floor(Math.random() * 900000000) + 100000000;
  return `${selectedDDD}9${number.toString().substring(0, 8)}`;
};

// Função para gerar email baseado no nome
const generateEmail = (name) => {
  const cleanName = name.toLowerCase()
    .replace(/\s+/g, '.')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
  const domains = ['gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com', 'email.com'];
  const domain = domains[Math.floor(Math.random() * domains.length)];
  return `${cleanName}@${domain}`;
};

// Função para gerar datas aleatórias
const getRandomDate = (start, end) => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
};

// Função para calcular preço baseado no ano e marca
const calculateVehiclePrice = (brand, year) => {
  const basePrices = {
    'Toyota': 90000, 'Honda': 85000, 'Volkswagen': 75000, 'Ford': 65000,
    'Chevrolet': 60000, 'Nissan': 70000, 'Hyundai': 68000, 'Renault': 55000,
    'Peugeot': 80000, 'Fiat': 50000
  };
  
  const basePrice = basePrices[brand] || 60000;
  const yearFactor = (year - 2019) * 5000; // R$ 5.000 por ano mais novo
  const variation = Math.random() * 20000 - 10000; // Variação de ±R$ 10.000
  
  return Math.max(30000, Math.floor(basePrice + yearFactor + variation));
};

const clearExistingData = async () => {
  try {
    logger.info('🧹 Limpando dados existentes...');
    
    await Sale.deleteMany({});
    await Customer.deleteMany({});
    await Vehicle.deleteMany({});
    
    // Manter apenas o admin padrão se existir
    await User.deleteMany({ 
      email: { $nin: ['admin@vehiclesales.com', 'admin@fiap.com'] } 
    });
    
    logger.info('✅ Dados existentes removidos');
  } catch (error) {
    logger.error('❌ Erro ao limpar dados:', error);
    throw error;
  }
};

const createComprehensiveUsers = async () => {
  try {
    logger.info('👥 Criando usuários...');

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
        email: 'pedro.vendedor@fiap.com',
        name: 'Pedro Santos Vendedor',
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

    for (const userData of users) {
      const existingUser = await User.findOne({ email: userData.email });
      if (!existingUser) {
        const user = new User(userData);
        await user.save();
      }
    }

    logger.info(`✅ ${users.length} usuários criados`);
  } catch (error) {
    logger.error('❌ Erro ao criar usuários:', error);
    throw error;
  }
};

const createComprehensiveVehicles = async () => {
  try {
    logger.info('🚗 Criando veículos...');

    const vehicles = [];
    let vehicleCount = 0;

    // Criar 20 veículos variados
    for (const [brand, models] of Object.entries(vehicleData.brands)) {
      if (vehicleCount >= 20) break;
      
      for (const model of models) {
        if (vehicleCount >= 20) break;
        
        const year = vehicleData.years[Math.floor(Math.random() * vehicleData.years.length)];
        const color = vehicleData.colors[Math.floor(Math.random() * vehicleData.colors.length)];
        const price = calculateVehiclePrice(brand, year);
        
        // Status distribuído: 60% disponível, 25% vendido, 15% reservado
        let status = 'DISPONÍVEL';
        const rand = Math.random();
        if (rand < 0.25) status = 'VENDIDO';
        else if (rand < 0.40) status = 'RESERVADO';
        
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

    await Vehicle.insertMany(vehicles);
    logger.info(`✅ ${vehicles.length} veículos criados`);
  } catch (error) {
    logger.error('❌ Erro ao criar veículos:', error);
    throw error;
  }
};

const createComprehensiveCustomers = async () => {
  try {
    logger.info('👤 Criando clientes...');

    const customers = [];
    
    for (let i = 0; i < 15; i++) {
      const name = customerNames[i];
      const email = generateEmail(name);
      const phone = generatePhone();
      const cpf = generateValidCPF((123456789 + i).toString());
      const address = addresses[i % addresses.length];
      
      customers.push({
        name,
        email,
        phone,
        cpf,
        address,
        city: 'São Paulo',
        state: 'SP',
        zipCode: `${String(Math.floor(Math.random() * 90000) + 10000)}${String(Math.floor(Math.random() * 900) + 100)}`
      });
    }

    await Customer.insertMany(customers);
    logger.info(`✅ ${customers.length} clientes criados`);
  } catch (error) {
    logger.error('❌ Erro ao criar clientes:', error);
    throw error;
  }
};

const createComprehensiveSales = async () => {
  try {
    logger.info('💰 Criando vendas...');

    const customers = await Customer.find();
    const vehicles = await Vehicle.find();
    const sellers = await User.find({ role: { $in: ['ADMIN', 'SALES'] } });

    if (customers.length === 0 || vehicles.length === 0 || sellers.length === 0) {
      logger.error('❌ Dados insuficientes para criar vendas');
      return;
    }

    const sales = [];
    const paymentMethods = ['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX'];
    
    // Criar 25 vendas com cenários variados
    for (let i = 0; i < 25; i++) {
      const customer = customers[Math.floor(Math.random() * customers.length)];
      const vehicle = vehicles[Math.floor(Math.random() * vehicles.length)];
      const seller = sellers[Math.floor(Math.random() * sellers.length)];
      const paymentMethod = paymentMethods[Math.floor(Math.random() * paymentMethods.length)];
      
      // Status distribuído: 50% pago, 30% pendente, 20% cancelado
      let status = 'PAGO';
      const statusRand = Math.random();
      if (statusRand < 0.30) status = 'PENDENTE';
      else if (statusRand < 0.50) status = 'CANCELADO';
      
      // Desconto aleatório (0-20%)
      const discountPercent = Math.random() * 20;
      const discount = Math.floor(vehicle.price * (discountPercent / 100));
      
      // Data da venda (últimos 6 meses)
      const saleDate = getRandomDate(
        new Date(Date.now() - 180 * 24 * 60 * 60 * 1000), // 180 dias atrás
        new Date()
      );

      // Data de pagamento (se pago)
      let paymentDate = null;
      if (status === 'PAGO') {
        paymentDate = getRandomDate(saleDate, new Date());
      }

      // Notas variadas baseadas no cenário
      let notes = `Venda ${i + 1} - ${paymentMethod}`;
      if (discount > 0) {
        notes += ` - Desconto de ${discountPercent.toFixed(1)}% aplicado`;
      }
      if (status === 'CANCELADO') {
        const cancelReasons = [
          'Cliente desistiu da compra',
          'Problema com financiamento',
          'Veículo com defeito identificado',
          'Cliente não compareceu para finalizar'
        ];
        notes += ` - Cancelado: ${cancelReasons[Math.floor(Math.random() * cancelReasons.length)]}`;
      }
      if (paymentMethod === 'FINANCIAMENTO') {
        notes += ' - Financiamento aprovado pelo banco';
      }

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
        notes: notes,
        paymentDate: paymentDate
      };

      sales.push(sale);
    }

    await Sale.insertMany(sales);
    logger.info(`✅ ${sales.length} vendas criadas`);

    // Atualizar status dos veículos conforme as vendas
    let vehiclesUpdated = 0;
    for (const sale of sales) {
      if (sale.status === 'PAGO') {
        await Vehicle.findByIdAndUpdate(sale.vehicleId, { status: 'VENDIDO' });
        vehiclesUpdated++;
      } else if (sale.status === 'PENDENTE') {
        await Vehicle.findByIdAndUpdate(sale.vehicleId, { status: 'RESERVADO' });
        vehiclesUpdated++;
      }
      // Veículos cancelados voltam para DISPONÍVEL
      else if (sale.status === 'CANCELADO') {
        await Vehicle.findByIdAndUpdate(sale.vehicleId, { status: 'DISPONÍVEL' });
        vehiclesUpdated++;
      }
    }

    logger.info(`✅ Status de ${vehiclesUpdated} veículos atualizados`);

  } catch (error) {
    logger.error('❌ Erro ao criar vendas:', error);
    throw error;
  }
};

const generateDetailedReport = async () => {
  try {
    logger.info('📊 Gerando relatório detalhado...');

    const stats = {
      users: await User.countDocuments(),
      vehicles: {
        total: await Vehicle.countDocuments(),
        available: await Vehicle.countDocuments({ status: 'DISPONÍVEL' }),
        sold: await Vehicle.countDocuments({ status: 'VENDIDO' }),
        reserved: await Vehicle.countDocuments({ status: 'RESERVADO' })
      },
      customers: await Customer.countDocuments(),
      sales: {
        total: await Sale.countDocuments(),
        paid: await Sale.countDocuments({ status: 'PAGO' }),
        pending: await Sale.countDocuments({ status: 'PENDENTE' }),
        cancelled: await Sale.countDocuments({ status: 'CANCELADO' })
      }
    };

    // Calcular receita total
    const revenueResult = await Sale.aggregate([
      { $match: { status: 'PAGO' } },
      { $group: { _id: null, total: { $sum: '$finalAmount' } } }
    ]);
    const totalRevenue = revenueResult.length > 0 ? revenueResult[0].total : 0;

    // Vendas por método de pagamento
    const paymentMethodStats = await Sale.aggregate([
      { $group: { _id: '$paymentMethod', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    logger.info('📈 === RELATÓRIO DETALHADO ===');
    logger.info(`👥 Usuários: ${stats.users}`);
    logger.info(`🚗 Veículos: ${stats.vehicles.total} (${stats.vehicles.available} disponíveis, ${stats.vehicles.sold} vendidos, ${stats.vehicles.reserved} reservados)`);
    logger.info(`👤 Clientes: ${stats.customers}`);
    logger.info(`💰 Vendas: ${stats.sales.total} (${stats.sales.paid} pagas, ${stats.sales.pending} pendentes, ${stats.sales.cancelled} canceladas)`);
    logger.info(`💵 Receita Total: R$ ${totalRevenue.toLocaleString('pt-BR')}`);
    
    logger.info('💳 Métodos de Pagamento:');
    paymentMethodStats.forEach(method => {
      logger.info(`   ${method._id}: ${method.count} vendas`);
    });

  } catch (error) {
    logger.error('❌ Erro ao gerar relatório:', error);
  }
};

const populateAdvancedData = async () => {
  try {
    logger.info('🚀 Iniciando população avançada de dados...');
    
    // Conectar ao banco
    await connectDatabase();
    
    // Limpar dados existentes
    await clearExistingData();
    
    // Criar dados em ordem de dependência
    await createComprehensiveUsers();
    await createComprehensiveVehicles();
    await createComprehensiveCustomers();
    await createComprehensiveSales();
    
    // Gerar relatório
    await generateDetailedReport();
    
    logger.info('🎉 População avançada de dados concluída com sucesso!');
    
    // Informações de login
    logger.info('🔑 === CREDENCIAIS DE ACESSO ===');
    logger.info('   👑 Admin: admin@fiap.com / admin123');
    logger.info('   💼 Vendedor: carlos.vendedor@fiap.com / vendedor123');
    logger.info('   💼 Vendedor: ana.vendedora@fiap.com / vendedor123');
    logger.info('   👤 Cliente: cliente.joao@fiap.com / cliente123');
    logger.info('   👤 Cliente: cliente.maria@fiap.com / cliente123');
    logger.info('⚠️  IMPORTANTE: Altere as senhas padrão em produção!');
    
  } catch (error) {
    logger.error('❌ Erro na população avançada de dados:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    logger.info('🔌 Conexão com banco encerrada');
    process.exit(0);
  }
};

// Executar se chamado diretamente
if (require.main === module) {
  populateAdvancedData();
}

module.exports = populateAdvancedData;
