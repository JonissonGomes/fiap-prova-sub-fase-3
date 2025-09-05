const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
require('dotenv').config({ path: './config.env' });

const { connectDatabase } = require('./config/database');
const { setupMiddleware } = require('./middleware');
const routes = require('./routes');
const { logger } = require('./utils/logger');
const { createDefaultAdmin } = require('./utils/seed');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware básico
app.use(helmet());
app.use(compression());
app.use(morgan('combined'));

// CORS
const allowedOrigins = process.env.ALLOWED_ORIGINS 
  ? process.env.ALLOWED_ORIGINS.split(',')
  : ['http://localhost:3000'];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Configurar middleware personalizado
setupMiddleware(app);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'unified-vehicle-api',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Rotas principais
app.use('/auth', routes.auth);
app.use('/vehicles', routes.vehicles);
app.use('/customers', routes.customers);
app.use('/sales', routes.sales);
app.use('/rate-limit', routes.rateLimit);

// Rota raiz
app.get('/', (req, res) => {
  res.json({
    message: 'Unified Vehicle Sales API',
    version: '1.0.0',
    endpoints: {
      auth: '/auth',
      vehicles: '/vehicles',
      customers: '/customers',
      sales: '/sales',
      health: '/health'
    }
  });
});

// Error handling
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Dados inválidos',
      details: err.message
    });
  }
  
  if (err.name === 'MongoError' && err.code === 11000) {
    return res.status(409).json({
      error: 'Recurso já existe',
      details: 'Dados duplicados'
    });
  }
  
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'Token inválido'
    });
  }
  
  res.status(err.status || 500).json({
    error: err.message || 'Erro interno do servidor'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint não encontrado',
    path: req.originalUrl
  });
});

// Inicializar servidor
async function startServer() {
  try {
    // Conectar ao banco
    await connectDatabase();
    logger.info('Conectado ao MongoDB com sucesso');
    
    // Criar admin padrão
    await createDefaultAdmin();
    
    // Iniciar servidor
    app.listen(PORT, () => {
      logger.info(`🚀 Servidor rodando na porta ${PORT}`);
      logger.info(`🌍 Ambiente: ${process.env.NODE_ENV}`);
      logger.info(`📊 Health check: http://localhost:${PORT}/health`);
    });
    
  } catch (error) {
    logger.error('Erro ao iniciar servidor:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM recebido, desligando servidor...');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT recebido, desligando servidor...');
  process.exit(0);
});

if (require.main === module) {
  startServer();
}

module.exports = app;
