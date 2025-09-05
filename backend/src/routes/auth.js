const express = require('express');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const { authenticateToken, requireAdmin } = require('../middleware/auth');
const { createRateLimiter } = require('../middleware');
const { logger } = require('../utils/logger');

const router = express.Router();

// Rate limiting específico para auth
const authLimiter = createRateLimiter(15 * 60 * 1000, 20); // 20 tentativas por 15 minutos
const loginLimiter = createRateLimiter(15 * 60 * 1000, 5); // 5 tentativas de login por 15 minutos

// Função para gerar tokens
const generateTokens = (user) => {
  const payload = {
    userId: user._id,
    email: user.email,
    role: user.role
  };
  
  const accessToken = jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN || '24h'
  });
  
  const refreshToken = jwt.sign(payload, process.env.REFRESH_TOKEN_SECRET, {
    expiresIn: process.env.REFRESH_TOKEN_EXPIRES_IN || '7d'
  });
  
  return { accessToken, refreshToken };
};

// Validações
const registerValidation = [
  body('email').isEmail().normalizeEmail().withMessage('Email inválido'),
  body('name').trim().isLength({ min: 2, max: 100 }).withMessage('Nome deve ter entre 2 e 100 caracteres'),
  body('password').isLength({ min: 8 }).withMessage('Senha deve ter pelo menos 8 caracteres'),
  body('role').optional().isIn(['ADMIN', 'CUSTOMER', 'SALES']).withMessage('Papel inválido')
];

const loginValidation = [
  body('email').isEmail().normalizeEmail().withMessage('Email inválido'),
  body('password').notEmpty().withMessage('Senha é obrigatória')
];

const updateProfileValidation = [
  body('email').optional().isEmail().normalizeEmail().withMessage('Email inválido'),
  body('name').optional().trim().isLength({ min: 2, max: 100 }).withMessage('Nome deve ter entre 2 e 100 caracteres')
];

// POST /auth/register
router.post('/register', authLimiter, registerValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { email, name, password, role = 'CUSTOMER' } = req.body;
    
    // Verificar se usuário já existe
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({
        error: 'Usuário já existe'
      });
    }
    
    // Criar usuário
    const user = new User({
      email,
      name,
      password,
      role,
      status: 'ACTIVE'
    });
    
    await user.save();
    
    // Gerar tokens
    const { accessToken, refreshToken } = generateTokens(user);
    
    logger.info(`Usuário registrado: ${email}`);
    
    res.status(201).json({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      expires_in: 86400, // 24 horas
      user: user.toResponse()
    });
    
  } catch (error) {
    logger.error('Erro no registro:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /auth/login
router.post('/login', loginLimiter, loginValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { email, password } = req.body;
    
    // Buscar usuário
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({
        error: 'Credenciais inválidas'
      });
    }
    
    if (user.status !== 'ACTIVE') {
      return res.status(401).json({
        error: 'Usuário inativo'
      });
    }
    
    // Verificar senha
    const isValidPassword = await user.comparePassword(password);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Credenciais inválidas'
      });
    }
    
    // Atualizar último login
    user.lastLogin = new Date();
    await user.save();
    
    // Gerar tokens
    const { accessToken, refreshToken } = generateTokens(user);
    
    logger.info(`Login realizado: ${email}`);
    
    res.json({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      expires_in: 86400,
      user: user.toResponse()
    });
    
  } catch (error) {
    logger.error('Erro no login:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /auth/refresh
router.post('/refresh', authLimiter, async (req, res) => {
  try {
    const { refresh_token } = req.body;
    
    if (!refresh_token) {
      return res.status(400).json({
        error: 'Refresh token necessário'
      });
    }
    
    // Verificar refresh token
    const decoded = jwt.verify(refresh_token, process.env.REFRESH_TOKEN_SECRET);
    
    // Buscar usuário
    const user = await User.findById(decoded.userId);
    if (!user || user.status !== 'ACTIVE') {
      return res.status(401).json({
        error: 'Usuário não encontrado ou inativo'
      });
    }
    
    // Gerar novos tokens
    const { accessToken, refreshToken } = generateTokens(user);
    
    res.json({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      expires_in: 86400,
      user: user.toResponse()
    });
    
  } catch (error) {
    logger.error('Erro no refresh:', error);
    
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Refresh token inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /auth/validate
router.get('/validate', async (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({
        valid: false,
        error: 'Token necessário'
      });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);
    
    if (!user || user.status !== 'ACTIVE') {
      return res.status(401).json({
        valid: false,
        error: 'Token inválido ou usuário inativo'
      });
    }
    
    res.json({
      valid: true,
      user: user.toResponse(),
      expires_at: new Date(decoded.exp * 1000)
    });
  } catch (error) {
    logger.error('Erro na validação:', error);
    
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return res.status(401).json({
        valid: false,
        error: 'Token inválido ou expirado'
      });
    }
    
    res.status(500).json({
      valid: false,
      error: 'Erro interno do servidor'
    });
  }
});

// POST /auth/validate
router.post('/validate', async (req, res) => {
  try {
    const { token } = req.body;
    
    if (!token) {
      return res.status(400).json({
        error: 'Token necessário'
      });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);
    
    if (!user || user.status !== 'ACTIVE') {
      return res.json({
        valid: false,
        user: null
      });
    }
    
    res.json({
      valid: true,
      user: user.toResponse(),
      expires_at: new Date(decoded.exp * 1000)
    });
    
  } catch (error) {
    res.json({
      valid: false,
      user: null
    });
  }
});

// POST /auth/logout
router.post('/logout', authenticateToken, async (req, res) => {
  try {
    // Em uma implementação completa, você adicionaria o token a uma blacklist
    logger.info(`Logout realizado: ${req.user.email}`);
    
    res.json({
      message: 'Logout realizado com sucesso'
    });
  } catch (error) {
    logger.error('Erro no logout:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /auth/profile
router.get('/profile', authenticateToken, async (req, res) => {
  try {
    res.json(req.user.toResponse());
  } catch (error) {
    logger.error('Erro ao obter perfil:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /auth/profile
router.put('/profile', authenticateToken, updateProfileValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { email, name } = req.body;
    const user = req.user;
    
    // Verificar se email já existe (se diferente do atual)
    if (email && email !== user.email) {
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(409).json({
          error: 'Email já está em uso'
        });
      }
      user.email = email;
    }
    
    if (name) {
      user.name = name;
    }
    
    await user.save();
    
    logger.info(`Perfil atualizado: ${user.email}`);
    
    res.json(user.toResponse());
    
  } catch (error) {
    logger.error('Erro ao atualizar perfil:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /auth/users (admin only)
router.get('/users', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { skip = 0, limit = 100 } = req.query;
    
    const users = await User.find()
      .skip(parseInt(skip))
      .limit(parseInt(limit))
      .sort({ createdAt: -1 });
    
    const response = users.map(user => user.toResponse());
    
    res.json(response);
    
  } catch (error) {
    logger.error('Erro ao listar usuários:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /auth/users/:id
router.get('/users/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    
    // Usuário pode ver apenas seus próprios dados ou admin pode ver todos
    if (req.user.role !== 'ADMIN' && req.user._id.toString() !== id) {
      return res.status(403).json({
        error: 'Acesso negado'
      });
    }
    
    const user = await User.findById(id);
    if (!user) {
      return res.status(404).json({
        error: 'Usuário não encontrado'
      });
    }
    
    res.json(user.toResponse());
    
  } catch (error) {
    logger.error('Erro ao obter usuário:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /auth/users/:id (admin only)
router.put('/users/:id', authenticateToken, requireAdmin, updateProfileValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { id } = req.params;
    const { email, name, role, status } = req.body;
    
    const user = await User.findById(id);
    if (!user) {
      return res.status(404).json({
        error: 'Usuário não encontrado'
      });
    }
    
    // Verificar se email já existe (se diferente do atual)
    if (email && email !== user.email) {
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(409).json({
          error: 'Email já está em uso'
        });
      }
      user.email = email;
    }
    
    if (name) user.name = name;
    if (role) user.role = role;
    if (status) user.status = status;
    
    await user.save();
    
    logger.info(`Usuário atualizado por admin: ${user.email}`);
    
    res.json(user.toResponse());
    
  } catch (error) {
    logger.error('Erro ao atualizar usuário:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// DELETE /auth/users/:id (admin only)
router.delete('/users/:id', authenticateToken, requireAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const user = await User.findById(id);
    if (!user) {
      return res.status(404).json({
        error: 'Usuário não encontrado'
      });
    }
    
    await User.findByIdAndDelete(id);
    
    logger.info(`Usuário deletado por admin: ${user.email}`);
    
    res.status(204).send();
    
  } catch (error) {
    logger.error('Erro ao deletar usuário:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /auth/health
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'auth-service'
  });
});

module.exports = router;
