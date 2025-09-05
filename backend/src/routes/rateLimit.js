const express = require('express');
const { authenticateToken, requireAdmin } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// GET /rate-limit/stats
router.get('/stats', authenticateToken, requireAdmin, async (req, res) => {
  try {
    // Em uma implementação real, você buscaria estatísticas do Redis ou memória
    const stats = {
      service: 'unified-vehicle-api',
      window_ms: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
      max_requests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
      active_limits: [
        {
          endpoint: '/auth/login',
          window_ms: 900000,
          max_requests: 5,
          current_requests: 0
        },
        {
          endpoint: '/auth/register',
          window_ms: 900000,
          max_requests: 20,
          current_requests: 0
        },
        {
          endpoint: 'global',
          window_ms: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
          max_requests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
          current_requests: 0
        }
      ],
      timestamp: new Date().toISOString()
    };
    
    res.json(stats);
    
  } catch (error) {
    logger.error('Erro ao obter estatísticas de rate limiting:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /rate-limit/config
router.get('/config', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const config = {
      service: 'unified-vehicle-api',
      global: {
        window_ms: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
        max_requests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100
      },
      endpoints: {
        '/auth/login': {
          window_ms: 900000,
          max_requests: 5,
          description: 'Limite específico para login'
        },
        '/auth/register': {
          window_ms: 900000,
          max_requests: 20,
          description: 'Limite específico para registro'
        }
      },
      enabled: true,
      timestamp: new Date().toISOString()
    };
    
    res.json(config);
    
  } catch (error) {
    logger.error('Erro ao obter configuração de rate limiting:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /rate-limit/config
router.put('/config', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { window_ms, max_requests } = req.body;
    
    if (window_ms && (typeof window_ms !== 'number' || window_ms < 1000)) {
      return res.status(400).json({
        error: 'window_ms deve ser um número maior que 1000'
      });
    }
    
    if (max_requests && (typeof max_requests !== 'number' || max_requests < 1)) {
      return res.status(400).json({
        error: 'max_requests deve ser um número maior que 0'
      });
    }
    
    // Em uma implementação real, você atualizaria as configurações no Redis ou arquivo
    logger.info(`Configuração de rate limiting atualizada por ${req.user.email}:`, {
      window_ms,
      max_requests
    });
    
    const updatedConfig = {
      service: 'unified-vehicle-api',
      global: {
        window_ms: window_ms || parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000,
        max_requests: max_requests || parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100
      },
      message: 'Configuração atualizada com sucesso (reinicie o servidor para aplicar)',
      timestamp: new Date().toISOString()
    };
    
    res.json(updatedConfig);
    
  } catch (error) {
    logger.error('Erro ao atualizar configuração de rate limiting:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// DELETE /rate-limit/reset
router.delete('/reset', authenticateToken, requireAdmin, async (req, res) => {
  try {
    // Em uma implementação real, você resetaria os contadores no Redis
    logger.info(`Contadores de rate limiting resetados por ${req.user.email}`);
    
    res.json({
      message: 'Contadores de rate limiting resetados com sucesso',
      service: 'unified-vehicle-api',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    logger.error('Erro ao resetar contadores de rate limiting:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /rate-limit/health
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'rate-limit-service',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
