const mongoose = require('mongoose');

const vehicleSchema = new mongoose.Schema({
  brand: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  model: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  year: {
    type: Number,
    required: true,
    min: 1900,
    max: new Date().getFullYear() + 1
  },
  color: {
    type: String,
    required: true,
    trim: true,
    maxlength: 30
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  status: {
    type: String,
    enum: ['DISPONÍVEL', 'VENDIDO', 'RESERVADO'],
    default: 'DISPONÍVEL'
  }
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      ret.id = ret._id;
      delete ret._id;
      delete ret.__v;
      return ret;
    }
  }
});

// Índices
vehicleSchema.index({ brand: 1 });
vehicleSchema.index({ model: 1 });
vehicleSchema.index({ year: 1 });
vehicleSchema.index({ status: 1 });
vehicleSchema.index({ price: 1 });
vehicleSchema.index({ brand: 1, model: 1 });

// Validações customizadas
vehicleSchema.pre('save', function(next) {
  if (this.year < 1900 || this.year > new Date().getFullYear() + 1) {
    return next(new Error('Ano do veículo inválido'));
  }
  
  if (this.price <= 0) {
    return next(new Error('Preço do veículo deve ser maior que zero'));
  }
  
  next();
});

// Métodos de instância
vehicleSchema.methods.markAsSold = function() {
  if (this.status === 'VENDIDO') {
    throw new Error('Veículo já está vendido');
  }
  if (!['DISPONÍVEL', 'RESERVADO'].includes(this.status)) {
    throw new Error('Veículo não está disponível para venda');
  }
  
  this.status = 'VENDIDO';
  return this.save();
};

vehicleSchema.methods.markAsReserved = function() {
  if (this.status === 'RESERVADO') {
    throw new Error('Veículo já está reservado');
  }
  if (this.status !== 'DISPONÍVEL') {
    throw new Error('Veículo não está disponível para reserva');
  }
  
  this.status = 'RESERVADO';
  return this.save();
};

vehicleSchema.methods.markAsAvailable = function() {
  if (this.status === 'DISPONÍVEL') {
    throw new Error('Veículo já está disponível');
  }
  if (this.status === 'VENDIDO') {
    throw new Error('Veículo vendido não pode ser marcado como disponível');
  }
  
  this.status = 'DISPONÍVEL';
  return this.save();
};

// Métodos estáticos
vehicleSchema.statics.findAvailable = function() {
  return this.find({ status: 'DISPONÍVEL' });
};

vehicleSchema.statics.findByStatus = function(status) {
  return this.find({ status });
};

vehicleSchema.statics.searchVehicles = function(filters) {
  const query = {};
  
  if (filters.brand) {
    query.brand = new RegExp(filters.brand, 'i');
  }
  
  if (filters.model) {
    query.model = new RegExp(filters.model, 'i');
  }
  
  if (filters.status) {
    query.status = filters.status;
  }
  
  if (filters.minPrice || filters.maxPrice) {
    query.price = {};
    if (filters.minPrice) query.price.$gte = filters.minPrice;
    if (filters.maxPrice) query.price.$lte = filters.maxPrice;
  }
  
  if (filters.year) {
    query.year = filters.year;
  }
  
  return this.find(query);
};

module.exports = mongoose.model('Vehicle', vehicleSchema);
