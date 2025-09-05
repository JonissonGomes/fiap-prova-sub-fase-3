const express = require('express');
const { body, query, validationResult } = require('express-validator');
const Sale = require('../models/Sale');
const Vehicle = require('../models/Vehicle');
const Customer = require('../models/Customer');
const { authenticateToken, requireSalesOrAdmin } = require('../middleware/auth');
const { logger } = require('../utils/logger');

const router = express.Router();

// Validações
const createSaleValidation = [
  body('customer_id').isMongoId().withMessage('ID do cliente inválido'),
  body('vehicle_id').isMongoId().withMessage('ID do veículo inválido'),
  body('payment_method').isIn(['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX']).withMessage('Método de pagamento inválido'),
  body('discount').optional().isFloat({ min: 0 }).withMessage('Desconto deve ser maior ou igual a zero'),
  body('notes').optional().isLength({ max: 500 }).withMessage('Notas muito longas')
];

const updateSaleValidation = [
  body('status').optional().isIn(['PENDENTE', 'PAGO', 'CANCELADO']).withMessage('Status inválido'),
  body('payment_method').optional().isIn(['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX']).withMessage('Método de pagamento inválido'),
  body('discount').optional().isFloat({ min: 0 }).withMessage('Desconto deve ser maior ou igual a zero'),
  body('notes').optional().isLength({ max: 500 }).withMessage('Notas muito longas')
];

const purchaseValidation = [
  body('customer_id').isMongoId().withMessage('ID do cliente inválido'),
  body('vehicle_id').isMongoId().withMessage('ID do veículo inválido'),
  body('payment_method').isIn(['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX']).withMessage('Método de pagamento inválido'),
  body('notes').optional().isLength({ max: 500 }).withMessage('Notas muito longas')
];

const listSalesValidation = [
  query('skip').optional().isInt({ min: 0 }).withMessage('Skip deve ser um número não negativo'),
  query('limit').optional().isInt({ min: 1, max: 1000 }).withMessage('Limit deve estar entre 1 e 1000'),
  query('status').optional().isIn(['PENDENTE', 'PAGO', 'CANCELADO']).withMessage('Status inválido'),
  query('customer_id').optional().isMongoId().withMessage('ID do cliente inválido'),
  query('vehicle_id').optional().isMongoId().withMessage('ID do veículo inválido')
];

// GET /sales
router.get('/', authenticateToken, requireSalesOrAdmin, listSalesValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Parâmetros inválidos',
        details: errors.array()
      });
    }
    
    const { skip = 0, limit = 100, status, customer_id, vehicle_id } = req.query;
    
    const filters = {};
    if (status) filters.status = status;
    if (customer_id) filters.customerId = customer_id;
    if (vehicle_id) filters.vehicleId = vehicle_id;
    
    const sales = await Sale.find(filters)
      .populate('customerId', 'name email cpf')
      .populate('vehicleId', 'brand model year color price status')
      .populate('sellerId', 'name email role')
      .sort({ createdAt: -1 })
      .skip(parseInt(skip))
      .limit(parseInt(limit));
    
    res.json(sales);
    
  } catch (error) {
    logger.error('Erro ao listar vendas:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /sales/:id
router.get('/:id', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const sale = await Sale.findById(id)
      .populate('customerId', 'name email cpf phone address city state zipCode')
      .populate('vehicleId', 'brand model year color price status')
      .populate('sellerId', 'name email role');
    
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    res.json(sale);
    
  } catch (error) {
    logger.error('Erro ao obter venda:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /sales
router.post('/', authenticateToken, requireSalesOrAdmin, createSaleValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { customer_id, vehicle_id, payment_method, discount = 0, notes } = req.body;
    
    // Verificar se cliente existe
    const customer = await Customer.findById(customer_id);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    // Verificar se veículo existe e está disponível
    const vehicle = await Vehicle.findById(vehicle_id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    if (vehicle.status !== 'DISPONÍVEL') {
      return res.status(400).json({
        error: 'Veículo não está disponível para venda'
      });
    }
    
    // Criar venda
    const sale = new Sale({
      customerId: customer_id,
      vehicleId: vehicle_id,
      sellerId: req.user._id,
      totalAmount: vehicle.price,
      paymentMethod: payment_method,
      discount,
      notes
    });
    
    await sale.save();
    
    // Marcar veículo como reservado
    vehicle.status = 'RESERVADO';
    await vehicle.save();
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('vehicleId', 'brand model year color price');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Venda criada: ${vehicle.brand} ${vehicle.model} para ${customer.name} por ${req.user.email}`);
    
    res.status(201).json(sale);
    
  } catch (error) {
    logger.error('Erro ao criar venda:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// POST /sales/purchase (endpoint simplificado para compra)
router.post('/purchase', authenticateToken, requireSalesOrAdmin, purchaseValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { customer_id, vehicle_id, payment_method, notes } = req.body;
    
    // Verificar se cliente existe
    const customer = await Customer.findById(customer_id);
    if (!customer) {
      return res.status(404).json({
        error: 'Cliente não encontrado'
      });
    }
    
    // Verificar se veículo existe e está disponível
    const vehicle = await Vehicle.findById(vehicle_id);
    if (!vehicle) {
      return res.status(404).json({
        error: 'Veículo não encontrado'
      });
    }
    
    if (vehicle.status !== 'DISPONÍVEL') {
      return res.status(400).json({
        error: 'Veículo não está disponível para compra'
      });
    }
    
    // Criar venda
    const sale = new Sale({
      customerId: customer_id,
      vehicleId: vehicle_id,
      sellerId: req.user._id,
      totalAmount: vehicle.price,
      paymentMethod: payment_method,
      status: 'PENDENTE',
      notes
    });
    
    await sale.save();
    
    // Marcar veículo como reservado
    vehicle.status = 'RESERVADO';
    await vehicle.save();
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('vehicleId', 'brand model year color price');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Compra realizada: ${vehicle.brand} ${vehicle.model} para ${customer.name} por ${req.user.email}`);
    
    res.status(201).json(sale);
    
  } catch (error) {
    logger.error('Erro ao realizar compra:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /sales/:id
router.put('/:id', authenticateToken, requireSalesOrAdmin, updateSaleValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Dados inválidos',
        details: errors.array()
      });
    }
    
    const { id } = req.params;
    const { status, payment_method, discount, notes } = req.body;
    
    const sale = await Sale.findById(id);
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    // Atualizar campos
    if (status) sale.status = status;
    if (payment_method) sale.paymentMethod = payment_method;
    if (discount !== undefined) sale.discount = discount;
    if (notes) sale.notes = notes;
    
    await sale.save();
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('vehicleId', 'brand model year color price');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Venda atualizada: ${id} por ${req.user.email}`);
    
    res.json(sale);
    
  } catch (error) {
    logger.error('Erro ao atualizar venda:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PUT /sales/:id/status
router.put('/:id/status', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    const { status, notes } = req.body;
    
    if (!status) {
      return res.status(400).json({
        error: 'Status é obrigatório'
      });
    }
    
    if (!['PENDENTE', 'PAGO', 'CANCELADO'].includes(status)) {
      return res.status(400).json({
        error: 'Status inválido. Valores aceitos: PENDENTE, PAGO, CANCELADO'
      });
    }
    
    const sale = await Sale.findById(id).populate('vehicleId');
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    const oldStatus = sale.status;
    sale.status = status;
    
    if (notes) {
      sale.notes = sale.notes ? `${sale.notes}\n${notes}` : notes;
    }
    
    // Atualizar status do veículo baseado no status da venda
    if (sale.vehicleId) {
      if (status === 'PAGO') {
        sale.vehicleId.status = 'VENDIDO';
        sale.paymentDate = new Date();
      } else if (status === 'CANCELADO' && oldStatus !== 'CANCELADO') {
        sale.vehicleId.status = 'DISPONÍVEL';
      }
      
      await sale.vehicleId.save();
    }
    
    await sale.save();
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Status da venda alterado: ${id} de ${oldStatus} para ${status} por ${req.user.email}`);
    
    res.json(sale);
    
  } catch (error) {
    logger.error('Erro ao alterar status da venda:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PATCH /sales/:id/payment/confirm
router.patch('/:id/payment/confirm', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const sale = await Sale.findById(id).populate('vehicleId');
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    await sale.markAsPaid();
    
    // Marcar veículo como vendido
    if (sale.vehicleId) {
      sale.vehicleId.status = 'VENDIDO';
      await sale.vehicleId.save();
    }
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Pagamento confirmado para venda: ${id} por ${req.user.email}`);
    
    res.json(sale);
    
  } catch (error) {
    logger.error('Erro ao confirmar pagamento:', error);
    
    if (error.message.includes('já está') || error.message.includes('cancelada')) {
      return res.status(400).json({
        error: error.message
      });
    }
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// PATCH /sales/:id/mark-as-canceled
router.patch('/:id/mark-as-canceled', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    const { reason } = req.body;
    
    const sale = await Sale.findById(id).populate('vehicleId');
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    await sale.cancel(reason);
    
    // Marcar veículo como disponível novamente
    if (sale.vehicleId) {
      sale.vehicleId.status = 'DISPONÍVEL';
      await sale.vehicleId.save();
    }
    
    // Popular dados para resposta
    await sale.populate('customerId', 'name email cpf');
    await sale.populate('sellerId', 'name email');
    
    logger.info(`Venda cancelada: ${id} por ${req.user.email} - Motivo: ${reason || 'Não informado'}`);
    
    res.json(sale);
    
  } catch (error) {
    logger.error('Erro ao cancelar venda:', error);
    
    if (error.message.includes('já está') || error.message.includes('paga')) {
      return res.status(400).json({
        error: error.message
      });
    }
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// DELETE /sales/:id
router.delete('/:id', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { id } = req.params;
    
    const sale = await Sale.findById(id).populate('vehicleId');
    if (!sale) {
      return res.status(404).json({
        error: 'Venda não encontrada'
      });
    }
    
    // Não permite deletar vendas pagas
    if (sale.status === 'PAGO') {
      return res.status(400).json({
        error: 'Não é possível deletar uma venda paga'
      });
    }
    
    // Liberar veículo se estava reservado
    if (sale.vehicleId && sale.vehicleId.status === 'RESERVADO') {
      sale.vehicleId.status = 'DISPONÍVEL';
      await sale.vehicleId.save();
    }
    
    await Sale.findByIdAndDelete(id);
    
    logger.info(`Venda deletada: ${id} por ${req.user.email}`);
    
    res.status(204).send();
    
  } catch (error) {
    logger.error('Erro ao deletar venda:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        error: 'ID da venda inválido'
      });
    }
    
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /sales/stats/summary
router.get('/stats/summary', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { start_date, end_date } = req.query;
    
    const stats = await Sale.getSalesStats(start_date, end_date);
    
    if (stats.length === 0) {
      return res.json({
        totalSales: 0,
        totalRevenue: 0,
        stats: []
      });
    }
    
    res.json(stats[0]);
    
  } catch (error) {
    logger.error('Erro ao obter estatísticas de vendas:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

// GET /sales/stats/monthly/:year
router.get('/stats/monthly/:year', authenticateToken, requireSalesOrAdmin, async (req, res) => {
  try {
    const { year } = req.params;
    
    if (!year || isNaN(year)) {
      return res.status(400).json({
        error: 'Ano inválido'
      });
    }
    
    const stats = await Sale.getMonthlyStats(parseInt(year));
    
    res.json(stats);
    
  } catch (error) {
    logger.error('Erro ao obter estatísticas mensais:', error);
    res.status(500).json({
      error: 'Erro interno do servidor'
    });
  }
});

module.exports = router;
