import api from './api';
import { Vehicle, VehicleCreate, VehicleUpdate, VehicleStatus } from '../types';

const vehicleService = {
  getAll: async (): Promise<Vehicle[]> => {
    const response = await api.get('/vehicles');
    return response.data;
  },

  getById: async (id: string): Promise<Vehicle> => {
    const response = await api.get(`/vehicles/${id}`);
    return response.data;
  },

  getByStatus: async (status: VehicleStatus): Promise<Vehicle[]> => {
    const response = await api.get(`/vehicles/status/${status}`);
    return response.data;
  },

  create: async (vehicle: VehicleCreate): Promise<Vehicle> => {
    const response = await api.post('/vehicles', vehicle);
    return response.data;
  },

  update: async (id: string, vehicle: VehicleUpdate): Promise<Vehicle> => {
    const response = await api.put(`/vehicles/${id}`, vehicle);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/vehicles/${id}`);
  },

  updateStatus: async (id: string, status: VehicleStatus): Promise<Vehicle> => {
    const response = await api.patch(`/vehicles/${id}/status`, { status });
    return response.data;
  },

  markAsReserved: async (id: string): Promise<void> => {
    await api.post(`/vehicles/${id}/mark-as-reserved`);
  },

  markAsAvailable: async (id: string): Promise<void> => {
    await api.post(`/vehicles/${id}/mark-as-available`);
  },

  markAsSold: async (id: string): Promise<void> => {
    await api.post(`/vehicles/${id}/mark-as-sold`);
  },
};

export default vehicleService; 