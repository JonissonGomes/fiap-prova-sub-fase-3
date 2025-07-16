import axios, { AxiosInstance } from 'axios';
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

// Configuração das URLs base - Render
const BASE_URL = 'https://fiap-prova-sub-fase-3.onrender.com';

const CORE_API_URL = process.env.REACT_APP_CORE_API_URL || BASE_URL;
const SALES_API_URL = process.env.REACT_APP_SALES_API_URL || BASE_URL;
const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || BASE_URL;
const CUSTOMER_API_URL = process.env.REACT_APP_CUSTOMER_API_URL || BASE_URL;

// Instâncias do Axios
const coreApi: AxiosInstance = axios.create({
  baseURL: CORE_API_URL,
  timeout: 30000, // Aumentado para 30 segundos devido ao cold start do Render
  headers: {
    'Content-Type': 'application/json',
  },
});

const salesApiInstance: AxiosInstance = axios.create({
  baseURL: SALES_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const authApi: AxiosInstance = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const customerApi: AxiosInstance = axios.create({
  baseURL: CUSTOMER_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
const addAuthInterceptor = (apiInstance: any) => {
  apiInstance.interceptors.request.use(
    (config: any) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: any) => Promise.reject(error)
  );

  // Interceptor para lidar com rate limiting
  apiInstance.interceptors.response.use(
    (response: any) => response,
    async (error: any) => {
      if (error.response?.status === 429) {
        const retryAfter = error.response.data.retry_after || 60;
        console.warn(`Rate limit excedido. Tentando novamente em ${retryAfter} segundos...`);
        
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        return apiInstance.request(error.config);
      }

      if (error.response?.status === 401) {
        // Token expirado, tentar renovar
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            const response = await authApi.post('/auth/refresh', {
              refresh_token: refreshToken
            });
            
            const { access_token, refresh_token: newRefreshToken } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefreshToken);
            
            // Repetir a requisição original
            error.config.headers.Authorization = `Bearer ${access_token}`;
            return apiInstance.request(error.config);
          } catch (refreshError) {
            // Falha ao renovar token, redirecionar para login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('current_user');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
      }

      return Promise.reject(error);
    }
  );
}

// Aplicar interceptors
addAuthInterceptor(coreApi);
addAuthInterceptor(salesApiInstance);
addAuthInterceptor(authApi);
addAuthInterceptor(customerApi);

// Serviços de Autenticação
export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await authApi.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await authApi.post<User>('/auth/register', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await authApi.post('/auth/logout', { refresh_token: refreshToken });
    }
  },

  validateToken: async (): Promise<TokenValidation> => {
    const response = await authApi.get<TokenValidation>('/auth/validate');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await authApi.post<LoginResponse>('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await authApi.get<User>('/auth/profile');
    return response.data;
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await authApi.put<User>('/auth/profile', userData);
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

    const response = await coreApi.get<Vehicle[]>(`/vehicles/?${params.toString()}`);
    return response.data;
  },

  get: async (id: string): Promise<Vehicle> => {
    const response = await coreApi.get<Vehicle>(`/vehicles/${id}`);
    return response.data;
  },

  create: async (vehicle: VehicleCreate): Promise<Vehicle> => {
    const response = await coreApi.post<Vehicle>('/vehicles/', vehicle);
    return response.data;
  },

  update: async (id: string, vehicle: Partial<VehicleCreate>): Promise<Vehicle> => {
    const response = await coreApi.put<Vehicle>(`/vehicles/${id}`, vehicle);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await coreApi.delete(`/vehicles/${id}`);
  },

  updateStatus: async (id: string, status: string): Promise<Vehicle> => {
    const response = await coreApi.patch<Vehicle>(`/vehicles/${id}/status`, { status });
    return response.data;
  }
};

// Serviços de Vendas
export const salesApi = {
  list: async (skip = 0, limit = 100): Promise<Sale[]> => {
    const response = await salesApiInstance.get<Sale[]>(`/sales?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  get: async (id: string): Promise<Sale> => {
    const response = await salesApiInstance.get<Sale>(`/sales/${id}`);
    return response.data;
  },

  create: async (sale: SaleCreate): Promise<Sale> => {
    const response = await salesApiInstance.post<Sale>('/sales', sale);
    return response.data;
  },

  update: async (id: string, sale: SaleUpdate): Promise<Sale> => {
    const response = await salesApiInstance.put<Sale>(`/sales/${id}`, sale);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await salesApiInstance.delete(`/sales/${id}`);
  },

  purchase: async (data: { customer_id: string; vehicle_id: string; payment_method: string; notes?: string }): Promise<Sale> => {
    const response = await salesApiInstance.post<Sale>('/sales/purchase', data);
    return response.data;
  },

  updateStatus: async (id: string, status: string, notes?: string): Promise<Sale> => {
    const response = await salesApiInstance.put<Sale>(`/sales/${id}/status`, { status, notes });
    return response.data;
  },

  confirmPayment: async (saleId: string): Promise<Sale> => {
    const response = await salesApiInstance.patch<Sale>(`/sales/${saleId}/payment/confirm`);
    return response.data;
  },

  cancelPayment: async (saleId: string): Promise<Sale> => {
    const response = await salesApiInstance.patch<Sale>(`/sales/${saleId}/mark-as-canceled`);
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
      
      const response = await customerApi.get<Customer[]>(`/customers/?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      throw error;
    }
  },

  get: async (id: string): Promise<Customer> => {
    try {
      const response = await customerApi.get<Customer>(`/customers/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar cliente:', error);
      throw error;
    }
  },

  create: async (customer: CustomerCreate): Promise<Customer> => {
    try {
      const response = await customerApi.post<Customer>('/customers/', customer);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar cliente:', error);
      throw error;
    }
  },

  update: async (id: string, customer: CustomerUpdate): Promise<Customer> => {
    try {
      const response = await customerApi.put<Customer>(`/customers/${id}`, customer);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar cliente:', error);
      throw error;
    }
  },

  delete: async (id: string): Promise<void> => {
    try {
      await customerApi.delete(`/customers/${id}`);
    } catch (error) {
      console.error('Erro ao deletar cliente:', error);
      throw error;
    }
  },

  search: async (query: string): Promise<Customer[]> => {
    try {
      const response = await customerApi.get<Customer[]>(`/customers/search?q=${encodeURIComponent(query)}`);
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
  return !!localStorage.getItem('access_token');
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
export default coreApi; 