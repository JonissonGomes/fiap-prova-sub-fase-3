const express = require('express');
const { body, query, validationResult } = require('express-validator');
const Customer = require('../models/Customer');
const { authenticateToken, requireSalesOrAdmin } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Validações
const createCustomerValidation = [
  body('name').trim().isLength({ min: 2, max: 100 }).withMessage('Nome deve ter entre 2 e 100 caracteres'),
  body('email').isEmail().normalizeEmail().withMessage('Email inválido'),
  body('phone').custom((value) => {
    const phone = value.replace(/[^\d]/g, '');
    if (phone.length < 10 || phone.length > 11) {
      throw new Error('Telefone deve ter 10 ou 11 dígitos');
    }
    return true;
  }).withMessage('Telefone inválido'),
  body('cpf').isLength({ min: 11, max: 11 }).withMessage('CPF deve ter 11 dígitos'),
  body('address').optional().isLength({ max: 200 }).withMessage('Endereço muito longo'),
  body('city').optional().isLength({ max: 100 }).withMessage('Cidade muito longa'),
  body('state').optional().isLength({ min: 2, max: 2 }).withMessage('Estado deve ter 2 caracteres'),
  body('zip_code').optional().isLength({ max: 10 }).withMessage('CEP muito longo')
];

const updateCustomerValidation = [
  body('name').optional().trim().isLength({ min: 2, max: 100 }).withMessage('Nome deve ter entre 2 e 100 caracteres'),
  body('email').optional().isEmail().normalizeEmail().withMessage('Email inválido'),
  body('phone').optional().custom((value) => {
    if (!value) return true;
    const phone = value.replace(/[^\d]/g, '');
    if (phone.length < 10 || phone.length > 11) {
      throw new Error('Telefone deve ter 10 ou 11 dígitos');
    }
    return true;
  }).withMessage('Telefone inválido'),
  body('address').optional().isLength({ max: 200 }).withMessage('Endereço muito longo'),
  body('city').optional().isLength({ max: 100 }).withMessage('Cidade muito longa'),
  body('state').optional().isLength({ min: 2, max: 2 }).withMessage('Estado deve ter 2 caracteres'),
  body('zip_code').optional().isLength({ max: 10 }).withMessage('CEP muito longo')
];

const listCustomersValidation = [
  query('skip').optional().isInt({ min: 0 }).withMessage('Skip deve ser um número não negativo'),
  query('limit').optional().isInt({ min: 1, max: 1000 }).withMessage('Limit deve estar entre 1 e 1000'),
  query('active').optional().isBoolean().withMessage('Active deve ser true ou false')
];

// GET /customers
router.get('/', authenticateToken, requireSalesOrAdmin, listCustomersValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Parâmetros inválidos',
        details: errors.array()
      });
    }
    
    const { skip = 0, limit = 100, active } = req.query;
    
    const filters = {};
    if (active !== undefined) {
      filters.active = active === 'true';
    }
    
    const customers = await Customer.find(filters)
      .sort({ createdAt: -1 })
      .skip(parseInt(skip))
      .limit(parseInt(limit));
    
    res.json(customers);
    
  } catch (error) {
    logger.error('Erro ao listar clientes:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /customers/:id
router.get('/:id', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const customer = await Customer.findById(id);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    res.json(customer);
    
  } catch (error) {
    logger.error('Erro ao obter cliente:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do cliente inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /customers/cpf/:cpf
router.get('/cpf/:cpf', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { cpf } = req.params;
    
    const customer = await Customer.findByCPF(cpf);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    res.json(customer);
    
  } catch (error) {
    logger.error('Erro ao buscar cliente por CPF:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /customers/email/:email
router.get('/email/:email', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { email } = req.params;
    
    const customer = await Customer.findByEmail(email);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    res.json(customer);
    
  } catch (error) {
    logger.error('Erro ao buscar cliente por email:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /customers/search
router.get('/search', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { q } = req.query;
    
    if (!q) {
      return res.status(400).json({
        error: 'Parâmetro de busca (q) é obrigatório'
      });
    }
    
    const customers = await Customer.searchCustomers(q);
    
    res.json(customers);
    
  } catch (error) {
    logger.error('Erro ao buscar clientes:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /customers/search (busca avançada)
router.post('/search', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { cpf, email, phone, name } = req.body;
    
    const filters = { active: true };
    
    if (cpf) {
      filters.cpf = cpf.replace(/[^\d]/g, '');
    }
    
    if (email) {
      filters.email = email.toLowerCase();
    }
    
    if (phone) {
      filters.phone = phone.replace(/[^\d]/g, '');
    }
    
    if (name) {
      filters.name = new RegExp(name, 'i');
    }
    
    const customers = await Customer.find(filters).sort({ createdAt: -1 });
    
    res.json(customers);
    
  } catch (error) {
    logger.error('Erro na busca avançada de clientes:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /customers
router.post('/', authenticateToken, requireSalesOrAdmin, createCustomerValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { name, email, phone, cpf, address, city, state, zip_code } = req.body;
    
    // Verificar se cliente já existe
    const existingByEmail = await Customer.findByEmail(email);
    if (existingByEmail) {
      return res.status(409).json({
        error: 'Cliente com este email já existe'
      });
    }
    
    const existingByCPF = await Customer.findByCPF(cpf);
    if (existingByCPF) {
      return res.status(409).json({
        error: 'Cliente com este CPF já existe'
      });
    }
    
    const customer = new Customer({
      name,
      email,
      phone,
      cpf,
      address,
      city,
      state,
      zipCode: zip_code
    });
    
    await customer.save();
    
    logger.info(`Cliente criado: ${name} (${email}) por ${req.user.email}`);
    
    res.status(201).json(customer);
    
  } catch (error) {
    logger.error('Erro ao criar cliente:', error);
    
    if (error.code === 11000) {
      return res.status(409).json({
        error: 'Cliente já existe'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /customers/:id
router.put('/:id', authenticateToken, requireSalesOrAdmin, updateCustomerValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { id } = req.params;
    const { name, email, phone, address, city, state, zip_code } = req.body;
    
    const customer = await Customer.findById(id);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    // Verificar se email já existe (se diferente do atual)
    if (email && email !== customer.email) {
      const existingByEmail = await Customer.findByEmail(email);
      if (existingByEmail) {
        return res.status(409).json({
          error: 'Email já está em uso'
        });
      }
      customer.email = email;
    }
    
    // Atualizar campos
    if (name) customer.name = name;
    if (phone) customer.phone = phone;
    if (address) customer.address = address;
    if (city) customer.city = city;
    if (state) customer.state = state;
    if (zip_code) customer.zipCode = zip_code;
    
    await customer.save();
    
    logger.info(`Cliente atualizado: ${customer.name} por ${req.user.email}`);
    
    res.json(customer);
    
  } catch (error) {
    logger.error('Erro ao atualizar cliente:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do cliente inválido'
      });
    }
    
    if (error.code === 11000) {
      return res.status(409).json({
        error: 'Email já está em uso'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// DELETE /customers/:id (soft delete)
router.delete('/:id', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const customer = await Customer.findById(id);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    await customer.softDelete();
    
    logger.info(`Cliente deletado (soft): ${customer.name} por ${req.user.email}`);
    
    res.json({
      message: 'Cliente deletado com sucesso'
    });
    
  } catch (error) {
    logger.error('Erro ao deletar cliente:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do cliente inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /customers/stats/summary
router.get('/stats/summary', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const stats = await Customer.getStats();
    
    if (stats.length === 0) {
      return res.json({
        total_customers: 0,
        active_customers: 0,
        inactive_customers: 0,
        customers_this_month: 0
      });
    }
    
    res.json(stats[0]);
    
  } catch (error) {
    logger.error('Erro ao obter estatísticas de clientes:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

module.exports = router;
