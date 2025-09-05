const mongoose = require('mongoose');

const saleSchema = new mongoose.Schema({
  customerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Customer',
    required: true
  },
  vehicleId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Vehicle',
    required: true
  },
  sellerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  saleDate: {
    type: Date,
    default: Date.now
  },
  totalAmount: {
    type: Number,
    required: true,
    min: 0
  },
  status: {
    type: String,
    enum: ['PENDENTE', 'PAGO', 'CANCELADO'],
    default: 'PENDENTE'
  },
  paymentMethod: {
    type: String,
    enum: ['DINHEIRO', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'FINANCIAMENTO', 'PIX'],
    required: true
  },
  notes: {
    type: String,
    maxlength: 500,
    trim: true
  },
  paymentDate: {
    type: Date,
    default: null
  },
  discount: {
    type: Number,
    default: 0,
    min: 0
  },
  finalAmount: {
    type: Number,
    required: true,
    min: 0
  }
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      ret.id = ret._id;
      ret.customer_id = ret.customerId;
      ret.vehicle_id = ret.vehicleId;
      ret.seller_id = ret.sellerId;
      ret.sale_date = ret.saleDate;
      ret.total_amount = ret.totalAmount;
      ret.payment_method = ret.paymentMethod;
      ret.payment_date = ret.paymentDate;
      ret.final_amount = ret.finalAmount;
      delete ret._id;
      delete ret.__v;
      delete ret.customerId;
      delete ret.vehicleId;
      delete ret.sellerId;
      delete ret.saleDate;
      delete ret.totalAmount;
      delete ret.paymentMethod;
      delete ret.paymentDate;
      delete ret.finalAmount;
      return ret;
    }
  }
});

// Índices
saleSchema.index({ customerId: 1 });
saleSchema.index({ vehicleId: 1 });
saleSchema.index({ sellerId: 1 });
saleSchema.index({ status: 1 });
saleSchema.index({ saleDate: -1 });
saleSchema.index({ paymentMethod: 1 });

// Virtual para popular dados relacionados
saleSchema.virtual('customer', {
  ref: 'Customer',
  localField: 'customerId',
  foreignField: '_id',
  justOne: true
});

saleSchema.virtual('vehicle', {
  ref: 'Vehicle',
  localField: 'vehicleId',
  foreignField: '_id',
  justOne: true
});

saleSchema.virtual('seller', {
  ref: 'User',
  localField: 'sellerId',
  foreignField: '_id',
  justOne: true
});

// Middleware para calcular valor final
saleSchema.pre('save', function(next) {
  this.finalAmount = this.totalAmount - (this.discount || 0);
  
  if (this.finalAmount < 0) {
    return next(new Error('Valor final não pode ser negativo'));
  }
  
  next();
});

// Métodos de instância
saleSchema.methods.markAsPaid = function() {
  if (this.status === 'PAGO') {
    throw new Error('Venda já está paga');
  }
  if (this.status === 'CANCELADO') {
    throw new Error('Venda cancelada não pode ser marcada como paga');
  }
  
  this.status = 'PAGO';
  this.paymentDate = new Date();
  return this.save();
};

saleSchema.methods.cancel = function(reason) {
  if (this.status === 'CANCELADO') {
    throw new Error('Venda já está cancelada');
  }
  if (this.status === 'PAGO') {
    throw new Error('Venda paga não pode ser cancelada');
  }
  
  this.status = 'CANCELADO';
  if (reason) {
    this.notes = this.notes ? `${this.notes}\nCancelamento: ${reason}` : `Cancelamento: ${reason}`;
  }
  return this.save();
};

// Métodos estáticos
saleSchema.statics.findByCustomer = function(customerId) {
  return this.find({ customerId }).populate('vehicle seller');
};

saleSchema.statics.findByVehicle = function(vehicleId) {
  return this.find({ vehicleId }).populate('customer seller');
};

saleSchema.statics.findBySeller = function(sellerId) {
  return this.find({ sellerId }).populate('customer vehicle');
};

saleSchema.statics.findByStatus = function(status) {
  return this.find({ status }).populate('customer vehicle seller');
};

saleSchema.statics.getSalesStats = function(startDate, endDate) {
  const matchStage = {};
  
  if (startDate || endDate) {
    matchStage.saleDate = {};
    if (startDate) matchStage.saleDate.$gte = new Date(startDate);
    if (endDate) matchStage.saleDate.$lte = new Date(endDate);
  }
  
  return this.aggregate([
    { $match: matchStage },
    {
      $group: {
        _id: '$status',
        count: { $sum: 1 },
        totalAmount: { $sum: '$finalAmount' }
      }
    },
    {
      $group: {
        _id: null,
        stats: {
          $push: {
            status: '$_id',
            count: '$count',
            totalAmount: '$totalAmount'
          }
        },
        totalSales: { $sum: '$count' },
        totalRevenue: { $sum: '$totalAmount' }
      }
    }
  ]);
};

saleSchema.statics.getMonthlyStats = function(year) {
  return this.aggregate([
    {
      $match: {
        saleDate: {
          $gte: new Date(year, 0, 1),
          $lt: new Date(year + 1, 0, 1)
        }
      }
    },
    {
      $group: {
        _id: { $month: '$saleDate' },
        count: { $sum: 1 },
        revenue: { $sum: '$finalAmount' }
      }
    },
    { $sort: { '_id': 1 } }
  ]);
};

module.exports = mongoose.model('Sale', saleSchema);
