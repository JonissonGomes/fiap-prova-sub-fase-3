const rateLimit = require('express-rate-limit');
const { logger } = require('../utils/logger');

// Rate limiting
const createRateLimiter = (windowMs = 15 * 60 * 1000, max = 100) => {
  return rateLimit({
    windowMs,
    max,
    message: {
      error: 'Muitas requisições, tente novamente mais tarde',
      retryAfter: Math.ceil(windowMs / 1000)
    },
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
      logger.warn(`Rate limit atingido para IP ${req.ip} na rota ${req.path}`);
      res.status(429).json({
        error: 'Muitas requisições, tente novamente mais tarde',
        retryAfter: Math.ceil(windowMs / 1000)
      });
    }
  });
};

const setupMiddleware = (app) => {
  // Rate limiting global
  const windowMs = parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000; // 15 minutos
  const maxRequests = parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100;
  
  app.use(createRateLimiter(windowMs, maxRequests));
  
  // Middleware de logging de requisições
  app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
      const duration = Date.now() - start;
      logger.info(`${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
    });
    
    next();
  });
};

module.exports = {
  setupMiddleware,
  createRateLimiter
};
