const mongoose = require('mongoose');
const { logger } = require('../utils/logger');

const connectDatabase = async () => {
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
    
    logger.info('Conectado ao MongoDB com sucesso');
    
    // Event listeners
    mongoose.connection.on('error', (error) => {
      logger.error('Erro na conexão MongoDB:', error);
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB desconectado');
    });

    mongoose.connection.on('reconnected', () => {
      logger.info('MongoDB reconectado');
    });

  } catch (error) {
    logger.error('Erro ao conectar ao MongoDB:', error);
    throw error;
  }
};

const disconnectDatabase = async () => {
  try {
    await mongoose.disconnect();
    logger.info('Desconectado do MongoDB');
  } catch (error) {
    logger.error('Erro ao desconectar do MongoDB:', error);
  }
};

module.exports = {
  connectDatabase,
  disconnectDatabase
};
