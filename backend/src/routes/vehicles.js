const express = require('express');
const { body, query, validationResult } = require('express-validator');
const Vehicle = require('../models/Vehicle');
const { authenticateToken, requireSalesOrAdmin, optionalAuth } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Validações
const createVehicleValidation = [
  body('brand').trim().notEmpty().withMessage('Marca é obrigatória'),
  body('model').trim().notEmpty().withMessage('Modelo é obrigatório'),
  body('year').isInt({ min: 1900, max: new Date().getFullYear() + 1 }).withMessage('Ano inválido'),
  body('color').trim().notEmpty().withMessage('Cor é obrigatória'),
  body('price').isFloat({ min: 0 }).withMessage('Preço deve ser maior que zero')
];

const updateVehicleValidation = [
  body('brand').optional().trim().notEmpty().withMessage('Marca não pode estar vazia'),
  body('model').optional().trim().notEmpty().withMessage('Modelo não pode estar vazio'),
  body('year').optional().isInt({ min: 1900, max: new Date().getFullYear() + 1 }).withMessage('Ano inválido'),
  body('color').optional().trim().notEmpty().withMessage('Cor não pode estar vazia'),
  body('price').optional().isFloat({ min: 0 }).withMessage('Preço deve ser maior que zero')
];

const listVehiclesValidation = [
  query('skip').optional().isInt({ min: 0 }).withMessage('Skip deve ser um número não negativo'),
  query('limit').optional().isInt({ min: 1, max: 1000 }).withMessage('Limit deve estar entre 1 e 1000'),
  query('status').optional().isIn(['DISPONÍVEL', 'VENDIDO', 'RESERVADO']).withMessage('Status inválido'),
  query('min_price').optional().isFloat({ min: 0 }).withMessage('Preço mínimo inválido'),
  query('max_price').optional().isFloat({ min: 0 }).withMessage('Preço máximo inválido'),
  query('year').optional().isInt({ min: 1900 }).withMessage('Ano inválido')
];

// GET /vehicles
router.get('/', optionalAuth, listVehiclesValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Parâmetros inválidos',
        details: errors.array()
      });
    }
    
    const {
      skip = 0,
      limit = 100,
      status,
      brand,
      model,
      min_price,
      max_price,
      year,
      sort = 'createdAt',
      order = 'desc'
    } = req.query;
    
    // Construir filtros
    const filters = {};
    if (status) filters.status = status;
    if (brand) filters.brand = new RegExp(brand, 'i');
    if (model) filters.model = new RegExp(model, 'i');
    if (year) filters.year = parseInt(year);
    
    if (min_price || max_price) {
      filters.price = {};
      if (min_price) filters.price.$gte = parseFloat(min_price);
      if (max_price) filters.price.$lte = parseFloat(max_price);
    }
    
    // Construir ordenação
    const sortOrder = order === 'desc' ? -1 : 1;
    const sortObj = { [sort]: sortOrder };
    
    const vehicles = await Vehicle.find(filters)
      .sort(sortObj)
      .skip(parseInt(skip))
      .limit(parseInt(limit));
    
    res.json(vehicles);
    
  } catch (error) {
    logger.error('Erro ao listar veículos:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /vehicles/available
router.get('/available', optionalAuth, async (req, res) => {
  try {
    const vehicles = await Vehicle.findAvailable().sort({ createdAt: -1 });
    res.json(vehicles);
  } catch (error) {
    logger.error('Erro ao listar veículos disponíveis:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /vehicles/reserved
router.get('/reserved', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const vehicles = await Vehicle.findByStatus('RESERVADO').sort({ createdAt: -1 });
    res.json(vehicles);
  } catch (error) {
    logger.error('Erro ao listar veículos reservados:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /vehicles/sold
router.get('/sold', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const vehicles = await Vehicle.findByStatus('VENDIDO').sort({ createdAt: -1 });
    res.json(vehicles);
  } catch (error) {
    logger.error('Erro ao listar veículos vendidos:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /vehicles/:id
router.get('/:id', optionalAuth, async (req, res) => {
  try {
    const { id } = req.params;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao obter veículo:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /vehicles
router.post('/', authenticateToken, requireSalesOrAdmin, createVehicleValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { brand, model, year, color, price, status = 'DISPONÍVEL' } = req.body;
    
    const vehicle = new Vehicle({
      brand,
      model,
      year,
      color,
      price,
      status
    });
    
    await vehicle.save();
    
    logger.info(`Veículo criado: ${brand} ${model} ${year} por ${req.user.email}`);
    
    res.status(201).json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao criar veículo:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /vehicles/:id
router.put('/:id', authenticateToken, requireSalesOrAdmin, updateVehicleValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { id } = req.params;
    const { brand, model, year, color, price } = req.body;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    // Não permite alterar veículos vendidos
    if (vehicle.status === 'VENDIDO') {
      return res.status(400).json({
        error: 'Não é possível alterar um veículo vendido'
      });
    }
    
    // Atualizar campos
    if (brand) vehicle.brand = brand;
    if (model) vehicle.model = model;
    if (year) vehicle.year = year;
    if (color) vehicle.color = color;
    if (price) vehicle.price = price;
    
    await vehicle.save();
    
    logger.info(`Veículo atualizado: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao atualizar veículo:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// DELETE /vehicles/:id
router.delete('/:id', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    // Não permite deletar veículos vendidos
    if (vehicle.status === 'VENDIDO') {
      return res.status(400).json({
        error: 'Não é possível deletar um veículo vendido'
      });
    }
    
    await Vehicle.findByIdAndDelete(id);
    
    logger.info(`Veículo deletado: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.status(204).send();
    
  } catch (error) {
    logger.error('Erro ao deletar veículo:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /vehicles/:id/mark-as-available
router.post('/:id/mark-as-available', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    await vehicle.markAsAvailable();
    
    logger.info(`Veículo marcado como disponível: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao marcar veículo como disponível:', error);
    
    if (error.message.includes('já está') || error.message.includes('não pode ser')) {
      return res.status(400).json({
        error: error.message
      });
    }
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /vehicles/:id/mark-as-reserved
router.post('/:id/mark-as-reserved', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    await vehicle.markAsReserved();
    
    logger.info(`Veículo marcado como reservado: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao marcar veículo como reservado:', error);
    
    if (error.message.includes('já está') || error.message.includes('não está')) {
      return res.status(400).json({
        error: error.message
      });
    }
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /vehicles/:id/mark-as-sold
router.post('/:id/mark-as-sold', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    await vehicle.markAsSold();
    
    logger.info(`Veículo marcado como vendido: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao marcar veículo como vendido:', error);
    
    if (error.message.includes('já está') || error.message.includes('não está')) {
      return res.status(400).json({
        error: error.message
      });
    }
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PATCH /vehicles/:id/status
router.patch('/:id/status', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    
    if (!status) {
      return res.status(400).json({
        error: 'Status é obrigatório'
      });
    }
    
    if (!['DISPONÍVEL', 'RESERVADO', 'VENDIDO'].includes(status)) {
      return res.status(400).json({
        error: 'Status inválido. Valores aceitos: DISPONÍVEL, RESERVADO, VENDIDO'
      });
    }
    
    const vehicle = await Vehicle.findById(id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    vehicle.status = status;
    await vehicle.save();
    
    logger.info(`Status do veículo alterado para ${status}: ${vehicle.brand} ${vehicle.model} por ${req.user.email}`);
    
    res.json(vehicle);
    
  } catch (error) {
    logger.error('Erro ao alterar status do veículo:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /vehicles/sale-status (webhook do sales service)
router.post('/sale-status', async (req, res) => {
  try {
    const { vehicle_id, status } = req.body;
    
    if (!vehicle_id || !status) {
      return res.status(400).json({
        error: 'vehicle_id e status são obrigatórios'
      });
    }
    
    // Mapear status do sales-service para status do veículo
    const statusMapping = {
      'PAGO': 'VENDIDO',
      'PENDENTE': 'RESERVADO',
      'CANCELADO': 'DISPONÍVEL'
    };
    
    const vehicleStatus = statusMapping[status];
    if (!vehicleStatus) {
      return res.status(400).json({
        error: 'Status inválido. Valores aceitos: PAGO, PENDENTE, CANCELADO'
      });
    }
    
    const vehicle = await Vehicle.findById(vehicle_id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    vehicle.status = vehicleStatus;
    await vehicle.save();
    
    logger.info(`Status do veículo atualizado via webhook: ${vehicle.brand} ${vehicle.model} -> ${vehicleStatus}`);
    
    res.json({
      message: 'Status do veículo atualizado com sucesso',
      vehicle_id,
      new_status: vehicleStatus,
      sale_status: status
    });
    
  } catch (error) {
    logger.error('Erro no webhook de status:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID do veículo inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

module.exports = router;
