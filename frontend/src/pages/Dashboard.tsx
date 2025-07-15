import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  DirectionsCar as VehicleIcon,
  ShoppingCart as SaleIcon,
  Payment as PaymentIcon,
  CheckCircle as CheckIcon,
  Pending as PendingIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { VehicleStatus, PaymentStatus } from '../types';
import api from '../services/api';

interface DashboardStats {
  totalVehicles: number;
  availableVehicles: number;
  reservedVehicles: number;
  soldVehicles: number;
  totalSales: number;
  pendingSales: number;
  paidSales: number;
  cancelledSales: number;
  totalRevenue: number;
  totalPayments: number;
  pendingPayments: number;
  paidPayments: number;
  cancelledPayments: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalVehicles: 0,
    availableVehicles: 0,
    reservedVehicles: 0,
    soldVehicles: 0,
    totalSales: 0,
    pendingSales: 0,
    paidSales: 0,
    cancelledSales: 0,
    totalRevenue: 0,
    totalPayments: 0,
    pendingPayments: 0,
    paidPayments: 0,
    cancelledPayments: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [vehicles, sales, payments] = await Promise.all([
          api.get('/vehicles').then(res => res.data),
          api.get('/sales').then(res => res.data), 
          api.get('/payments').then(res => res.data)
        ]);

        setStats({
          totalVehicles: vehicles.length,
          availableVehicles: vehicles.filter((v: { status: VehicleStatus }) => v.status === VehicleStatus.AVAILABLE).length,
          reservedVehicles: vehicles.filter((v: { status: VehicleStatus }) => v.status === VehicleStatus.RESERVED).length,
          soldVehicles: vehicles.filter((v: { status: VehicleStatus }) => v.status === VehicleStatus.SOLD).length,
          totalSales: sales.length,
          pendingSales: sales.filter((s: { payment_status: PaymentStatus }) => s.payment_status === PaymentStatus.PENDING).length,
          paidSales: sales.filter((s: { payment_status: PaymentStatus }) => s.payment_status === PaymentStatus.PAID).length,
          cancelledSales: sales.filter((s: { payment_status: PaymentStatus }) => s.payment_status === PaymentStatus.CANCELLED).length,
          totalRevenue: sales.reduce((sum: number, s: { sale_price: number }) => sum + s.sale_price, 0),
          // Dados de pagamentos
          totalPayments: payments.length,
          pendingPayments: payments.filter((p: { status: PaymentStatus }) => p.status === PaymentStatus.PENDING).length,
          paidPayments: payments.filter((p: { status: PaymentStatus }) => p.status === PaymentStatus.PAID).length,
          cancelledPayments: payments.filter((p: { status: PaymentStatus }) => p.status === PaymentStatus.CANCELLED).length
        });
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    };

    fetchStats();
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <Paper
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        height: 140,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          right: 0,
          opacity: 0.1,
          transform: 'scale(2)',
          transformOrigin: 'top right'
        }}
      >
        {icon}
      </Box>
      <Typography component="h2" variant="h6" color="primary" gutterBottom>
        {title}
      </Typography>
      <Typography component="p" variant="h4" sx={{ color }}>
        {value}
      </Typography>
    </Paper>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {/* Vehicle Stats */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Total de Veículos"
            value={stats.totalVehicles}
            icon={<VehicleIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Veículos Disponíveis"
            value={stats.availableVehicles}
            icon={<VehicleIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Veículos Reservados"
            value={stats.reservedVehicles}
            icon={<VehicleIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Veículos Vendidos"
            value={stats.soldVehicles}
            icon={<VehicleIcon />}
            color="#d32f2f"
          />
        </Grid>

        {/* Sales Stats */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Total de Vendas"
            value={stats.totalSales}
            icon={<SaleIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Vendas Pendentes"
            value={stats.pendingSales}
            icon={<PendingIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Vendas Pagas"
            value={stats.paidSales}
            icon={<CheckIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Vendas Canceladas"
            value={stats.cancelledSales}
            icon={<CancelIcon />}
            color="#d32f2f"
          />
        </Grid>

        {/* Payment Stats */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Total de Pagamentos"
            value={stats.totalPayments}
            icon={<PaymentIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Pagamentos Pendentes"
            value={stats.pendingPayments}
            icon={<PendingIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Pagamentos Realizados"
            value={stats.paidPayments}
            icon={<CheckIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Pagamentos Cancelados"
            value={stats.cancelledPayments}
            icon={<CancelIcon />}
            color="#d32f2f"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;