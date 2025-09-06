require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const { logger } = require('../src/utils/logger');

// Importar modelos
const Vehicle = require('../src/models/Vehicle');
const Sale = require('../src/models/Sale');

async function validateDb() {
  try {
    await connectDatabase();
    
    // Verificar veículos com preços negativos
    const negativeVehicles = await Vehicle.countDocuments({ price: { $lt: 0 } });
    
    // Verificar vendas com valores negativos
    const negativeSales = await Sale.countDocuments({
      $or: [
        { totalAmount: { $lt: 0 } },
        { finalAmount: { $lt: 0 } },
        { discount: { $lt: 0 } }
      ]
    });
    
    // Verificar vendas onde desconto > valor total
    const invalidDiscounts = await Sale.countDocuments({
      $expr: { $gt: ['$discount', '$totalAmount'] }
    });
    
    // Verificar vendas órfãs (sem veículo ou cliente válido)
    const invalidSales = await Sale.aggregate([
      {
        $lookup: {
          from: 'vehicles',
          localField: 'vehicleId',
          foreignField: '_id',
          as: 'vehicle'
        }
      },
      {
        $lookup: {
          from: 'customers',
          localField: 'customerId',
          foreignField: '_id',
          as: 'customer'
        }
      },
      {
        $match: {
          $or: [
            { vehicle: { $size: 0 } },
            { customer: { $size: 0 } }
          ]
        }
      },
      {
        $count: 'total'
      }
    ]);
    
    const orphanSales = invalidSales.length > 0 ? invalidSales[0].total : 0;
    
    // Verificar inconsistências de data
    const futureSales = await Sale.countDocuments({
      saleDate: { $gt: new Date() }
    });
    
    const invalidPaymentDates = await Sale.countDocuments({
      $and: [
        { paymentDate: { $ne: null } },
        { $expr: { $lt: ['$paymentDate', '$saleDate'] } }
      ]
    });
    
    console.log('\n✅ === VALIDAÇÃO DE INTEGRIDADE DOS DADOS ===');
    console.log(`🚗 Veículos com preço negativo: ${negativeVehicles}`);
    console.log(`💰 Vendas com valores negativos: ${negativeSales}`);
    console.log(`💳 Vendas com desconto inválido: ${invalidDiscounts}`);
    console.log(`🔗 Vendas órfãs (sem veículo/cliente): ${orphanSales}`);
    console.log(`📅 Vendas com data futura: ${futureSales}`);
    console.log(`⏰ Vendas com data de pagamento anterior à venda: ${invalidPaymentDates}`);
    
    const totalProblems = negativeVehicles + negativeSales + invalidDiscounts + orphanSales + futureSales + invalidPaymentDates;
    
    if (totalProblems === 0) {
      console.log('\n🎉 TODOS OS DADOS ESTÃO VÁLIDOS!');
      console.log('✅ Nenhum problema de integridade encontrado.');
    } else {
      console.log(`\n⚠️  PROBLEMAS ENCONTRADOS: ${totalProblems}`);
      console.log('❌ Recomenda-se revisar e corrigir os dados inconsistentes.');
    }
    
    console.log('');
    
  } catch (error) {
    console.error('❌ Erro ao validar banco:', error.message);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  validateDb();
}

module.exports = validateDb;
