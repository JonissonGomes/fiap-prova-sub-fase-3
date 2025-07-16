import axios from 'axios';
import { 
  Vehicle, 
  VehicleCreate, 
  VehicleStatus, 
  VehicleFilters, 
  Sale, 
  SaleCreate,
  SaleUpdate,
  Payment,
  Customer, 
  CustomerCreate, 
  CustomerUpdate,
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  TokenValidation,
  RateLimitStats,
  RateLimitConfig
} from '../types';

// URL do backend unificado no Render
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://fiap-unified-backend.onrender.com';

// Configuração base do Axios
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000, // 30 segundos para cold starts do Render
  headers: {
    'Content-Type': 'application/json',
  },
});

// Instâncias específicas para cada serviço (todas apontam para o mesmo backend)
export const authApi = axios.create({
  baseURL: `${BACKEND_URL}/auth`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const coreApi = axios.create({
  baseURL: `${BACKEND_URL}/vehicles`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const salesApi = axios.create({
  baseURL: `${BACKEND_URL}/sales`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const customerApi = axios.create({
  baseURL: `${BACKEND_URL}/customers`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptador para adicionar token de autenticação
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

// Interceptador para tratar erros
const handleError = (error: any) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
  
  // Rate limiting
  if (error.response?.status === 429) {
    console.warn('Rate limit atingido, aguardando...');
  }
  
  return Promise.reject(error);
};

// Aplicar interceptadores em todas as instâncias
[api, authApi, coreApi, salesApi, customerApi].forEach(instance => {
  instance.interceptors.request.use(addAuthToken);
  instance.interceptors.response.use(
    (response) => response,
    handleError
  );
});

// Serviços de Autenticação
export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await authApi.post<LoginResponse>('/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await authApi.post<User>('/register', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await authApi.post('/logout', { refresh_token: refreshToken });
    }
  },

  validateToken: async (): Promise<TokenValidation> => {
    const response = await authApi.get<TokenValidation>('/validate');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await authApi.post<LoginResponse>('/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await authApi.get<User>('/profile');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await authApi.put<User>('/profile', userData);
    return response.data;
  }
};

// Serviços de Veículos
export const vehiclesApi = {
  list: async (filters: VehicleFilters = {}): Promise<Vehicle[]> => {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.min_price) params.append('min_price', filters.min_price.toString());
    if (filters.max_price) params.append('max_price', filters.max_price.toString());
    if (filters.brand) params.append('brand', filters.brand);
    if (filters.model) params.append('model', filters.model);
    if (filters.sort) params.append('sort', filters.sort);
    if (filters.order) params.append('order', filters.order);
    if (filters.skip) params.append('skip', filters.skip.toString());
    if (filters.limit) params.append('limit', filters.limit.toString());

    const response = await coreApi.get<Vehicle[]>(`/?${params.toString()}`);
    return response.data;
  },

  get: async (id: string): Promise<Vehicle> => {
    const response = await coreApi.get<Vehicle>(`/${id}`);
    return response.data;
  },

  create: async (vehicle: VehicleCreate): Promise<Vehicle> => {
    const response = await coreApi.post<Vehicle>('/', vehicle);
    return response.data;
  },

  update: async (id: string, vehicle: Partial<VehicleCreate>): Promise<Vehicle> => {
    const response = await coreApi.put<Vehicle>(`/${id}`, vehicle);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await coreApi.delete(`/${id}`);
  },

  updateStatus: async (id: string, status: string): Promise<Vehicle> => {
    const response = await coreApi.patch<Vehicle>(`/${id}/status`, { status });
    return response.data;
  }
};

// Serviços de Vendas
export const salesApi = {
  list: async (skip = 0, limit = 100): Promise<Sale[]> => {
    const response = await salesApi.get<Sale[]>(`?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  get: async (id: string): Promise<Sale> => {
    const response = await salesApi.get<Sale>(`/${id}`);
    return response.data;
  },

  create: async (sale: SaleCreate): Promise<Sale> => {
    const response = await salesApi.post<Sale>('/', sale);
    return response.data;
  },

  update: async (id: string, sale: SaleUpdate): Promise<Sale> => {
    const response = await salesApi.put<Sale>(`/${id}`, sale);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await salesApi.delete(`/${id}`);
  },

  purchase: async (data: { customer_id: string; vehicle_id: string; payment_method: string; notes?: string }): Promise<Sale> => {
    const response = await salesApi.post<Sale>('/purchase', data);
    return response.data;
  },

  updateStatus: async (id: string, status: string, notes?: string): Promise<Sale> => {
    const response = await salesApi.put<Sale>(`/${id}/status`, { status, notes });
    return response.data;
  },

  confirmPayment: async (saleId: string): Promise<Sale> => {
    const response = await salesApi.patch<Sale>(`/${saleId}/payment/confirm`);
    return response.data;
  },

  cancelPayment: async (saleId: string): Promise<Sale> => {
    const response = await salesApi.patch<Sale>(`/${saleId}/mark-as-canceled`);
    return response.data;
  }
};

// Serviços de Clientes
export const customerService = {
  list: async (skip = 0, limit = 100, active?: boolean): Promise<Customer[]> => {
    try {
      const params = new URLSearchParams();
      params.append('skip', skip.toString());
      params.append('limit', limit.toString());
      if (active !== undefined) {
        params.append('active', active.toString());
      }
      
      const response = await customerApi.get<Customer[]>(`/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      throw error;
    }
  },

  get: async (id: string): Promise<Customer> => {
    try {
      const response = await customerApi.get<Customer>(`/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar cliente:', error);
      throw error;
    }
  },

  create: async (customer: CustomerCreate): Promise<Customer> => {
    try {
      const response = await customerApi.post<Customer>('/', customer);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar cliente:', error);
      throw error;
    }
  },

  update: async (id: string, customer: CustomerUpdate): Promise<Customer> => {
    try {
      const response = await customerApi.put<Customer>(`/${id}`, customer);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar cliente:', error);
      throw error;
    }
  },

  delete: async (id: string): Promise<void> => {
    try {
      await customerApi.delete(`/${id}`);
    } catch (error) {
      console.error('Erro ao deletar cliente:', error);
      throw error;
    }
  },

  search: async (query: string): Promise<Customer[]> => {
    try {
      const response = await customerApi.get<Customer[]>(`/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      throw error;
    }
  }
}

// Serviços de Pagamentos (mantido para compatibilidade)
export const paymentsApi = {
  list: async (): Promise<Payment[]> => {
    const response = await coreApi.get<Payment[]>('/payments');
    return response.data;
  },

  get: async (id: string): Promise<Payment> => {
    const response = await coreApi.get<Payment>(`/payments/${id}`);
    return response.data;
  },

  create: async (payment: Omit<Payment, 'id' | 'created_at' | 'updated_at'>): Promise<Payment> => {
    const response = await coreApi.post<Payment>('/payments', payment);
    return response.data;
  },

  update: async (id: string, payment: Partial<Payment>): Promise<Payment> => {
    const response = await coreApi.put<Payment>(`/payments/${id}`, payment);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await coreApi.delete(`/payments/${id}`);
  }
};

// Serviços de Rate Limiting
export const rateLimitApi = {
  getStats: async (): Promise<RateLimitStats> => {
    const response = await authApi.get<RateLimitStats>('/rate-limit/stats');
    return response.data;
  },

  getConfig: async (): Promise<RateLimitConfig> => {
    const response = await authApi.get<RateLimitConfig>('/rate-limit/config');
    return response.data;
  },

  updateConfig: async (config: Partial<RateLimitConfig>): Promise<RateLimitConfig> => {
    const response = await authApi.put<RateLimitConfig>('/rate-limit/config', config);
    return response.data;
  }
};

// Utilitários
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

export const getCurrentUser = (): User | null => {
  const userStr = localStorage.getItem('current_user');
  return userStr ? JSON.parse(userStr) : null;
};

export const hasRole = (role: string): boolean => {
  const user = getCurrentUser();
  return user?.role === role;
};

export const isAdmin = (): boolean => hasRole('ADMIN');
export const isSales = (): boolean => hasRole('SALES');
export const isCustomer = (): boolean => hasRole('CUSTOMER');

// Exportação da API principal (para compatibilidade)
export default api; 