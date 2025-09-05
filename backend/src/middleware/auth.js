const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { logger } = require('../utils/logger');

// Middleware de autenticação
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
    
    if (!token) {
      return res.status(401).json({
        error: 'Token de acesso necessário'
      });
    }
    
    // Verificar token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Buscar usuário
    const user = await User.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({
        error: 'Usuário não encontrado'
      });
    }
    
    if (user.status !== 'ACTIVE') {
      return res.status(401).json({
        error: 'Usuário inativo'
      });
    }
    
    // Adicionar usuário ao request
    req.user = user;
    req.token = token;
    
    next();
  } catch (error) {
    logger.error('Erro na autenticação:', error);
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: 'Token inválido'
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Token expirado'
      });
    }
    
    return res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
};

// Middleware de autorização por papel
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Usuário não autenticado'
      });
    }
    
    const userRoles = Array.isArray(req.user.role) ? req.user.role : [req.user.role];
    const requiredRoles = Array.isArray(roles) ? roles : [roles];
    
    const hasRole = requiredRoles.some(role => userRoles.includes(role));
    
    if (!hasRole) {
      return res.status(403).json({
        error: 'Acesso negado',
        required_roles: requiredRoles,
        user_roles: userRoles
      });
    }
    
    next();
  };
};

// Middleware para verificar se é admin
const requireAdmin = requireRole(['ADMIN']);

// Middleware para verificar se é vendedor ou admin
const requireSalesOrAdmin = requireRole(['SALES', 'ADMIN']);

// Middleware opcional de autenticação (não falha se não autenticado)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];
    
    if (token) {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findById(decoded.userId);
      
      if (user && user.status === 'ACTIVE') {
        req.user = user;
        req.token = token;
      }
    }
    
    next();
  } catch (error) {
    // Ignora erros de token em auth opcional
    next();
  }
};

// Middleware para verificar propriedade do recurso
const requireOwnership = (getResourceOwnerId) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          error: 'Usuário não autenticado'
        });
      }
      
      // Admins podem acessar qualquer recurso
      if (req.user.role === 'ADMIN') {
        return next();
      }
      
      const resourceOwnerId = await getResourceOwnerId(req);
      
      if (resourceOwnerId && resourceOwnerId.toString() !== req.user._id.toString()) {
        return res.status(403).json({
          error: 'Acesso negado - você só pode acessar seus próprios recursos'
        });
      }
      
      next();
    } catch (error) {
      logger.error('Erro na verificação de propriedade:', error);
      return res.status(500).json({
        error: 'Erro interno do servidor'
      });
    }
  };
};

module.exports = {
  authenticateToken,
  requireRole,
  requireAdmin,
  requireSalesOrAdmin,
  optionalAuth,
  requireOwnership
};
