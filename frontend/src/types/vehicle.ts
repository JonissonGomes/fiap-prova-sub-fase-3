export enum VehicleStatus {
  AVAILABLE = 'DISPONÍVEL',
  SOLD = 'VENDIDO',
  RESERVED = 'RESERVADO'
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