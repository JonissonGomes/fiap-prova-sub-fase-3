import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Container,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Collapse,
  SelectChangeEvent
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { 
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  ShoppingBag as ShoppingBagIcon,
  Receipt as ReceiptIcon,
  TrendingUp as TrendingIcon,
  ShoppingCart as ShoppingCartIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
  AttachMoney as AttachMoneyIcon
} from '@mui/icons-material';
import { Sale, Vehicle, PaymentStatus } from '../types';
import { salesApi, vehiclesApi, customerService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { isCustomer } from '../utils/permissions';

interface PurchaseFilters {
  payment_status?: PaymentStatus;
  vehicle_brand?: string;
  vehicle_model?: string;
  min_price?: number;
  max_price?: number;
  date_range?: 'all' | 'last_month' | 'last_3_months' | 'last_year';
}

const MyPurchases: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [filteredSales, setFilteredSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [customerCpf, setCustomerCpf] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<PurchaseFilters>({});

  const { user } = useAuth();

  useEffect(() => {
    if (user && isCustomer(user)) {
      fetchCustomerData();
    }
  }, [user]);

  useEffect(() => {
    applyFilters();
  }, [sales, filters]);

  const fetchCustomerData = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      
      // Buscar dados do cliente para obter o CPF
      const customers = await customerService.list();
      const customer = customers.find(c => c.email === user.email);
      
      if (!customer) {
        setError('Dados do cliente não encontrados');
        return;
      }
      
      setCustomerCpf(customer.cpf);
      
      // Buscar vendas do cliente
      const allSales = await salesApi.list();
      const customerSales = allSales.filter(sale => sale.buyer_cpf === customer.cpf);
      setSales(customerSales);
      
      // Buscar veículos relacionados
      const allVehicles = await vehiclesApi.list();
      setVehicles(allVehicles);
      
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      setError('Erro ao carregar suas compras');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...sales];

    // Filtro por status de pagamento
    if (filters.payment_status) {
      filtered = filtered.filter(sale => 
        sale.payment_status === filters.payment_status
      );
    }

    // Filtro por marca do veículo
    if (filters.vehicle_brand) {
      filtered = filtered.filter(sale => {
        const vehicle = vehicles.find(v => v.id === sale.vehicle_id);
        return vehicle && vehicle.brand.toLowerCase().includes(filters.vehicle_brand!.toLowerCase());
      });
    }

    // Filtro por modelo do veículo
    if (filters.vehicle_model) {
      filtered = filtered.filter(sale => {
        const vehicle = vehicles.find(v => v.id === sale.vehicle_id);
        return vehicle && vehicle.model.toLowerCase().includes(filters.vehicle_model!.toLowerCase());
      });
    }

    // Filtro por preço mínimo
    if (filters.min_price) {
      filtered = filtered.filter(sale => sale.sale_price >= filters.min_price!);
    }

    // Filtro por preço máximo
    if (filters.max_price) {
      filtered = filtered.filter(sale => sale.sale_price <= filters.max_price!);
    }

    // Filtro por data
    if (filters.date_range && filters.date_range !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (filters.date_range) {
        case 'last_month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case 'last_3_months':
          filterDate.setMonth(now.getMonth() - 3);
          break;
        case 'last_year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      filtered = filtered.filter(sale => {
        const saleDate = new Date(sale.created_at);
        return saleDate >= filterDate;
      });
    }

    setFilteredSales(filtered);
  };

  const handleFilterChange = (field: keyof PurchaseFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value || undefined
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
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

  // Estatísticas das compras
  const totalCompras = filteredSales.length;
  const comprasPendentes = filteredSales.filter(s => s.payment_status === PaymentStatus.PENDING).length;
  const comprasPagas = filteredSales.filter(s => s.payment_status === PaymentStatus.PAID).length;
  const comprasCanceladas = filteredSales.filter(s => s.payment_status === PaymentStatus.CANCELLED).length;
  const valorTotal = filteredSales.reduce((sum, sale) => sum + sale.sale_price, 0);

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', flex: 0.4, minWidth: 70, align: 'center' as const, headerAlign: 'center' as const },
    { 
      field: 'vehicle_id', 
      headerName: 'Veículo', 
      flex: 2.2,
      minWidth: 160,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => {
        const vehicle = vehicles.find(v => v.id === params.value);
        return vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.year})` : params.value;
      }
    },
    { 
      field: 'sale_price', 
      headerName: 'Preço', 
      flex: 1.1,
      minWidth: 110,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => formatCurrency(params.value)
    },
    { field: 'payment_code', headerName: 'Código de Pagamento', flex: 1.4, minWidth: 130, align: 'center' as const, headerAlign: 'center' as const },
    { 
      field: 'payment_status', 
      headerName: 'Status', 
      flex: 1,
      minWidth: 100,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => (
        <Chip
          label={getStatusText(params.value)}
          color={getStatusColor(params.value) as any}
          size="small"
          sx={{ 
            minWidth: 80,
            height: 24,
            fontSize: '0.75rem',
            fontWeight: 500,
            '& .MuiChip-label': {
              px: 1
            }
          }}
        />
      )
    },
    {
      field: 'created_at',
      headerName: 'Data da Compra',
      flex: 1.2,
      minWidth: 130,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => {
        const date = new Date(params.value);
        return date.toLocaleDateString('pt-BR');
      }
    }
  ];

  // Verificar se o usuário é cliente
  if (!isCustomer(user)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Esta página é apenas para clientes.
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Minhas Compras
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Acompanhe o histórico e status de suas compras
          </Typography>
        </Box>
      </Box>

      {/* Cards de Estatísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'primary.light', borderRadius: 1 }}>
                  <ShoppingCartIcon color="primary" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {filteredSales.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Compras
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'success.light', borderRadius: 1 }}>
                  <CheckCircleIcon color="success" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {filteredSales.filter(s => s.payment_status === PaymentStatus.PAID).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pagas
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'warning.light', borderRadius: 1 }}>
                  <PendingIcon color="warning" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {filteredSales.filter(s => s.payment_status === PaymentStatus.PENDING).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pendentes
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'secondary.light', borderRadius: 1 }}>
                  <AttachMoneyIcon color="secondary" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {formatCurrency(filteredSales.reduce((sum, sale) => sum + sale.sale_price, 0))}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Valor Total
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Filtros</Typography>
            <Button
              onClick={() => setShowFilters(!showFilters)}
              startIcon={showFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              variant="outlined"
              size="small"
            >
              {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
            </Button>
          </Box>
          
          <Collapse in={showFilters}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status do Pagamento</InputLabel>
                  <Select
                    value={filters.payment_status || ''}
                    label="Status do Pagamento"
                    onChange={(e: SelectChangeEvent) => handleFilterChange('payment_status', e.target.value as PaymentStatus || undefined)}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value={PaymentStatus.PENDING}>Pendente</MenuItem>
                    <MenuItem value={PaymentStatus.PAID}>Pago</MenuItem>
                    <MenuItem value={PaymentStatus.CANCELLED}>Cancelado</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Marca do Veículo"
                  value={filters.vehicle_brand || ''}
                  onChange={(e) => handleFilterChange('vehicle_brand', e.target.value || undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Modelo do Veículo"
                  value={filters.vehicle_model || ''}
                  onChange={(e) => handleFilterChange('vehicle_model', e.target.value || undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Período</InputLabel>
                  <Select
                    value={filters.date_range || ''}
                    label="Período"
                    onChange={(e: SelectChangeEvent) => handleFilterChange('date_range', e.target.value || undefined)}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value="last_month">Último mês</MenuItem>
                    <MenuItem value="last_3_months">Últimos 3 meses</MenuItem>
                    <MenuItem value="last_year">Último ano</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Preço Mínimo"
                  type="number"
                  value={filters.min_price || ''}
                  onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Preço Máximo"
                  type="number"
                  value={filters.max_price || ''}
                  onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  onClick={clearFilters}
                  variant="outlined"
                  fullWidth
                  size="small"
                >
                  Limpar Filtros
                </Button>
              </Grid>
            </Grid>
          </Collapse>
        </CardContent>
      </Card>

      {/* DataGrid */}
      <Card>
        <CardContent sx={{ p: 2 }}>
          <Box sx={{ height: 650, width: '100%' }}>
            <DataGrid
              rows={filteredSales}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: { pageSize: 10 }
                }
              }}
              pageSizeOptions={[10, 25, 50]}
              disableRowSelectionOnClick
              density="standard"
              sx={{
                '& .MuiDataGrid-cell': {
                  borderBottom: 'none',
                  fontSize: '0.875rem',
                  padding: '8px 12px',
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiDataGrid-columnHeader': {
                    backgroundColor: 'primary.main',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    padding: '12px',
                  },
                },
                '& .MuiDataGrid-row': {
                  minHeight: 52,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                },
              }}
              slots={{
                noRowsOverlay: () => (
                  <Box
                    sx={{
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexDirection: 'column',
                      gap: 2
                    }}
                  >
                    <Typography variant="h6" color="text.secondary">
                      Nenhuma compra encontrada
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Object.keys(filters).length > 0 
                        ? 'Tente ajustar os filtros para encontrar suas compras.'
                        : 'Você ainda não realizou nenhuma compra.'
                      }
                    </Typography>
                  </Box>
                )
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Instruções para pagamento */}
      {comprasPendentes > 0 && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body1">
            <strong>Instruções para Pagamento:</strong><br />
            • Você tem {comprasPendentes} compra(s) pendente(s)<br />
            • Use o código de pagamento para efetuar o pagamento<br />
            • Após o pagamento, aguarde a confirmação do vendedor<br />
            • Em caso de dúvidas, entre em contato com nossa equipe
          </Typography>
        </Alert>
      )}
    </Container>
  );
};

export default MyPurchases; 