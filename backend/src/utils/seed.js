const User = require('../models/User');
const { logger } = require('./logger');

const createDefaultAdmin = async () => {
  try {
    const adminEmail = process.env.DEFAULT_ADMIN_EMAIL || 'admin@vehiclesales.com';
    const adminPassword = process.env.DEFAULT_ADMIN_PASSWORD || 'admin123';
    
    // Verificar se o admin já existe
    const existingAdmin = await User.findOne({ email: adminEmail });
    if (existingAdmin) {
      logger.info(`Usuário admin já existe`);
      return existingAdmin;
    }
    
    // Criar o usuário admin
    const admin = new User({
      email: adminEmail,
      name: 'Administrador',
      password: adminPassword,
      role: 'ADMIN',
      status: 'ACTIVE'
    });
    
    await admin.save();
    
    logger.info(`Usuário admin criado com sucesso: ${adminEmail}`);
    logger.info('Credenciais padrão:');
    logger.info(`  Email: ${adminEmail}`);
    logger.info(`  Senha: ${adminPassword}`);
    logger.info('⚠️  IMPORTANTE: Altere a senha padrão em produção!');
    
    return admin;
    
  } catch (error) {
    logger.error('Erro ao criar usuário admin:', error);
    throw error;
  }
};

const createSampleData = async () => {
  try {
    const Vehicle = require('../models/Vehicle');
    const Customer = require('../models/Customer');
    
    // Verificar se já existem dados
    const vehicleCount = await Vehicle.countDocuments();
    const customerCount = await Customer.countDocuments();
    
    if (vehicleCount > 0 && customerCount > 0) {
      logger.info('Dados de exemplo já existem');
      return;
    }
    
    // Criar veículos de exemplo
    const sampleVehicles = [
      {
        brand: 'Toyota',
        model: 'Corolla',
        year: 2022,
        color: 'Prata',
        price: 95000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Honda',
        model: 'Civic',
        year: 2023,
        color: 'Preto',
        price: 110000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Volkswagen',
        model: 'Jetta',
        year: 2021,
        color: 'Branco',
        price: 85000,
        status: 'DISPONÍVEL'
      },
      {
        brand: 'Ford',
        model: 'Focus',
        year: 2020,
        color: 'Azul',
        price: 70000,
        status: 'DISPONÍVEL'
      }
    ];
    
    if (vehicleCount === 0) {
      await Vehicle.insertMany(sampleVehicles);
      logger.info(`${sampleVehicles.length} veículos de exemplo criados`);
    }
    
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

    // Criar clientes de exemplo
    const sampleCustomers = [
      {
        name: 'João Silva',
        email: 'joao.silva@email.com',
        phone: '11987654321',
        cpf: generateValidCPF('123456789'),
        address: 'Rua das Flores, 123',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01234567'
      },
      {
        name: 'Maria Santos',
        email: 'maria.santos@email.com',
        phone: '11876543210',
        cpf: generateValidCPF('987654321'),
        address: 'Avenida Paulista, 456',
        city: 'São Paulo',
        state: 'SP',
        zipCode: '01310100'
      }
    ];
    
    if (customerCount === 0) {
      await Customer.insertMany(sampleCustomers);
      logger.info(`${sampleCustomers.length} clientes de exemplo criados`);
    }
    
    logger.info('Dados de exemplo criados com sucesso');
    
  } catch (error) {
    logger.error('Erro ao criar dados de exemplo:', error);
  }
};

module.exports = {
  createDefaultAdmin,
  createSampleData
};
