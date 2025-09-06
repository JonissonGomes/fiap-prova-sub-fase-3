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
  Autocomplete,
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
  Search as SearchIcon
} from '@mui/icons-material';
import { Sale, SaleCreate, SaleUpdate, Vehicle, VehicleStatus, PaymentStatus } from '../types';
import { salesService, vehiclesApi, customerService } from '../services/api';
import InputMask from 'react-input-mask';
import { NumericFormat } from 'react-number-format';
import { useAuth } from '../contexts/AuthContext';
import { canViewSales, canCreateSales } from '../utils/permissions';
import { triggerDataRefresh, DATA_REFRESH_EVENTS } from '../utils/dataRefresh';

interface SalesFilters {
  customer_cpf?: string;
  status?: string;
  vehicle_brand?: string;
  min_price?: number;
  max_price?: number;
  payment_method?: string;
}

const Sales: React.FC = () => {
  const { user } = useAuth();
  const [sales, setSales] = useState<Sale[]>([]);
  const [filteredSales, setFilteredSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [availableVehicles, setAvailableVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSale, setSelectedSale] = useState<Sale | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SalesFilters>({});
  const [formData, setFormData] = useState({
    vehicle_id: '',
    customer_cpf: '',
    payment_method: 'PIX',
    notes: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    fetchSales();
    fetchVehicles();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [sales, filters]);

  const fetchSales = async () => {
    try {
      const data = await salesService.list();
      setSales(data);
    } catch (error) {
      console.error('Error fetching sales:', error);
    }
  };

  const fetchVehicles = async () => {
    try {
      const data = await vehiclesApi.list();
      if (!Array.isArray(data)) {
        throw new Error('Dados de veículos não retornados em formato esperado');
      }
      setVehicles(data);
      
      // Filtrar apenas veículos disponíveis para o autocomplete
      const available = data.filter(vehicle => vehicle.status === VehicleStatus.AVAILABLE);
      setAvailableVehicles(available);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao carregar veículos. Verifique se o serviço está rodando.',
        severity: 'error'
      });
      setVehicles([]);
      setAvailableVehicles([]);
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

    // Filtro por marca do veículo
    if (filters.vehicle_brand) {
      filtered = filtered.filter(sale => {
        const vehicle = sale.vehicle_id;
        return vehicle?.brand?.toLowerCase().includes(filters.vehicle_brand!.toLowerCase());
      });
    }

    // Filtro por preço mínimo
    if (filters.min_price) {
      filtered = filtered.filter(sale => sale.final_amount >= filters.min_price!);
    }

    // Filtro por preço máximo
    if (filters.max_price) {
      filtered = filtered.filter(sale => sale.final_amount <= filters.max_price!);
    }

    // Filtro por método de pagamento
    if (filters.payment_method) {
      filtered = filtered.filter(sale => 
        sale.payment_method.toLowerCase().includes(filters.payment_method!.toLowerCase())
      );
    }

    setFilteredSales(filtered);
  };

  const handleFilterChange = (field: keyof SalesFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value || undefined
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const handleOpenDialog = (sale?: Sale) => {
    if (sale) {
      setSelectedSale(sale);
      setFormData({
        vehicle_id: sale.vehicle_id?.id || '',
        customer_cpf: sale.customer_id?.cpf || '',
        payment_method: sale.payment_method || 'PIX',
        notes: sale.notes || ''
      });
      
      // Encontrar o veículo selecionado para o autocomplete
      const vehicle = vehicles.find(v => v.id === sale.vehicle_id?.id);
      setSelectedVehicle(vehicle || null);
    } else {
      setSelectedSale(null);
      setSelectedVehicle(null);
      setFormData({
        vehicle_id: '',
        customer_cpf: '',
        payment_method: 'PIX',
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedSale(null);
    setSelectedVehicle(null);
    setFormData({
      vehicle_id: '',
      customer_cpf: '',
      payment_method: 'PIX',
      notes: ''
    });
  };

  const handleVehicleChange = (event: any, newValue: Vehicle | null) => {
    setSelectedVehicle(newValue);
    setFormData(prev => ({
      ...prev,
      vehicle_id: newValue?.id || ''
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const parseCurrency = (value: string) => {
    const numericValue = value.replace(/[^\d,]/g, '').replace(',', '.');
    return parseFloat(numericValue) || 0;
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.vehicle_id) {
      newErrors.vehicle_id = 'Veículo é obrigatório';
    }
    
    if (!formData.customer_cpf) {
      newErrors.customer_cpf = 'CPF é obrigatório';
    } else if (!/^\d{11}$/.test(formData.customer_cpf)) {
      newErrors.customer_cpf = 'CPF inválido';
    }
    
    if (!formData.payment_method) {
      newErrors.payment_method = 'Método de pagamento é obrigatório';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      if (selectedSale) {
        // Envia apenas os campos necessários para atualização
        const saleData: SaleUpdate = {
          payment_method: formData.payment_method,
          notes: formData.notes
        };
        await salesService.update(selectedSale.id, saleData);
        setSnackbar({
          open: true,
          message: 'Venda atualizada com sucesso',
          severity: 'success'
        });
      } else {
        // Cria uma nova venda - primeiro buscar customer pelo CPF
        const customers = await customerService.list();
        const customer = customers.find(c => c.cpf === formData.customer_cpf);
        
        if (!customer) {
          setSnackbar({
            open: true,
            message: 'Cliente não encontrado com este CPF',
            severity: 'error'
          });
          return;
        }
        
        const saleData: SaleCreate = {
          customer_id: customer.id,
          vehicle_id: formData.vehicle_id!,
          payment_method: formData.payment_method,
          notes: formData.notes
        };
        
        const newSale = await salesService.create(saleData);

        // Marca o veículo como reservado
        if (newSale && formData.vehicle_id) {
          await vehiclesApi.updateStatus(formData.vehicle_id, 'RESERVADO');
        }
        
        setSnackbar({
          open: true,
          message: 'Venda criada com sucesso',
          severity: 'success'
        });
      }
      await fetchSales();
      await fetchVehicles(); // Atualizar veículos também, pois o status pode ter mudado
      
      // Notificar outras páginas sobre mudanças
      triggerDataRefresh(DATA_REFRESH_EVENTS.SALES);
      triggerDataRefresh(DATA_REFRESH_EVENTS.VEHICLES);
      
      handleCloseDialog();
    } catch (error) {
      console.error('Erro ao salvar venda:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao salvar venda',
        severity: 'error'
      });
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir esta venda?')) {
      try {
        await salesService.delete(id);
        setSnackbar({
          open: true,
          message: 'Venda excluída com sucesso',
          severity: 'success'
        });
        // Atualizar listas imediatamente
        fetchSales();
        fetchVehicles(); // Atualizar veículos também, pois o status pode ter mudado
        
        // Notificar outras páginas sobre mudanças
        triggerDataRefresh(DATA_REFRESH_EVENTS.SALES);
        triggerDataRefresh(DATA_REFRESH_EVENTS.VEHICLES);
      } catch (error) {
        console.error('Error deleting sale:', error);
        setSnackbar({
          open: true,
          message: 'Erro ao excluir venda',
          severity: 'error'
        });
      }
    }
  };

  const handleStatusChange = async (id: string, status: PaymentStatus) => {
    try {
      const sale = sales.find(s => s.id === id);
      if (!sale) return;

      switch (status) {
        case PaymentStatus.PENDING:
          await salesService.updateStatus(id, 'PENDING');
          await vehiclesApi.updateStatus(sale.vehicle_id?.id || sale.vehicle_id, 'DISPONÍVEL');
          break;
        case PaymentStatus.PAID:
          await salesService.confirmPayment(id);
          await vehiclesApi.updateStatus(sale.vehicle_id?.id || sale.vehicle_id, 'VENDIDO');
          break;
        case PaymentStatus.CANCELLED:
          await salesService.cancelPayment(id);
          await vehiclesApi.updateStatus(sale.vehicle_id?.id || sale.vehicle_id, 'DISPONÍVEL');
          break;
      }
      setSnackbar({
        open: true,
        message: 'Status atualizado com sucesso',
        severity: 'success'
      });
      
      fetchSales();
      fetchVehicles(); // Atualizar veículos também, pois o status pode ter mudado
      
      // Notificar outras páginas sobre mudanças
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

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PENDENTE':
        return 'Pendente';
      case 'PAGO':
        return 'Pago';
      case 'CANCELADO':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDENTE':
        return 'warning';
      case 'PAGO':
        return 'success';
      case 'CANCELADO':
        return 'error';
      default:
        return 'default';
    }
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
      flex: 1,
      minWidth: 100,
      align: 'center' as const,
      headerAlign: 'center' as const,
      sortable: false,
      renderCell: (params) => {
        // Não mostrar ações para vendas pagas
        if (params.row.status === 'PAGO') {
          return (
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Finalizada
              </Typography>
            </Box>
          );
        }

        return (
          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
            <IconButton onClick={() => handleOpenDialog(params.row)} size="small">
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton onClick={() => handleDelete(params.row.id)} size="small" color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        );
      }
    }
  ];

  if (!canViewSales(user)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Você não tem permissão para acessar esta página.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Gerenciamento de Vendas
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gerencie todas as vendas realizadas no sistema
          </Typography>
        </Box>
        
        {canCreateSales(user) && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            sx={{ minWidth: 140, height: 42 }}
          >
            Nova Venda
          </Button>
        )}
      </Box>

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
                  label="Marca do Veículo"
                  value={filters.vehicle_brand || ''}
                  onChange={(e) => handleFilterChange('vehicle_brand', e.target.value || undefined)}
                />
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
              
              <Grid item xs={12} sm={6} md={2}>
                <Button
                  onClick={clearFilters}
                  variant="outlined"
                  fullWidth
                  size="small"
                  startIcon={<SearchIcon />}
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
                      Nenhuma venda encontrada
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Object.keys(filters).length > 0 
                        ? 'Tente ajustar os filtros ou cadastre uma nova venda.'
                        : 'Cadastre a primeira venda para começar.'
                      }
                    </Typography>
                  </Box>
                )
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Dialog de Criação/Edição */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedSale ? 'Editar Venda' : 'Nova Venda'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Autocomplete
                value={selectedVehicle}
                onChange={handleVehicleChange}
                options={availableVehicles}
                getOptionLabel={(option) => `${option.brand} ${option.model} - ${option.year} (${formatCurrency(option.price)})`}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Veículo"
                    error={!!errors.vehicle_id}
                    helperText={errors.vehicle_id}
                    required
                    placeholder="Digite para buscar um veículo..."
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props}>
                    <Box>
                      <Typography variant="body1">
                        {option.brand} {option.model} - {option.year}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Cor: {option.color} | Preço: {formatCurrency(option.price)}
                      </Typography>
                    </Box>
                  </Box>
                )}
                filterOptions={(options, { inputValue }) => {
                  const filtered = options.filter((option) => {
                    const searchText = inputValue.toLowerCase();
                    return (
                      option.brand.toLowerCase().includes(searchText) ||
                      option.model.toLowerCase().includes(searchText) ||
                      option.year.toString().includes(searchText) ||
                      option.color.toLowerCase().includes(searchText)
                    );
                  });
                  return filtered;
                }}
                noOptionsText="Nenhum veículo disponível encontrado"
                loadingText="Carregando veículos..."
                clearText="Limpar"
                closeText="Fechar"
                openText="Abrir"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12}>
              <InputMask
                mask="999.999.999-99"
                value={formData.customer_cpf}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                  setFormData({ ...formData, customer_cpf: e.target.value.replace(/\D/g, '') })
                }
              >
                {(inputProps: any) => (
                  <TextField
                    {...inputProps}
                    fullWidth
                    label="CPF do Cliente"
                    error={!!errors.customer_cpf}
                    helperText={errors.customer_cpf}
                    required
                  />
                )}
              </InputMask>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth error={!!errors.payment_method}>
                <InputLabel>Método de Pagamento</InputLabel>
                <Select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  label="Método de Pagamento"
                  required
                >
                  <MenuItem value="PIX">PIX</MenuItem>
                  <MenuItem value="DINHEIRO">Dinheiro</MenuItem>
                  <MenuItem value="CARTAO_CREDITO">Cartão de Crédito</MenuItem>
                  <MenuItem value="CARTAO_DEBITO">Cartão de Débito</MenuItem>
                  <MenuItem value="FINANCIAMENTO">Financiamento</MenuItem>
                </Select>
                {errors.payment_method && (
                  <Typography variant="caption" color="error" sx={{ ml: 2, mt: 0.5 }}>
                    {errors.payment_method}
                  </Typography>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Observações"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Observações sobre a venda..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button onClick={handleSubmit} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

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

export default Sales;