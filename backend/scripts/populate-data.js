require('dotenv').config({ path: '../config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const { createDefaultAdmin, createSampleData } = require('../src/utils/seed');
const { logger } = require('../src/utils/logger');

async function populate() {
  try {
    logger.info('Iniciando população de dados...');
    
    // Conectar ao banco
    await connectDatabase();
    
    // Criar admin padrão
    await createDefaultAdmin();
    
    // Criar dados de exemplo
    await createSampleData();
    
    logger.info('População de dados concluída com sucesso!');
    
  } catch (error) {
    logger.error('Erro na população de dados:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  populate();
}

module.exports = populate;
