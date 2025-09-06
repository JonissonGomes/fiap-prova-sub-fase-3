import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Paper,
  TextField,
  Typography,
  IconButton,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Alert,
  Snackbar,
  Container,
  Card,
  CardContent,
  Collapse,
  Chip,
  SelectChangeEvent
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Pending as PendingIcon,
  AttachMoney as AttachMoneyIcon
} from '@mui/icons-material';
import { Payment, Sale, Vehicle, PaymentStatus } from '../types';
import { salesService, vehiclesApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { canViewPayments, canApprovePayments, canCancelPayments } from '../utils/permissions';
import { triggerDataRefresh, onDataRefresh, DATA_REFRESH_EVENTS } from '../utils/dataRefresh';

interface PaymentsFilters {
  customer_cpf?: string;
  status?: string;
  payment_method?: string;
  vehicle_brand?: string;
  min_amount?: number;
  max_amount?: number;
}

const Payments: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [filteredSales, setFilteredSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSale, setSelectedSale] = useState<Sale | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<PaymentsFilters>({});
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const { user } = useAuth();

  useEffect(() => {
    fetchSales();
    fetchVehicles();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [sales, filters]);

  // Escutar mudanças de dados
  useEffect(() => {
    const cleanup = onDataRefresh(DATA_REFRESH_EVENTS.SALES, () => {
      fetchSales();
    });

    return cleanup;
  }, []);

  const fetchSales = async () => {
    try {
      const data = await salesService.list();
      // Filtrar apenas vendas que não estão canceladas
      const activeSales = data.filter(sale => sale.status !== 'CANCELADO');
      setSales(activeSales);
    } catch (error) {
      console.error('Error fetching sales:', error);
    }
  };

  const fetchVehicles = async () => {
    try {
      const data = await vehiclesApi.list();
      setVehicles(data);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...sales];

    // Filtro por CPF do cliente
    if (filters.customer_cpf) {
      filtered = filtered.filter(sale => {
        const customer = sale.customer_id;
        return customer?.cpf?.includes(filters.customer_cpf!);
      });
    }

    // Filtro por status
    if (filters.status) {
      filtered = filtered.filter(sale => sale.status === filters.status);
    }

    // Filtro por método de pagamento
    if (filters.payment_method) {
      filtered = filtered.filter(sale => 
        sale.payment_method.toLowerCase().includes(filters.payment_method!.toLowerCase())
      );
    }

    // Filtro por marca do veículo
    if (filters.vehicle_brand) {
      filtered = filtered.filter(sale => {
        const vehicle = vehicles.find(v => v.id === sale.vehicle_id);
        return vehicle && vehicle.brand.toLowerCase().includes(filters.vehicle_brand!.toLowerCase());
      });
    }

    // Filtro por valor mínimo
    if (filters.min_amount) {
      filtered = filtered.filter(sale => sale.final_amount >= filters.min_amount!);
    }

    // Filtro por valor máximo
    if (filters.max_amount) {
      filtered = filtered.filter(sale => sale.final_amount <= filters.max_amount!);
    }

    setFilteredSales(filtered);
  };

  const handleFilterChange = (field: keyof PaymentsFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value || undefined
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PAGO':
        return 'Aprovado';
      case 'PENDENTE':
        return 'Pendente';
      case 'CANCELADO':
        return 'Cancelado';
      default:
        return status;
    }
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

  const handleStatusChange = async (saleId: string, status: string) => {
    // Verificar permissões
    if (status === 'PAGO' && !canApprovePayments(user)) {
      setSnackbar({
        open: true,
        message: 'Você não tem permissão para aprovar pagamentos',
        severity: 'error'
      });
      return;
    }

    if (status === 'CANCELADO' && !canCancelPayments(user)) {
      setSnackbar({
        open: true,
        message: 'Você não tem permissão para cancelar pagamentos',
        severity: 'error'
      });
      return;
    }

    try {
      const sale = sales.find(s => s.id === saleId);
      if (!sale) return;

      switch (status) {
        case 'PAGO':
          // Notificar webhook de pagamento
          await salesService.confirmPayment(saleId);
          await vehiclesApi.updateStatus(sale.vehicle_id?.id || sale.vehicle_id, 'VENDIDO');
          break;
        case 'CANCELADO':
          await salesService.cancelPayment(saleId);
          await vehiclesApi.updateStatus(sale.vehicle_id?.id || sale.vehicle_id, 'DISPONÍVEL');
          break;
      }
      
      setSnackbar({
        open: true,
        message: 'Status atualizado com sucesso',
        severity: 'success'
      });
      
      fetchSales();
      triggerDataRefresh(DATA_REFRESH_EVENTS.SALES);
      triggerDataRefresh(DATA_REFRESH_EVENTS.VEHICLES);
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao atualizar status',
        severity: 'error'
      });
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const columns: GridColDef[] = [
    { 
      field: 'vehicle_id', 
      headerName: 'Veículo', 
      flex: 2.2,
      minWidth: 160,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => {
        const vehicle = params.value;
        return vehicle && typeof vehicle === 'object' 
          ? `${vehicle.brand} ${vehicle.model} (${vehicle.year})` 
          : 'N/A';
      }
    },
    { 
      field: 'customer_id', 
      headerName: 'Cliente', 
      flex: 1.3, 
      minWidth: 130, 
      align: 'center' as const, 
      headerAlign: 'center' as const,
      renderCell: (params) => params.value?.name || 'N/A'
    },
    { 
      field: 'final_amount', 
      headerName: 'Valor Final', 
      flex: 1.1,
      minWidth: 110,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => formatCurrency(params.value)
    },
    { field: 'payment_method', headerName: 'Método de Pagamento', flex: 1.4, minWidth: 130, align: 'center' as const, headerAlign: 'center' as const },
    { 
      field: 'status', 
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
      field: 'actions',
      headerName: 'Ações',
      flex: 1.5,
      minWidth: 120,
      align: 'center' as const,
      headerAlign: 'center' as const,
      sortable: false,
      renderCell: (params) => {
        // Apenas administradores podem ver as ações
        if (!canApprovePayments(user) && !canCancelPayments(user)) {
          return (
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Somente administradores
              </Typography>
            </Box>
          );
        }

        return (
          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
            {params.row.status === 'PENDENTE' && canApprovePayments(user) && (
              <Button
                onClick={() => handleStatusChange(params.row.id, 'PAGO')}
                color="success"
                variant="outlined"
                size="small"
              >
                Aprovar
              </Button>
            )}
            {params.row.status === 'PENDENTE' && canCancelPayments(user) && (
              <Button
                onClick={() => handleStatusChange(params.row.id, 'CANCELADO')}
                color="error"
                variant="outlined"
                size="small"
              >
                Cancelar
              </Button>
            )}
          </Box>
        );
      }
    }
  ];

  // Verificar se o usuário tem permissão para ver pagamentos
  if (!canViewPayments(user)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Você não tem permissão para acessar esta página.
        </Alert>
      </Container>
    );
  }

  const pendingCount = filteredSales.filter(s => s.status === 'PENDENTE').length;
  const approvedCount = filteredSales.filter(s => s.status === 'PAGO').length;
  const totalAmount = filteredSales.reduce((sum, sale) => sum + sale.final_amount, 0);
  const pendingTotal = filteredSales.filter(s => s.status === 'PENDENTE').reduce((sum, sale) => sum + sale.final_amount, 0);
  const approvedTotal = filteredSales.filter(s => s.status === 'PAGO').reduce((sum, sale) => sum + sale.final_amount, 0);

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {canApprovePayments(user) || canCancelPayments(user) 
              ? 'Gerenciamento de Pagamentos' 
              : 'Visualização de Pagamentos'
            }
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {canApprovePayments(user) || canCancelPayments(user)
              ? 'Gerencie e aprove pagamentos das vendas realizadas'
              : 'Visualize o status dos pagamentos das vendas realizadas'
            }
          </Typography>
        </Box>
      </Box>

      {/* Cards de Resumo */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'warning.light', borderRadius: 1 }}>
                  <PendingIcon color="warning" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {formatCurrency(pendingTotal)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pendentes ({pendingCount})
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'success.light', borderRadius: 1 }}>
                  <CheckCircleIcon color="success" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {formatCurrency(approvedTotal)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Aprovados ({approvedCount})
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'primary.light', borderRadius: 1 }}>
                  <AttachMoneyIcon color="primary" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {formatCurrency(totalAmount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total ({sales.length})
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>Filtros</Typography>
            <Button
              onClick={() => setShowFilters(!showFilters)}
              startIcon={showFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              variant="outlined"
              size="small"
              sx={{ minWidth: 140 }}
            >
              {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
            </Button>
          </Box>
          
          <Collapse in={showFilters}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="CPF do Cliente"
                  value={filters.customer_cpf || ''}
                  onChange={(e) => handleFilterChange('customer_cpf', e.target.value || undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={filters.status || ''}
                    label="Status"
                    onChange={(e: SelectChangeEvent) => handleFilterChange('status', e.target.value || undefined)}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value="PENDENTE">Pendente</MenuItem>
                    <MenuItem value="PAGO">Pago</MenuItem>
                    <MenuItem value="CANCELADO">Cancelado</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Método de Pagamento"
                  value={filters.payment_method || ''}
                  onChange={(e) => handleFilterChange('payment_method', e.target.value || undefined)}
                />
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
                  label="Valor Mínimo"
                  type="number"
                  value={filters.min_amount || ''}
                  onChange={(e) => handleFilterChange('min_amount', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Valor Máximo"
                  type="number"
                  value={filters.max_amount || ''}
                  onChange={(e) => handleFilterChange('max_amount', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={2}>
                <Button
                  onClick={clearFilters}
                  variant="outlined"
                  fullWidth
                  size="small"
                  sx={{ height: 40 }}
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
        <CardContent sx={{ p: 3 }}>
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
                      Nenhum pagamento encontrado
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Object.keys(filters).length > 0 
                        ? 'Tente ajustar os filtros para encontrar pagamentos.'
                        : 'Aguarde as primeiras vendas para gerenciar pagamentos.'
                      }
                    </Typography>
                  </Box>
                )
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Snackbar para notificações */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Payments; 