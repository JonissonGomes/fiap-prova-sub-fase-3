require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const { logger } = require('../src/utils/logger');

// Importar modelos
const User = require('../src/models/User');
const Vehicle = require('../src/models/Vehicle');
const Customer = require('../src/models/Customer');
const Sale = require('../src/models/Sale');

async function getDbStatus() {
  try {
    await connectDatabase();
    
    // Contar documentos
    const users = await User.countDocuments();
    const vehicles = await Vehicle.countDocuments();
    const customers = await Customer.countDocuments();
    const sales = await Sale.countDocuments();
    
    // Calcular receita total
    const revenueResult = await Sale.aggregate([
      { $match: { status: 'PAGO' } },
      { $group: { _id: null, total: { $sum: '$finalAmount' } } }
    ]);
    const totalRevenue = revenueResult.length > 0 ? revenueResult[0].total : 0;
    
    // Status dos veículos
    const vehicleStatus = await Vehicle.aggregate([
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 }
        }
      }
    ]);
    
    // Status das vendas
    const salesStatus = await Sale.aggregate([
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 }
        }
      }
    ]);
    
    // Métodos de pagamento
    const paymentMethods = await Sale.aggregate([
      {
        $group: {
          _id: '$paymentMethod',
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    console.log('\n📊 === ESTATÍSTICAS DO BANCO DE DADOS ===');
    console.log(`👥 Usuários: ${users}`);
    console.log(`🚗 Veículos: ${vehicles}`);
    console.log(`👤 Clientes: ${customers}`);
    console.log(`💰 Vendas: ${sales}`);
    console.log(`💵 Receita Total: R$ ${totalRevenue.toLocaleString('pt-BR')}`);
    
    console.log('\n🚗 Status dos Veículos:');
    vehicleStatus.forEach(status => {
      console.log(`   ${status._id}: ${status.count} veículos`);
    });
    
    console.log('\n💰 Status das Vendas:');
    salesStatus.forEach(status => {
      console.log(`   ${status._id}: ${status.count} vendas`);
    });
    
    console.log('\n💳 Métodos de Pagamento:');
    paymentMethods.forEach(method => {
      console.log(`   ${method._id}: ${method.count} vendas`);
    });
    
    console.log('');
    
  } catch (error) {
    console.error('❌ Erro ao obter status do banco:', error.message);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  getDbStatus();
}

module.exports = getDbStatus;
