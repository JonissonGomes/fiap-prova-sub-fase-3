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
import { Sale, SaleCreate, Vehicle, VehicleStatus, PaymentStatus } from '../types';
import { salesApi, vehiclesApi } from '../services/api';
import InputMask from 'react-input-mask';
import { useAuth } from '../contexts/AuthContext';
import { canViewSales, canCreateSales } from '../utils/permissions';

interface SalesFilters {
  buyer_cpf?: string;
  payment_status?: PaymentStatus;
  vehicle_brand?: string;
  min_price?: number;
  max_price?: number;
  payment_code?: string;
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
  const [formData, setFormData] = useState<Partial<Sale>>({
    vehicle_id: '',
    buyer_cpf: '',
    sale_price: 0,
    payment_code: ''
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
      const data = await salesApi.list();
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

    // Filtro por CPF
    if (filters.buyer_cpf) {
      filtered = filtered.filter(sale => 
        sale.buyer_cpf.includes(filters.buyer_cpf!)
      );
    }

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

    // Filtro por preço mínimo
    if (filters.min_price) {
      filtered = filtered.filter(sale => sale.sale_price >= filters.min_price!);
    }

    // Filtro por preço máximo
    if (filters.max_price) {
      filtered = filtered.filter(sale => sale.sale_price <= filters.max_price!);
    }

    // Filtro por código de pagamento
    if (filters.payment_code) {
      filtered = filtered.filter(sale => 
        sale.payment_code.toLowerCase().includes(filters.payment_code!.toLowerCase())
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
      setFormData(sale);
      
      // Encontrar o veículo selecionado para o autocomplete
      const vehicle = vehicles.find(v => v.id === sale.vehicle_id);
      setSelectedVehicle(vehicle || null);
    } else {
      setSelectedSale(null);
      setSelectedVehicle(null);
      setFormData({
        vehicle_id: '',
        buyer_cpf: '',
        sale_price: 0,
        payment_code: ''
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
      buyer_cpf: '',
      sale_price: 0,
      payment_code: ''
    });
  };

  const handleVehicleChange = (event: any, newValue: Vehicle | null) => {
    setSelectedVehicle(newValue);
    setFormData(prev => ({
      ...prev,
      vehicle_id: newValue?.id || '',
      sale_price: newValue ? newValue.price : 0
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
    
    if (!formData.buyer_cpf) {
      newErrors.buyer_cpf = 'CPF é obrigatório';
    } else if (!/^\d{11}$/.test(formData.buyer_cpf)) {
      newErrors.buyer_cpf = 'CPF inválido';
    }
    
    if (!formData.sale_price || formData.sale_price <= 0) {
      newErrors.sale_price = 'Preço deve ser maior que zero';
    } else {
      const selectedVehicleData = vehicles.find(v => v.id === formData.vehicle_id);
      if (selectedVehicleData && formData.sale_price < selectedVehicleData.price) {
        newErrors.sale_price = 'Preço não pode ser menor que o preço do veículo';
      }
    }
    
    if (!formData.payment_code) {
      newErrors.payment_code = 'Código de pagamento é obrigatório';
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
        const saleData = {
          vehicle_id: formData.vehicle_id,
          buyer_cpf: formData.buyer_cpf,
          sale_price: formData.sale_price,
          payment_code: formData.payment_code,
          payment_status: formData.payment_status
        };
        await salesApi.update(selectedSale.id, saleData);
        setSnackbar({
          open: true,
          message: 'Venda atualizada com sucesso',
          severity: 'success'
        });
      } else {
        // Cria uma nova venda
        const saleData: SaleCreate = {
          vehicle_id: formData.vehicle_id!,
          buyer_cpf: formData.buyer_cpf!,
          sale_price: formData.sale_price!,
          payment_code: formData.payment_code!,
          payment_status: PaymentStatus.PENDING
        };
        
        const newSale = await salesApi.create(saleData);

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
        await salesApi.delete(id);
        setSales(prevSales => prevSales.filter(sale => sale.id !== id));
        setSnackbar({
          open: true,
          message: 'Venda excluída com sucesso',
          severity: 'success'
        });
        setTimeout(() => {
          fetchSales();
        }, 500);
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
          await salesApi.updateStatus(id, 'PENDING');
          await vehiclesApi.updateStatus(sale.vehicle_id, 'DISPONÍVEL');
          break;
        case PaymentStatus.PAID:
          await salesApi.confirmPayment(id);
          await vehiclesApi.updateStatus(sale.vehicle_id, 'VENDIDO');
          break;
        case PaymentStatus.CANCELLED:
          await salesApi.cancelPayment(id);
          await vehiclesApi.updateStatus(sale.vehicle_id, 'DISPONÍVEL');
          break;
      }
      setSnackbar({
        open: true,
        message: 'Status atualizado com sucesso',
        severity: 'success'
      });
      
      fetchSales();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao atualizar status',
        severity: 'error'
      });
    }
  };

  const getStatusText = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.PENDING:
        return 'Pendente';
      case PaymentStatus.PAID:
        return 'Pago';
      case PaymentStatus.CANCELLED:
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getStatusColor = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.PENDING:
        return 'warning';
      case PaymentStatus.PAID:
        return 'success';
      case PaymentStatus.CANCELLED:
        return 'error';
      default:
        return 'default';
    }
  };

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
    { field: 'buyer_cpf', headerName: 'CPF do Comprador', flex: 1.3, minWidth: 130, align: 'center' as const, headerAlign: 'center' as const },
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
      field: 'actions',
      headerName: 'Ações',
      flex: 1,
      minWidth: 100,
      align: 'center' as const,
      headerAlign: 'center' as const,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
          <IconButton onClick={() => handleOpenDialog(params.row)} size="small">
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton onClick={() => handleDelete(params.row.id)} size="small" color="error">
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      )
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
                  label="CPF do Comprador"
                  value={filters.buyer_cpf || ''}
                  onChange={(e) => handleFilterChange('buyer_cpf', e.target.value || undefined)}
                />
              </Grid>
              
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
                  label="Código de Pagamento"
                  value={filters.payment_code || ''}
                  onChange={(e) => handleFilterChange('payment_code', e.target.value || undefined)}
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
                value={formData.buyer_cpf}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                  setFormData({ ...formData, buyer_cpf: e.target.value.replace(/\D/g, '') })
                }
              >
                {(inputProps: any) => (
                  <TextField
                    {...inputProps}
                    fullWidth
                    label="CPF do Cliente"
                    error={!!errors.buyer_cpf}
                    helperText={errors.buyer_cpf}
                    required
                  />
                )}
              </InputMask>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Preço da Venda"
                value={formatCurrency(formData.sale_price || 0)}
                onChange={(e) => {
                  const numericValue = parseCurrency(e.target.value);
                  setFormData({ ...formData, sale_price: numericValue });
                }}
                error={!!errors.sale_price}
                helperText={errors.sale_price}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Código de Pagamento"
                value={formData.payment_code}
                onChange={(e) => setFormData({ ...formData, payment_code: e.target.value })}
                error={!!errors.payment_code}
                helperText={errors.payment_code}
                required
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