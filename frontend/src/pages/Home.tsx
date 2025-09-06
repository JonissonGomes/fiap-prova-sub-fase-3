import React, { useEffect, useState, useCallback } from 'react';
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
  Container,
  LinearProgress,
  Alert
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
  ShoppingBag as ShoppingBagIcon,
  Receipt as ReceiptIcon,
  AdminPanelSettings as AdminIcon,
  SellOutlined as SellIcon,
  PersonOutline as PersonIcon,
  Explore as ExploreIcon,
  Timeline as TimelineIcon,
  EmojiEvents as AchievementIcon,
  Speed as SpeedIcon,
  Verified as VerifiedIcon,
  LocalOffer as OfferIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { isAdmin, isSales, isCustomer, canViewPayments } from '../utils/permissions';
import { vehiclesApi, salesService, customerService } from '../services/api';
import { Vehicle, Sale, VehicleStatus, PaymentStatus } from '../types';
import { onDataRefresh, DATA_REFRESH_EVENTS } from '../utils/dataRefresh';

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
  const [, setCustomerCpf] = useState<string>('');

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      
      // Buscar dados básicos sempre
      const [vehicles, sales] = await Promise.all([
        vehiclesApi.list(),
        salesService.list()
      ]);

             const baseStats = {
         totalVehicles: vehicles.length,
         availableVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.AVAILABLE).length,
         reservedVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.RESERVED).length,
         soldVehicles: vehicles.filter((v: Vehicle) => v.status === VehicleStatus.SOLD).length,
         totalSales: sales.length,
         pendingSales: sales.filter((s: Sale) => s.status === 'PENDENTE').length,
         paidSales: sales.filter((s: Sale) => s.status === 'PAGO').length,
         cancelledSales: sales.filter((s: Sale) => s.status === 'CANCELADO').length,
         totalRevenue: sales.filter((s: Sale) => s.status === 'PAGO').reduce((sum: number, s: Sale) => sum + s.final_amount, 0),
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
                         const customerSales = sales.filter((s: Sale) => s.customer_id?.cpf === customer.cpf);
            baseStats.myPurchases = customerSales.length;
            baseStats.pendingPurchases = customerSales.filter((s: Sale) => s.status === 'PENDENTE').length;
            baseStats.paidPurchases = customerSales.filter((s: Sale) => s.status === 'PAGO').length;
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
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchStats();
    }
  }, [user]); // Removido fetchStats da dependência para evitar loops

  // Escutar mudanças de dados para atualizar automaticamente
  useEffect(() => {
    const cleanupFunctions: (() => void)[] = [];
    
    // Atualizar quando há mudanças em veículos, vendas ou clientes
    const eventTypes = [DATA_REFRESH_EVENTS.VEHICLES, DATA_REFRESH_EVENTS.SALES, DATA_REFRESH_EVENTS.CUSTOMERS];
    
    eventTypes.forEach(eventType => {
      const cleanup = onDataRefresh(eventType, () => {
        console.log(`Home: Atualizando dados devido a mudança em ${eventType}`);
        fetchStats();
      });
      cleanupFunctions.push(cleanup);
    });
    
    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.role]); // Apenas o role do usuário, evita dependência circular

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
      {/* Header de Boas-Vindas */}
      <Paper sx={{ 
        p: 6, 
        mb: 6, 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
        color: 'white',
        borderRadius: 4,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <Box sx={{ 
          position: 'absolute',
          top: -50,
          right: -50,
          width: 200,
          height: 200,
          bgcolor: 'rgba(255,255,255,0.1)',
          borderRadius: '50%'
        }} />
        <Box sx={{ 
          position: 'absolute',
          bottom: -30,
          left: -30,
          width: 150,
          height: 150,
          bgcolor: 'rgba(255,255,255,0.05)',
          borderRadius: '50%'
        }} />
        <Grid container spacing={4} sx={{ position: 'relative', zIndex: 1 }}>
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 3, width: 70, height: 70 }}>
                {getUserIcon()}
              </Avatar>
              <Box>
                <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {getGreeting()}, {user?.name}!
                </Typography>
                <Typography variant="h5" sx={{ opacity: 0.9, mb: 2 }}>
                  Bem-vindo ao Sistema FIAP III
                </Typography>
                <Chip
                  label={getUserRoleDisplay()}
                  sx={{ 
                    bgcolor: 'rgba(255,255,255,0.25)', 
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '1rem',
                    height: 40
                  }}
                />
              </Box>
            </Box>
            <Typography variant="h6" sx={{ opacity: 0.8, lineHeight: 1.6 }}>
              Sua plataforma completa para gerenciamento de vendas de veículos.
              {isCustomer(user) && ' Explore nossa seleção de veículos e realize suas compras com facilidade.'}
              {(isAdmin(user) || isSales(user)) && ' Gerencie operações, acompanhe métricas e otimize seus resultados.'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              textAlign: 'center',
              height: '100%',
              justifyContent: 'center'
            }}>
              <TimelineIcon sx={{ fontSize: 60, mb: 2, opacity: 0.8 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                Sistema Integrado
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8 }}>
                Todas as funcionalidades em um só lugar
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Seção Sobre o Sistema */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            height: '100%', 
            background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
            border: '1px solid #2196f3'
          }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: '#2196f3', mx: 'auto', mb: 3, width: 64, height: 64 }}>
                <SpeedIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 2, color: '#1976d2' }}>
                Eficiência
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Processamento rápido de vendas e gestão otimizada de estoque para maximizar seus resultados.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            height: '100%', 
            background: 'linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)',
            border: '1px solid #4caf50'
          }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: '#4caf50', mx: 'auto', mb: 3, width: 64, height: 64 }}>
                <VerifiedIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 2, color: '#2e7d32' }}>
                Confiabilidade
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Sistema seguro e estável, com controle de acesso baseado em perfis e auditoria completa.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            height: '100%', 
            background: 'linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%)',
            border: '1px solid #ff9800'
          }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: '#ff9800', mx: 'auto', mb: 3, width: 64, height: 64 }}>
                <ExploreIcon sx={{ fontSize: 32 }} />
              </Avatar>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 2, color: '#f57c00' }}>
                Flexibilidade
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Interface intuitiva que se adapta ao seu perfil, oferecendo as funcionalidades certas no momento certo.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Seção para Clientes */}
      {isCustomer(user) && (
        <>
          <Typography variant="h4" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 4,
            fontWeight: 'bold',
            color: 'primary.main'
          }}>
            <AchievementIcon sx={{ mr: 2, fontSize: 40 }} />
            Sua Jornada de Compras
          </Typography>
          
          {/* Resumo Rápido */}
          <Paper sx={{ p: 4, mb: 4, bgcolor: 'background.default' }}>
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Bem-vindo à sua área pessoal
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  Aqui você pode acompanhar suas compras, explorar nosso catálogo de veículos e 
                  gerenciar seus pagamentos de forma simples e segura.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<ShoppingBagIcon />}
                    label={`${stats.myPurchases || 0} Compras`}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<CheckIcon />}
                    label={`${stats.paidPurchases || 0} Pagas`}
                    color="success"
                    variant="outlined"
                  />
                  {stats.pendingPurchases && stats.pendingPurchases > 0 && (
                    <Chip
                      icon={<PendingIcon />}
                      label={`${stats.pendingPurchases} Pendentes`}
                      color="warning"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Avatar sx={{ 
                    bgcolor: 'primary.main', 
                    mx: 'auto', 
                    mb: 2, 
                    width: 80, 
                    height: 80 
                  }}>
                    <PersonIcon sx={{ fontSize: 40 }} />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {user?.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cliente FIAP III
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          <Typography variant="h5" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 3,
            fontWeight: 'bold'
          }}>
            <ExploreIcon sx={{ mr: 1 }} />
            Explore & Compre
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <QuickActionCard
                title="Catálogo de Veículos"
                description="Descubra nossa seleção premium de veículos"
                icon={<VehicleIcon />}
                color="#1976d2"
                to="/vehicles"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <QuickActionCard
                title="Histórico de Compras"
                description="Acompanhe suas transações e pagamentos"
                icon={<ReceiptIcon />}
                color="#2e7d32"
                to="/my-purchases"
              />
            </Grid>
          </Grid>

          <Alert severity="info" icon={<OfferIcon />} sx={{ mb: 3 }}>
            <Typography variant="body1">
              <strong>Como funciona:</strong> Navegue pelo catálogo, visualize detalhes dos veículos e 
              clique em "Comprar" para finalizar sua compra instantaneamente. Seus dados já estão cadastrados!
            </Typography>
          </Alert>
        </>
      )}

             {(isAdmin(user) || isSales(user)) && (
        <>
          <Typography variant="h4" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 4,
            fontWeight: 'bold',
            color: 'primary.main'
          }}>
            <AdminIcon sx={{ mr: 2, fontSize: 40 }} />
            Central de Gestão
          </Typography>

          {/* Resumo Executivo */}
          <Paper sx={{ p: 4, mb: 4, bgcolor: 'background.default' }}>
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Bem-vindo ao seu painel de controle
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  Sua ferramenta completa para gerenciar operações, acompanhar performance 
                  e otimizar processos de vendas. Acesse relatórios detalhados e tome decisões baseadas em dados.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Chip
                    icon={<VehicleIcon />}
                    label={`${stats.totalVehicles} Veículos`}
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    icon={<SaleIcon />}
                    label={`${stats.totalSales} Vendas`}
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    icon={<TrendingIcon />}
                    label={formatCurrency(stats.totalRevenue)}
                    color="secondary"
                    variant="outlined"
                  />
                  {isAdmin(user) && (
                    <Chip
                      icon={<CustomerIcon />}
                      label={`${stats.totalCustomers} Clientes`}
                      color="info"
                      variant="outlined"
                    />
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Avatar sx={{ 
                    bgcolor: 'secondary.main', 
                    mx: 'auto', 
                    mb: 2, 
                    width: 80, 
                    height: 80 
                  }}>
                    {isAdmin(user) ? <AdminIcon sx={{ fontSize: 40 }} /> : <SellIcon sx={{ fontSize: 40 }} />}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {user?.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {getUserRoleDisplay()} FIAP III
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          <Typography variant="h5" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 3,
            fontWeight: 'bold'
          }}>
            <TrendingIcon sx={{ mr: 1 }} />
            Ferramentas de Gestão
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Catálogo de Veículos"
                description="Gerencie estoque, preços e disponibilidade"
                icon={<VehicleIcon />}
                color="#1976d2"
                to="/vehicles"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Controle de Vendas"
                description="Monitore transações e histórico de negociações"
                icon={<SaleIcon />}
                color="#2e7d32"
                to="/sales"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <QuickActionCard
                title="Gestão Financeira"
                description="Aprove pagamentos e acompanhe receitas"
                icon={<PaymentIcon />}
                color="#ed6c02"
                to="/payments"
                disabled={!canViewPayments(user)}
              />
            </Grid>
          </Grid>

          {isAdmin(user) && (
            <>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                  <QuickActionCard
                    title="Base de Clientes"
                    description="Cadastre novos clientes e gerencie informações"
                    icon={<CustomerIcon />}
                    color="#9c27b0"
                    to="/customers"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <QuickActionCard
                    title="Dashboard Executivo"
                    description="Relatórios avançados e métricas de performance"
                    icon={<DashboardIcon />}
                    color="#607d8b"
                    to="/dashboard"
                  />
                </Grid>
              </Grid>

              {/* Dica para Administradores */}
              <Alert severity="success" icon={<AchievementIcon />} sx={{ mb: 3 }}>
                <Typography variant="body1">
                  <strong>Acesso Total:</strong> Como administrador, você tem controle completo sobre o sistema. 
                  Use o Dashboard Executivo para análises detalhadas e métricas de performance.
                </Typography>
              </Alert>
            </>
          )}

          {isSales(user) && !isAdmin(user) && (
            <Alert severity="info" icon={<SellIcon />} sx={{ mb: 3 }}>
              <Typography variant="body1">
                <strong>Foco em Vendas:</strong> Suas ferramentas estão otimizadas para maximizar vendas. 
                Gerencie veículos, acompanhe negociações e aprove pagamentos com eficiência.
              </Typography>
            </Alert>
          )}

        </>
      )}


    </Container>
  );
};

export default Home; 