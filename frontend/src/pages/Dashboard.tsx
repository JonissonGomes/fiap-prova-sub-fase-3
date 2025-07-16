import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  LinearProgress,
  Alert,
  Chip,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  DirectionsCar as VehicleIcon,
  ShoppingCart as SaleIcon,
  Payment as PaymentIcon,
  Person as CustomerIcon,
  CheckCircle as CheckIcon,
  Pending as PendingIcon,
  Cancel as CancelIcon,
  TrendingUp as TrendingIcon,
  TrendingDown as TrendingDownIcon,
  AdminPanelSettings as AdminIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  AttachMoney as MoneyIcon,
  Speed as SpeedIcon,
  Inventory as InventoryIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { isAdmin } from '../utils/permissions';
import { vehiclesApi, salesApi, customerService } from '../services/api';
import { Vehicle, Sale, Customer, VehicleStatus, PaymentStatus } from '../types';

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
  totalCustomers: number;
  averageSalePrice: number;
  conversionRate: number;
  recentSales: Sale[];
  topVehicles: Vehicle[];
  systemHealth: {
    vehicles: boolean;
    sales: boolean;
    customers: boolean;
    payments: boolean;
  };
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
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
    totalCustomers: 0,
    averageSalePrice: 0,
    conversionRate: 0,
    recentSales: [],
    topVehicles: [],
    systemHealth: {
      vehicles: true,
      sales: true,
      customers: true,
      payments: true
    }
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (user && isAdmin(user)) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [vehicles, sales, customers] = await Promise.all([
        vehiclesApi.list(),
        salesApi.list(),
        customerService.list()
      ]);

      // Calcular estatísticas
      const availableVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.AVAILABLE);
      const reservedVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.RESERVED);
      const soldVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.SOLD);
      
      const paidSales = sales.filter((s: Sale) => s.payment_status === PaymentStatus.PAID);
      const pendingSales = sales.filter((s: Sale) => s.payment_status === PaymentStatus.PENDING);
      const cancelledSales = sales.filter((s: Sale) => s.payment_status === PaymentStatus.CANCELLED);
      
      const totalRevenue = paidSales.reduce((sum: number, s: Sale) => sum + s.sale_price, 0);
      const averageSalePrice = paidSales.length > 0 ? totalRevenue / paidSales.length : 0;
      const conversionRate = vehicles.length > 0 ? (soldVehicles.length / vehicles.length) * 100 : 0;

      // Vendas recentes (últimas 5)
      const recentSales = sales
        .sort((a: Sale, b: Sale) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5);

      // Veículos mais caros (top 5)
      const topVehicles = vehicles
        .sort((a: Vehicle, b: Vehicle) => b.price - a.price)
        .slice(0, 5);

      setStats({
        totalVehicles: vehicles.length,
        availableVehicles: availableVehicles.length,
        reservedVehicles: reservedVehicles.length,
        soldVehicles: soldVehicles.length,
        totalSales: sales.length,
        pendingSales: pendingSales.length,
        paidSales: paidSales.length,
        cancelledSales: cancelledSales.length,
        totalRevenue,
        totalCustomers: customers.length,
        averageSalePrice,
        conversionRate,
        recentSales,
        topVehicles,
        systemHealth: {
          vehicles: vehicles.length > 0,
          sales: sales.length > 0,
          customers: customers.length > 0,
          payments: sales.length > 0
        }
      });
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getStatusColor = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.PAID:
        return 'success';
      case PaymentStatus.PENDING:
        return 'warning';
      case PaymentStatus.CANCELLED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.PAID:
        return 'Pago';
      case PaymentStatus.PENDING:
        return 'Pendente';
      case PaymentStatus.CANCELLED:
        return 'Cancelado';
      default:
        return status;
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
    trend?: { value: number; positive: boolean };
  }> = ({ title, value, icon, color, subtitle, trend }) => {
    // Função para formatar valores grandes (igual ao Home)
    const formatLargeValue = (val: string | number) => {
      if (typeof val === 'string' && val.includes('R$')) {
        const numericValue = parseFloat(val.replace(/[^\d,]/g, '').replace(',', '.'));
        if (numericValue >= 1000000) {
          const abbreviated = (numericValue / 1000000).toFixed(1).replace('.', ',');
          return {
            main: `R$ ${abbreviated}M`,
            full: val
          };
        } else if (numericValue >= 1000) {
          const abbreviated = (numericValue / 1000).toFixed(0);
          return {
            main: `R$ ${abbreviated}K`,
            full: val
          };
        }
      } else if (typeof val === 'number' && val >= 1000) {
        const abbreviated = (val / 1000).toFixed(0);
        return {
          main: `${abbreviated}K`,
          full: val.toString()
        };
      }
      return { main: val.toString(), full: null };
    };

    const formattedValue = formatLargeValue(value);

    return (
      <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
            <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
              {icon}
            </Avatar>
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, position: 'absolute', top: 16, right: 16 }}>
                {trend.positive ? (
                  <TrendingIcon color="success" fontSize="small" />
                ) : (
                  <TrendingDownIcon color="error" fontSize="small" />
                )}
                <Typography variant="caption" color={trend.positive ? 'success.main' : 'error.main'}>
                  {trend.value}%
                </Typography>
              </Box>
            )}
          </Box>
          
          <Box sx={{ 
            flex: 1,
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            textAlign: 'center'
          }}>
            <Typography 
              variant="h4" 
              component="div" 
              sx={{ 
                fontWeight: 'bold',
                fontSize: { xs: '1.25rem', sm: '1.5rem', md: '1.75rem' },
                lineHeight: 1.2,
                mb: 0.5,
                wordBreak: 'break-word'
              }}
            >
              {formattedValue.main}
            </Typography>
            {formattedValue.full && (
              <Typography 
                variant="caption" 
                color="text.secondary"
                sx={{ 
                  fontSize: { xs: '0.625rem', sm: '0.75rem' },
                  lineHeight: 1.2,
                  mb: 0.5,
                  fontWeight: 300
                }}
              >
                {formattedValue.full}
              </Typography>
            )}
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                lineHeight: 1.2,
                mb: subtitle ? 0.5 : 0,
                fontWeight: 500
              }}
            >
              {title}
            </Typography>
            {subtitle && (
              <Typography 
                variant="caption" 
                color="text.secondary"
                sx={{ 
                  fontSize: { xs: '0.625rem', sm: '0.75rem' },
                  lineHeight: 1.2,
                  display: 'block'
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };

  // Verificar se o usuário é administrador
  if (!user || !isAdmin(user)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Você não tem permissão para acessar o Dashboard Administrativo.
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ width: '100%' }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2, fontWeight: 'bold' }}>
            <AdminIcon color="primary" />
            Dashboard Administrativo
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Visão completa do sistema de vendas de veículos
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
          </Typography>
          <Tooltip title="Atualizar dados">
            <IconButton onClick={fetchDashboardData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Status do Sistema */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, mb: 3 }}>
            <InfoIcon color="primary" />
            Status do Sistema
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, borderRadius: 1, bgcolor: 'background.paper' }}>
                <CheckIcon color={stats.systemHealth.vehicles ? 'success' : 'error'} />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Veículos</Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, borderRadius: 1, bgcolor: 'background.paper' }}>
                <CheckIcon color={stats.systemHealth.sales ? 'success' : 'error'} />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Vendas</Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, borderRadius: 1, bgcolor: 'background.paper' }}>
                <CheckIcon color={stats.systemHealth.customers ? 'success' : 'error'} />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Clientes</Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, borderRadius: 1, bgcolor: 'background.paper' }}>
                <CheckIcon color={stats.systemHealth.payments ? 'success' : 'error'} />
                <Typography variant="body2" sx={{ fontWeight: 500 }}>Pagamentos</Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Estatísticas Principais */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total de Veículos"
            value={stats.totalVehicles}
            icon={<VehicleIcon />}
            color="#1976d2"
            subtitle={`${stats.availableVehicles} disponíveis`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total de Negociações"
            value={stats.totalSales}
            icon={<SaleIcon />}
            color="#2e7d32"
            subtitle={`${stats.paidSales} pagas`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Receita Total"
            value={formatCurrency(stats.totalRevenue)}
            icon={<MoneyIcon />}
            color="#ed6c02"
            subtitle="Apenas vendas pagas"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Clientes"
            value={stats.totalCustomers}
            icon={<CustomerIcon />}
            color="#9c27b0"
            subtitle="Cadastrados"
          />
        </Grid>
      </Grid>

      {/* Métricas de Performance */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Métricas de Performance
              </Typography>
              <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Grid container spacing={3}>
                  <Grid item xs={6}>
                    <Box sx={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      textAlign: 'center', 
                      p: 3,
                      height: '100%'
                    }}>
                      <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {formatPercentage(stats.conversionRate)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        Taxa de Conversão
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ 
                      display: 'flex', 
                      flexDirection: 'column', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      textAlign: 'center', 
                      p: 3,
                      height: '100%'
                    }}>
                      <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {formatCurrency(stats.averageSalePrice)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        Ticket Médio
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Status dos Veículos
              </Typography>
              <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>Disponíveis</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{stats.availableVehicles}</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(stats.availableVehicles / stats.totalVehicles) * 100} 
                    color="success"
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>Reservados</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{stats.reservedVehicles}</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(stats.reservedVehicles / stats.totalVehicles) * 100} 
                    color="warning"
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>Vendidos</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{stats.soldVehicles}</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(stats.soldVehicles / stats.totalVehicles) * 100} 
                    color="error"
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

            {/* Vendas Recentes e Top Veículos */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Vendas Recentes
              </Typography>
              <List sx={{ p: 0 }}>
                {stats.recentSales.map((sale) => (
                  <ListItem key={sale.id} divider sx={{ px: 0, py: 2 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <SaleIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`Venda #${sale.id.slice(-6)}`}
                      secondary={`${formatCurrency(sale.sale_price)} • ${sale.buyer_cpf}`}
                      primaryTypographyProps={{ fontWeight: 500 }}
                      secondaryTypographyProps={{ fontSize: '0.875rem' }}
                    />
                    <Chip
                      label={getStatusText(sale.payment_status)}
                      color={getStatusColor(sale.payment_status) as any}
                      size="small"
                      sx={{ fontWeight: 500 }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Veículos Mais Caros
              </Typography>
              <List sx={{ p: 0 }}>
                {stats.topVehicles.map((vehicle) => (
                  <ListItem key={vehicle.id} divider sx={{ px: 0, py: 2 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <VehicleIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${vehicle.brand} ${vehicle.model} (${vehicle.year})`}
                      secondary={`${vehicle.color} • ${vehicle.status}`}
                      primaryTypographyProps={{ fontWeight: 500 }}
                      secondaryTypographyProps={{ fontSize: '0.875rem' }}
                    />
                    <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                      {formatCurrency(vehicle.price)}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alertas e Recomendações */}
      <Card sx={{ mt: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 600, mb: 3 }}>
            <WarningIcon color="warning" />
            Alertas e Recomendações
          </Typography>
          <Grid container spacing={3}>
            {stats.pendingSales > 0 && (
              <Grid item xs={12} md={6}>
                <Alert severity="warning" sx={{ '& .MuiAlert-message': { fontWeight: 500 } }}>
                  <Typography variant="body2">
                    <strong>{stats.pendingSales} vendas pendentes</strong> aguardando aprovação de pagamento.
                  </Typography>
                </Alert>
              </Grid>
            )}
            {stats.availableVehicles < 5 && (
              <Grid item xs={12} md={6}>
                <Alert severity="info" sx={{ '& .MuiAlert-message': { fontWeight: 500 } }}>
                  <Typography variant="body2">
                    <strong>Estoque baixo:</strong> Apenas {stats.availableVehicles} veículos disponíveis.
                  </Typography>
                </Alert>
              </Grid>
            )}
            {stats.conversionRate < 20 && (
              <Grid item xs={12} md={6}>
                <Alert severity="info" sx={{ '& .MuiAlert-message': { fontWeight: 500 } }}>
                  <Typography variant="body2">
                    <strong>Taxa de conversão baixa:</strong> {formatPercentage(stats.conversionRate)} - considere revisar estratégias de venda.
                  </Typography>
                </Alert>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Dashboard;