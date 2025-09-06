import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  DirectionsCar as VehicleIcon,
  ShoppingCart as SaleIcon,
  Person as CustomerIcon,
  TrendingUp as TrendingIcon,
  TrendingDown as TrendingDownIcon,
  AdminPanelSettings as AdminIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { isAdmin } from '../utils/permissions';
import { vehiclesApi, salesService, customerService } from '../services/api';
import { Vehicle, Sale, VehicleStatus } from '../types';
import { onDataRefresh, DATA_REFRESH_EVENTS } from '../utils/dataRefresh';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

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
    topVehicles: []
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (user && isAdmin(user)) {
      fetchDashboardData();
    }
  }, [user]);

  // Escutar mudanças de dados para atualizar automaticamente
  useEffect(() => {
    const cleanupFunctions: (() => void)[] = [];
    
    if (user && isAdmin(user)) {
      // Atualizar quando há mudanças em veículos, vendas ou clientes
      const eventTypes = [DATA_REFRESH_EVENTS.VEHICLES, DATA_REFRESH_EVENTS.SALES, DATA_REFRESH_EVENTS.CUSTOMERS];
      
      eventTypes.forEach(eventType => {
        const cleanup = onDataRefresh(eventType, () => {
          console.log(`Dashboard: Atualizando dados devido a mudança em ${eventType}`);
          fetchDashboardData();
        });
        cleanupFunctions.push(cleanup);
      });
    }
    
    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.role]); // Apenas o role do usuário, não o objeto inteiro

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [vehicles, sales, customers] = await Promise.all([
        vehiclesApi.list(),
        salesService.list(),
        customerService.list()
      ]);

      // Calcular estatísticas
      const availableVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.AVAILABLE);
      const reservedVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.RESERVED);
      const soldVehicles = vehicles.filter((v: Vehicle) => v.status === VehicleStatus.SOLD);
      
      const paidSales = sales.filter((s: Sale) => s.status === 'PAGO');
      const pendingSales = sales.filter((s: Sale) => s.status === 'PENDENTE');
      const cancelledSales = sales.filter((s: Sale) => s.status === 'CANCELADO');
      
      const totalRevenue = paidSales.reduce((sum: number, s: Sale) => sum + s.final_amount, 0);
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
        topVehicles
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PAGO':
        return 'success';
      case 'PENDENTE':
        return 'warning';
      case 'CANCELADO':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PAGO':
        return 'Pago';
      case 'PENDENTE':
        return 'Pendente';
      case 'CANCELADO':
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

      {/* Gráficos */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Gráfico de Vendas por Status */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 400 }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Vendas por Status
              </Typography>
              <Box sx={{ flex: 1, position: 'relative' }}>
                <Doughnut
                  data={{
                    labels: ['Pagas', 'Pendentes', 'Canceladas'],
                    datasets: [
                      {
                        data: [stats.paidSales, stats.pendingSales, stats.cancelledSales],
                        backgroundColor: [
                          '#4caf50',
                          '#ff9800', 
                          '#f44336'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: {
                          padding: 20,
                          font: {
                            size: 12
                          }
                        }
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
                            return `${label}: ${value} (${percentage}%)`;
                          }
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Gráfico de Veículos por Status */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: 400 }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Veículos por Status
              </Typography>
              <Box sx={{ flex: 1, position: 'relative' }}>
                <Bar
                  data={{
                    labels: ['Disponíveis', 'Reservados', 'Vendidos'],
                    datasets: [
                      {
                        label: 'Quantidade',
                        data: [stats.availableVehicles, stats.reservedVehicles, stats.soldVehicles],
                        backgroundColor: [
                          '#2196f3',
                          '#ff9800',
                          '#4caf50'
                        ],
                        borderRadius: 8,
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            return `${context.label}: ${context.parsed.y} veículos`;
                          }
                        }
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          stepSize: 1
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Gráfico de Resumo Financeiro */}
        <Grid item xs={12}>
          <Card sx={{ height: 400 }}>
            <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Resumo Financeiro
              </Typography>
              <Box sx={{ flex: 1, position: 'relative' }}>
                <Bar
                  data={{
                    labels: ['Receita Total (R$ mil)', 'Receita Média (R$ mil)', 'Taxa de Conversão (%)'],
                    datasets: [
                      {
                        label: 'Valores',
                        data: [
                          Math.round(stats.totalRevenue / 1000),
                          Math.round(stats.averageSalePrice / 1000),
                          Math.round(stats.conversionRate * 10) / 10
                        ],
                        backgroundColor: [
                          '#4caf50',
                          '#2196f3',
                          '#ff9800'
                        ],
                        borderRadius: 8,
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const value = context.parsed.y;
                            if (context.dataIndex === 0) {
                              return `Receita Total: R$ ${(value * 1000).toLocaleString('pt-BR')}`;
                            } else if (context.dataIndex === 1) {
                              return `Receita Média: R$ ${(value * 1000).toLocaleString('pt-BR')}`;
                            } else {
                              return `Taxa de Conversão: ${value}%`;
                            }
                          }
                        }
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
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
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Vendas Recentes
              </Typography>
              <Box sx={{ flex: 1 }}>
                <List sx={{ p: 0 }}>
                  {stats.recentSales.map((sale) => (
                    <ListItem key={sale.id} divider sx={{ px: 0, py: 2 }}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <SaleIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`Venda #${sale.id.slice(-6)}`}
                        secondary={`${formatCurrency(sale.final_amount)} • ${sale.customer_id?.name || 'N/A'}`}
                        primaryTypographyProps={{ fontWeight: 500 }}
                        secondaryTypographyProps={{ fontSize: '0.875rem' }}
                      />
                      <Chip
                        label={getStatusText(sale.status)}
                        color={getStatusColor(sale.status) as any}
                        size="small"
                        sx={{ fontWeight: 500 }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                Veículos Mais Caros
              </Typography>
              <Box sx={{ flex: 1 }}>
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
              </Box>
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