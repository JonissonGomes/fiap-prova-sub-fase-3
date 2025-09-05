const mongoose = require('mongoose');

// Função para validar CPF
const validateCPF = (cpf) => {
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
    return false;
  }
  
  // Validação do algoritmo do CPF
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf[i]) * (10 - i);
  }
  let digit1 = 11 - (sum % 11);
  if (digit1 >= 10) digit1 = 0;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cpf[i]) * (11 - i);
  }
  let digit2 = 11 - (sum % 11);
  if (digit2 >= 10) digit2 = 0;
  
  return cpf[9] == digit1 && cpf[10] == digit2;
};

const customerSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true,
    minlength: 2,
    maxlength: 100
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Email inválido']
  },
  phone: {
    type: String,
    required: true,
    validate: {
      validator: function(v) {
        const phone = v.replace(/[^\d]/g, '');
        return phone.length >= 10 && phone.length <= 11;
      },
      message: 'Telefone deve ter 10 ou 11 dígitos'
    }
  },
  cpf: {
    type: String,
    required: true,
    unique: true,
    validate: {
      validator: validateCPF,
      message: 'CPF inválido'
    }
  },
  address: {
    type: String,
    maxlength: 200,
    trim: true
  },
  city: {
    type: String,
    maxlength: 100,
    trim: true
  },
  state: {
    type: String,
    maxlength: 2,
    uppercase: true,
    trim: true
  },
  zipCode: {
    type: String,
    maxlength: 10,
    trim: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    default: null
  },
  active: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      ret.id = ret._id;
      ret.zip_code = ret.zipCode; // Compatibilidade com frontend
      delete ret._id;
      delete ret.__v;
      delete ret.zipCode;
      return ret;
    }
  }
});

// Índices
customerSchema.index({ email: 1 });
customerSchema.index({ cpf: 1 });
customerSchema.index({ phone: 1 });
customerSchema.index({ name: 'text', email: 'text' });
customerSchema.index({ active: 1 });

// Middleware para normalizar dados
customerSchema.pre('save', function(next) {
  // Normalizar CPF
  if (this.cpf) {
    this.cpf = this.cpf.replace(/[^\d]/g, '');
  }
  
  // Normalizar telefone
  if (this.phone) {
    this.phone = this.phone.replace(/[^\d]/g, '');
  }
  
  // Normalizar estado
  if (this.state) {
    this.state = this.state.toUpperCase();
  }
  
  next();
});

// Métodos estáticos
customerSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase(), active: true });
};

customerSchema.statics.findByCPF = function(cpf) {
  const cleanCPF = cpf.replace(/[^\d]/g, '');
  return this.findOne({ cpf: cleanCPF, active: true });
};

customerSchema.statics.findByPhone = function(phone) {
  const cleanPhone = phone.replace(/[^\d]/g, '');
  return this.findOne({ phone: cleanPhone, active: true });
};

customerSchema.statics.searchCustomers = function(searchTerm) {
  const regex = new RegExp(searchTerm, 'i');
  return this.find({
    active: true,
    $or: [
      { name: regex },
      { email: regex },
      { cpf: searchTerm.replace(/[^\d]/g, '') },
      { phone: searchTerm.replace(/[^\d]/g, '') }
    ]
  });
};

customerSchema.statics.getStats = function() {
  return this.aggregate([
    {
      $group: {
        _id: null,
        total: { $sum: 1 },
        active: { $sum: { $cond: ['$active', 1, 0] } },
        inactive: { $sum: { $cond: ['$active', 0, 1] } }
      }
    },
    {
      $lookup: {
        from: 'customers',
        pipeline: [
          {
            $match: {
              createdAt: {
                $gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
              }
            }
          },
          { $count: 'thisMonth' }
        ],
        as: 'monthlyStats'
      }
    },
    {
      $project: {
        _id: 0,
        total_customers: '$total',
        active_customers: '$active',
        inactive_customers: '$inactive',
        customers_this_month: { $ifNull: [{ $arrayElemAt: ['$monthlyStats.thisMonth', 0] }, 0] }
      }
    }
  ]);
};

// Método de instância para soft delete
customerSchema.methods.softDelete = function() {
  this.active = false;
  return this.save();
};

module.exports = mongoose.model('Customer', customerSchema);
