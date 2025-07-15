export enum PaymentStatus {
  PENDING = 'PENDENTE',
  PAID = 'PAGO',
  CANCELLED = 'CANCELADA'
}

export enum VehicleStatus {
  AVAILABLE = 'DISPONÍVEL',
  RESERVED = 'RESERVADO',
  SOLD = 'VENDIDO'
}

export interface Vehicle {
  id: string;
  brand: string;
  model: string;
  year: number;
  color: string;
  price: number;
  status: VehicleStatus;
  created_at: string;
  updated_at: string;
}

export interface VehicleCreate {
  brand: string;
  model: string;
  year: number;
  color: string;
  price: number;
  status: VehicleStatus;
}

export interface VehicleUpdate {
  brand?: string;
  model?: string;
  year?: number;
  color?: string;
  price?: number;
  status?: VehicleStatus;
}

export interface Sale {
  id: string;
  vehicle_id: string;
  buyer_cpf: string;
  sale_price: number;
  payment_code: string;
  payment_status: PaymentStatus;
  created_at: string;
  updated_at: string;
}

export interface SaleCreate {
  vehicle_id: string;
  buyer_cpf: string;
  sale_price: number;
  payment_code: string;
  payment_status: PaymentStatus;
}

export interface SaleUpdate {
  vehicle_id?: string;
  buyer_cpf?: string;
  sale_price?: number;
  payment_code?: string;
  payment_status?: PaymentStatus;
}

export interface Payment {
  id: string;
  sale_id: string;
  amount: number;
  payment_method: string;
  status: PaymentStatus;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'ADMIN' | 'CUSTOMER' | 'SALES';
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role: 'ADMIN' | 'CUSTOMER' | 'SALES';
}

export interface TokenValidation {
  valid: boolean;
  user: User;
  expires_at: string;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  cpf: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
  active: boolean;
}

export interface CustomerCreate {
  name: string;
  email: string;
  phone: string;
  cpf: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface CustomerUpdate {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  active?: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

export interface RateLimitError {
  detail: string;
  retry_after: number;
}

export interface RateLimitStats {
  key: string;
  statistics: Record<string, any>;
  message: string;
}

export interface RateLimitConfig {
  limits: Record<string, string>;
  route_limits: Record<string, string>;
  message: string;
}

export interface SortOptions {
  field: string;
  order: 'asc' | 'desc';
}

export interface VehicleFilters {
  status?: VehicleStatus;
  min_price?: number;
  max_price?: number;
  brand?: string;
  model?: string;
  sort?: string;
  order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}
