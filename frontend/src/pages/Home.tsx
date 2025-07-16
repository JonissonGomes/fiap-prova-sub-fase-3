import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Button, 
  Card, 
  CardContent, 
  CardActions,
  Chip,
  Avatar,
  Divider,
  Container,
  LinearProgress,
  Alert,
  IconButton
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import {
  DirectionsCar as VehicleIcon,
  ShoppingCart as SaleIcon,
  Payment as PaymentIcon,
  Person as CustomerIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingIcon,
  CheckCircle as CheckIcon,
  Pending as PendingIcon,
  Cancel as CancelIcon,
  Star as StarIcon,
  ShoppingBag as ShoppingBagIcon,
  Receipt as ReceiptIcon,
  AdminPanelSettings as AdminIcon,
  SellOutlined as SellIcon,
  PersonOutline as PersonIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { isAdmin, isSales, isCustomer, canViewSales, canViewPayments, canViewCustomers } from '../utils/permissions';
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
  myPurchases?: number;
  pendingPurchases?: number;
  paidPurchases?: number;
}

const Home: React.FC = () => {
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
    myPurchases: 0,
    pendingPurchases: 0,
    paidPurchases: 0
  });
  const [loading, setLoading] = useState(true);
  const [customerCpf, setCustomerCpf] = useState<string>('');

  useEffect(() => {
    if (user) {
      fetchStats();
    }
  }, [user]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      
      // Buscar dados básicos sempre
      const [vehicles, sales] = await Promise.all([
        vehiclesApi.list(),
        salesApi.list()
      ]);

             const baseStats = {
         totalVehicles: vehicles.length,
         availableVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.AVAILABLE).length,
         reservedVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.RESERVED).length,
         soldVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.SOLD).length,
         totalSales: sales.length,
         pendingSales: sales.filter((s: Sale) => s.payment_status === PaymentStatus.PENDING).length,
         paidSales: sales.filter((s: Sale) => s.payment_status === PaymentStatus.PAID).length,
         cancelledSales: sales.filter((s: Sale) => s.payment_status === PaymentStatus.CANCELLED).length,
         totalRevenue: sales.filter((s: Sale) => s.payment_status === PaymentStatus.PAID).reduce((sum: number, s: Sale) => sum + s.sale_price, 0),
         totalCustomers: 0,
         myPurchases: 0,
         pendingPurchases: 0,
         paidPurchases: 0
       };

             // Dados específicos para clientes
       if (isCustomer(user) && user?.email) {
         try {
           const customers = await customerService.list();
           const customer = customers.find(c => c.email === user.email);
           
           if (customer) {
             setCustomerCpf(customer.cpf);
             const customerSales = sales.filter((s: Sale) => s.buyer_cpf === customer.cpf);
             baseStats.myPurchases = customerSales.length;
             baseStats.pendingPurchases = customerSales.filter((s: Sale) => s.payment_status === PaymentStatus.PENDING).length;
             baseStats.paidPurchases = customerSales.filter((s: Sale) => s.payment_status === PaymentStatus.PAID).length;
           }
         } catch (error) {
           console.error('Erro ao buscar dados do cliente:', error);
         }
       }

             // Dados específicos para admin/vendedor
       if (isAdmin(user) || isSales(user)) {
         try {
           const customers = await customerService.list();
           baseStats.totalCustomers = customers.length;
         } catch (error) {
           console.error('Erro ao buscar dados de clientes:', error);
         }
       }

      setStats(baseStats);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
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

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

     const getUserRoleDisplay = () => {
     if (isAdmin(user)) return 'Administrador';
     if (isSales(user)) return 'Vendedor';
     if (isCustomer(user)) return 'Cliente';
     return 'Usuário';
   };

     const getUserIcon = () => {
     if (isAdmin(user)) return <AdminIcon />;
     if (isSales(user)) return <SellIcon />;
     return <PersonIcon />;
   };

  const StatCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
  }> = ({ title, value, icon, color, subtitle }) => {
    // Função para formatar valores grandes
    const formatLargeValue = (val: string) => {
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
      }
      return { main: val, full: null };
    };

    const formattedValue = formatLargeValue(value as string);

    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            textAlign: 'center',
            height: '100%',
            justifyContent: 'center'
          }}>
            <Avatar sx={{ bgcolor: color, width: 48, height: 48, mb: 2 }}>
              {icon}
            </Avatar>
            <Typography 
              variant="h5" 
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
                mb: subtitle ? 0.5 : 0
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

  const QuickActionCard: React.FC<{
    title: string;
    description: string;
    icon: React.ReactNode;
    color: string;
    to: string;
    disabled?: boolean;
  }> = ({ title, description, icon, color, to, disabled = false }) => (
    <Card sx={{ height: '100%', opacity: disabled ? 0.6 : 1 }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: color, mr: 2 }}>
            {icon}
          </Avatar>
          <Box>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </Box>
        </Box>
      </CardContent>
      <CardActions sx={{ p: 3, pt: 0 }}>
        <Button
          component={RouterLink}
          to={to}
          variant="contained"
          fullWidth
          disabled={disabled}
          sx={{ bgcolor: color, '&:hover': { bgcolor: color } }}
        >
          Acessar
        </Button>
      </CardActions>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ width: '100%' }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 6, mb: 6 }}>
      {/* Header com saudação personalizada */}
      <Paper sx={{ p: 4, mb: 4, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 2, width: 56, height: 56 }}>
              {getUserIcon()}
            </Avatar>
            <Box>
              <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                {getGreeting()}, {user?.name}!
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9 }}>
                {getUserRoleDisplay()} - Sistema de Vendas FIAP
              </Typography>
            </Box>
          </Box>
          <Chip
            label={getUserRoleDisplay()}
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)', 
              color: 'white',
              fontWeight: 'bold'
            }}
          />
        </Box>
      </Paper>

      {/* Dashboard por perfil */}
      {isCustomer(user) && (
        <>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <ShoppingBagIcon sx={{ mr: 1 }} />
            Suas Compras
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={4}>
              <StatCard
                title="Compras Realizadas"
                value={stats.myPurchases || 0}
                icon={<ShoppingBagIcon />}
                color="#2e7d32"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <StatCard
                title="Pagamentos Pendentes"
                value={stats.pendingPurchases || 0}
                icon={<PendingIcon />}
                color="#ed6c02"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <StatCard
                title="Pagamentos Realizados"
                value={stats.paidPurchases || 0}
                icon={<CheckIcon />}
                color="#1976d2"
              />
            </Grid>
          </Grid>

          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <StarIcon sx={{ mr: 1 }} />
            Ações Rápidas
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <QuickActionCard
                title="Veículos Disponíveis"
                description="Explore nossa seleção de veículos"
                icon={<VehicleIcon />}
                color="#1976d2"
                to="/vehicles"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <QuickActionCard
                title="Minhas Compras"
                description="Acompanhe suas compras e pagamentos"
                icon={<ReceiptIcon />}
                color="#2e7d32"
                to="/my-purchases"
              />
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body1">
              <strong>Dica:</strong> Navegue pelos veículos disponíveis e use o botão "Comprar" para realizar uma compra instantânea com seu CPF cadastrado.
            </Typography>
          </Alert>
        </>
      )}

             {(isAdmin(user) || isSales(user)) && (
        <>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <DashboardIcon sx={{ mr: 1 }} />
            Dashboard Operacional
          </Typography>
          
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
                title="Total de Vendas"
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
                icon={<TrendingIcon />}
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

          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <TrendingIcon sx={{ mr: 1 }} />
            Gerenciamento
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Gerenciar Veículos"
                description="Cadastre e gerencie veículos"
                icon={<VehicleIcon />}
                color="#1976d2"
                to="/vehicles"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Gerenciar Vendas"
                description="Acompanhe e gerencie vendas"
                icon={<SaleIcon />}
                color="#2e7d32"
                to="/sales"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Gerenciar Pagamentos"
                description="Aprove e gerencie pagamentos"
                icon={<PaymentIcon />}
                color="#ed6c02"
                to="/payments"
                disabled={!canViewPayments(user)}
              />
            </Grid>
          </Grid>

          {isAdmin(user) && (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={6}>
                <QuickActionCard
                  title="Gerenciar Clientes"
                  description="Cadastre e gerencie clientes"
                  icon={<CustomerIcon />}
                  color="#9c27b0"
                  to="/customers"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <QuickActionCard
                  title="Dashboard Completo"
                  description="Visão completa do sistema"
                  icon={<DashboardIcon />}
                  color="#607d8b"
                  to="/dashboard"
                />
              </Grid>
            </Grid>
          )}

          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body1">
              <strong>Status do Sistema:</strong> Todos os serviços estão funcionando normalmente. 
              {isAdmin(user) && ' Você tem acesso total ao sistema.'}
                             {isSales(user) && ' Você pode gerenciar vendas e veículos.'}
            </Typography>
          </Alert>
        </>
      )}

      {/* Estatísticas gerais na parte inferior */}
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Estatísticas Gerais do Sistema
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={3}>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary">
                {stats.availableVehicles}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Veículos Disponíveis
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                {stats.paidSales}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vendas Concluídas
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">
                {stats.pendingSales}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vendas Pendentes
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main">
                {stats.cancelledSales}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vendas Canceladas
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default Home; 