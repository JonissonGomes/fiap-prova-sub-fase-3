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
  SelectChangeEvent,
  Chip,
  Alert,
  Snackbar,
  Container,
  Card,
  CardContent,
  Collapse
} from '@mui/material';
import { DataGrid, GridColDef, GridSortModel } from '@mui/x-data-grid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  FilterList as FilterIcon,
  ShoppingCart as ShoppingCartIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { NumericFormat } from 'react-number-format';
import { Vehicle, VehicleCreate, VehicleStatus, VehicleFilters } from '../types';
import { vehiclesApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { 
  canViewVehicles, 
  canCreateVehicles, 
  canEditVehicles, 
  canDeleteVehicles, 
  canBuyVehicles,
  isCustomer
} from '../utils/permissions';
import PurchaseDialog from '../components/PurchaseDialog';

interface LocalFilters {
  brand?: string;
  model?: string;
  status?: VehicleStatus;
  min_price?: number;
  max_price?: number;
}

const VehiclesWithRoles: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [purchaseDialogOpen, setPurchaseDialogOpen] = useState(false);
  const [vehicleToPurchase, setVehicleToPurchase] = useState<Vehicle | null>(null);
  const [filters, setFilters] = useState<LocalFilters>({});
  const [sortModel, setSortModel] = useState<GridSortModel>([{ field: 'price', sort: 'asc' }]);
  const [formData, setFormData] = useState<VehicleCreate>({
    brand: '',
    model: '',
    year: new Date().getFullYear(),
    color: '',
    price: 0,
    status: VehicleStatus.AVAILABLE,
  });
  const [snackbar, setSnackbar] = useState<{ 
    open: boolean; 
    message: string; 
    severity: 'success' | 'error' | 'info' | 'warning' 
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const { user } = useAuth();

  useEffect(() => {
    if (canViewVehicles(user)) {
      fetchVehicles();
    }
  }, [user]);

  useEffect(() => {
    applyFilters();
  }, [vehicles, filters]);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const data = await vehiclesApi.list();
      
      // Para clientes, mostrar apenas veículos disponíveis
      if (isCustomer(user)) {
        const availableVehicles = data.filter(v => v.status === VehicleStatus.AVAILABLE);
        setVehicles(availableVehicles);
      } else {
        setVehicles(data);
      }
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao carregar veículos. Verifique se o serviço está rodando.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...vehicles];

    // Filtro por marca
    if (filters.brand) {
      filtered = filtered.filter(vehicle => 
        vehicle.brand.toLowerCase().includes(filters.brand!.toLowerCase())
      );
    }

    // Filtro por modelo
    if (filters.model) {
      filtered = filtered.filter(vehicle => 
        vehicle.model.toLowerCase().includes(filters.model!.toLowerCase())
      );
    }

    // Filtro por status
    if (filters.status) {
      filtered = filtered.filter(vehicle => vehicle.status === filters.status);
    }

    // Filtro por preço mínimo
    if (filters.min_price) {
      filtered = filtered.filter(vehicle => vehicle.price >= filters.min_price!);
    }

    // Filtro por preço máximo
    if (filters.max_price) {
      filtered = filtered.filter(vehicle => vehicle.price <= filters.max_price!);
    }

    setFilteredVehicles(filtered);
  };

  const handleFilterChange = (field: keyof LocalFilters, value: any) => {
    setFilters((prev: LocalFilters) => ({ ...prev, [field]: value || undefined }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const handleSortModelChange = (model: GridSortModel) => {
    setSortModel(model);
  };

  const handleOpen = () => setOpen(true);

  const handleClose = () => {
    setOpen(false);
    setSelectedVehicle(null);
    setFormData({
      brand: '',
      model: '',
      year: new Date().getFullYear(),
      color: '',
      price: 0,
      status: VehicleStatus.AVAILABLE,
    });
  };

  const handleEdit = (vehicle: Vehicle) => {
    setSelectedVehicle(vehicle);
    setFormData(vehicle);
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este veículo?')) {
      try {
        await vehiclesApi.delete(id);
        setSnackbar({
          open: true,
          message: 'Veículo excluído com sucesso!',
          severity: 'success'
        });
        fetchVehicles();
      } catch (error) {
        console.error('Error deleting vehicle:', error);
        setSnackbar({
          open: true,
          message: 'Erro ao excluir veículo',
          severity: 'error'
        });
      }
    }
  };

  const handlePurchase = (vehicle: Vehicle) => {
    setVehicleToPurchase(vehicle);
    setPurchaseDialogOpen(true);
  };

  const handlePurchaseSuccess = () => {
    setPurchaseDialogOpen(false);
    setVehicleToPurchase(null);
    fetchVehicles();
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    try {
      if (selectedVehicle) {
        await vehiclesApi.update(selectedVehicle.id, formData);
        setSnackbar({
          open: true,
          message: 'Veículo atualizado com sucesso!',
          severity: 'success'
        });
      } else {
        await vehiclesApi.create(formData);
        setSnackbar({
          open: true,
          message: 'Veículo criado com sucesso!',
          severity: 'success'
        });
      }
      
      fetchVehicles();
      handleClose();
    } catch (error) {
      console.error('Error saving vehicle:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao salvar veículo',
        severity: 'error'
      });
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'year' ? parseInt(value) : value
    }));
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getStatusColor = (status: VehicleStatus) => {
    switch (status) {
      case VehicleStatus.AVAILABLE:
        return 'success';
      case VehicleStatus.RESERVED:
        return 'warning';
      case VehicleStatus.SOLD:
        return 'error';
      default:
        return 'default';
    }
  };

  const getPageTitle = () => {
    if (isCustomer(user)) {
      return 'Veículos Disponíveis';
    }
    return 'Gerenciamento de Veículos';
  };

  const getPageDescription = () => {
    if (isCustomer(user)) {
      return 'Explore nossa seleção de veículos disponíveis para compra';
    }
    return 'Gerencie o cadastro de veículos do sistema';
  };

  const columns: GridColDef[] = [
    { field: 'brand', headerName: 'Marca', flex: 1.2, minWidth: 110, align: 'center' as const, headerAlign: 'center' as const },
    { field: 'model', headerName: 'Modelo', flex: 1.5, minWidth: 120, align: 'center' as const, headerAlign: 'center' as const },
    { field: 'year', headerName: 'Ano', flex: 0.6, minWidth: 70, align: 'center' as const, headerAlign: 'center' as const },
    { field: 'color', headerName: 'Cor', flex: 0.8, minWidth: 90, align: 'center' as const, headerAlign: 'center' as const },
    { 
      field: 'price', 
      headerName: 'Preço', 
      flex: 1.1,
      minWidth: 110,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params) => formatCurrency(params.value)
    },
    // Mostrar status apenas para admin e vendedor
    ...(isCustomer(user) ? [] : [{
      field: 'status',
      headerName: 'Status',
      flex: 1,
      minWidth: 100,
      align: 'center' as const,
      headerAlign: 'center' as const,
      renderCell: (params: any) => (
        <Chip
          label={params.value}
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
    }]),
    {
      field: 'actions',
      headerName: 'Ações',
      flex: isCustomer(user) ? 0.8 : 1,
      minWidth: isCustomer(user) ? 80 : 100,
      align: 'center' as const,
      headerAlign: 'center' as const,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
          {isCustomer(user) ? (
            // Cliente: botão de compra
            <Button
              color="primary"
              variant="outlined"
              size="small"
              onClick={() => handlePurchase(params.row)}
              disabled={params.row.status !== VehicleStatus.AVAILABLE}
              sx={{ minWidth: 'auto', px: 1 }}
            >
              <ShoppingCartIcon fontSize="small" />
            </Button>
          ) : (
            // Admin/Vendedor: botões de edição e exclusão
            <>
              {canEditVehicles(user) && (
                <IconButton onClick={() => handleEdit(params.row)} size="small">
                  <EditIcon fontSize="small" />
                </IconButton>
              )}
              {canDeleteVehicles(user) && (
                <IconButton onClick={() => handleDelete(params.row.id)} size="small" color="error">
                  <DeleteIcon fontSize="small" />
                </IconButton>
              )}
            </>
          )}
        </Box>
      )
    }
  ];

  // Verificar se o usuário tem permissão para ver veículos
  if (!canViewVehicles(user)) {
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
            {getPageTitle()}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {getPageDescription()}
          </Typography>
        </Box>
        
        {canCreateVehicles(user) && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
            sx={{ minWidth: 140, height: 42 }}
          >
            Novo Veículo
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
              {/* Status - apenas para admin e vendedor */}
              {!isCustomer(user) && (
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filters.status || ''}
                      label="Status"
                      onChange={(e: SelectChangeEvent) => handleFilterChange('status', e.target.value || undefined)}
                    >
                      <MenuItem value="">Todos</MenuItem>
                      <MenuItem value={VehicleStatus.AVAILABLE}>Disponível</MenuItem>
                      <MenuItem value={VehicleStatus.RESERVED}>Reservado</MenuItem>
                      <MenuItem value={VehicleStatus.SOLD}>Vendido</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              )}
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Marca"
                  value={filters.brand || ''}
                  onChange={(e) => handleFilterChange('brand', e.target.value || undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  size="small"
                  label="Modelo"
                  value={filters.model || ''}
                  onChange={(e) => handleFilterChange('model', e.target.value || undefined)}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <NumericFormat
                  customInput={TextField}
                  fullWidth
                  size="small"
                  label="Preço Mínimo"
                  value={filters.min_price || ''}
                  onValueChange={(values) => {
                    handleFilterChange('min_price', values.floatValue || undefined);
                  }}
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  decimalScale={2}
                  fixedDecimalScale
                  isAllowed={(values) => {
                    const { floatValue } = values;
                    return floatValue === undefined || floatValue >= 0;
                  }}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <NumericFormat
                  customInput={TextField}
                  fullWidth
                  size="small"
                  label="Preço Máximo"
                  value={filters.max_price || ''}
                  onValueChange={(values) => {
                    handleFilterChange('max_price', values.floatValue || undefined);
                  }}
                  thousandSeparator="."
                  decimalSeparator=","
                  prefix="R$ "
                  decimalScale={2}
                  fixedDecimalScale
                  isAllowed={(values) => {
                    const { floatValue } = values;
                    return floatValue === undefined || floatValue >= 0;
                  }}
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
              rows={filteredVehicles}
              columns={columns}
              loading={loading}
              sortModel={sortModel}
              onSortModelChange={handleSortModelChange}
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
                '& .MuiDataGrid-columnHeader': {
                  fontSize: '0.875rem',
                  fontWeight: 600,
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
                      {Object.keys(filters).length > 0 ? 'Nenhum veículo encontrado' : 
                       isCustomer(user) ? 'Nenhum veículo disponível' : 'Nenhum veículo cadastrado'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Object.keys(filters).length > 0 ? 'Tente ajustar os filtros ou cadastre um novo veículo.' :
                       isCustomer(user) 
                        ? 'Não há veículos disponíveis no momento.'
                        : 'Cadastre o primeiro veículo para começar.'
                      }
                    </Typography>
                  </Box>
                )
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Dialog de Criação/Edição - apenas para admin e vendedor */}
      {canCreateVehicles(user) && (
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle>
            {selectedVehicle ? 'Editar Veículo' : 'Novo Veículo'}
          </DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Marca"
                    name="brand"
                    value={formData.brand}
                    onChange={handleInputChange}
                    required
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Modelo"
                    name="model"
                    value={formData.model}
                    onChange={handleInputChange}
                    required
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Ano"
                    name="year"
                    type="number"
                    value={formData.year}
                    onChange={handleInputChange}
                    required
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Cor"
                    name="color"
                    value={formData.color}
                    onChange={handleInputChange}
                    required
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <NumericFormat
                    customInput={TextField}
                    fullWidth
                    label="Preço"
                    name="price"
                    value={formData.price}
                    onValueChange={(values) => {
                      setFormData((prev: VehicleCreate) => ({ ...prev, price: values.floatValue || 0 }));
                    }}
                    thousandSeparator="."
                    decimalSeparator=","
                    prefix="R$ "
                    decimalScale={2}
                    fixedDecimalScale
                    required
                    margin="normal"
                    isAllowed={(values) => {
                      const { floatValue } = values;
                      return floatValue === undefined || floatValue >= 0;
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={formData.status}
                      label="Status"
                      onChange={(e) => setFormData((prev: VehicleCreate) => ({ ...prev, status: e.target.value as VehicleStatus }))}
                    >
                      <MenuItem value={VehicleStatus.AVAILABLE}>Disponível</MenuItem>
                      <MenuItem value={VehicleStatus.RESERVED}>Reservado</MenuItem>
                      <MenuItem value={VehicleStatus.SOLD}>Vendido</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancelar</Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedVehicle ? 'Atualizar' : 'Criar'}
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {/* Dialog de Compra - apenas para clientes */}
      {canBuyVehicles(user) && vehicleToPurchase && (
        <PurchaseDialog
          open={purchaseDialogOpen}
          onClose={() => setPurchaseDialogOpen(false)}
          vehicle={vehicleToPurchase}
          onPurchaseSuccess={handlePurchaseSuccess}
        />
      )}

      {/* Snackbar para notificações */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default VehiclesWithRoles; 