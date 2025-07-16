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

const VehiclesWithRoles: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [purchaseDialogOpen, setPurchaseDialogOpen] = useState(false);
  const [vehicleToPurchase, setVehicleToPurchase] = useState<Vehicle | null>(null);
  const [filters, setFilters] = useState<VehicleFilters>({
    skip: 0,
    limit: 100,
    sort: 'price',
    order: 'asc'
  });
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
  }, [filters, user]);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const data = await vehiclesApi.list(filters);
      
      // Para clientes, mostrar apenas veículos disponíveis
      if (isCustomer(user)) {
        const availableVehicles = data.filter(v => v.status === VehicleStatus.AVAILABLE);
        setVehicles(availableVehicles);
      } else {
        setVehicles(data);
      }
    } catch (error) {
      console.error('Erro ao buscar veículos:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao carregar veículos',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
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
    setFormData({
      brand: vehicle.brand,
      model: vehicle.model,
      year: vehicle.year,
      color: vehicle.color,
      price: vehicle.price,
      status: vehicle.status,
    });
    setOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este veículo?')) {
      try {
        await vehiclesApi.delete(id);
        setSnackbar({
          open: true,
          message: 'Veículo excluído com sucesso',
          severity: 'success'
        });
        fetchVehicles();
      } catch (error) {
        console.error('Erro ao excluir veículo:', error);
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
    setSnackbar({
      open: true,
      message: 'Compra realizada com sucesso!',
      severity: 'success'
    });
    fetchVehicles();
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      if (selectedVehicle) {
        await vehiclesApi.update(selectedVehicle.id, formData);
        setSnackbar({
          open: true,
          message: 'Veículo atualizado com sucesso',
          severity: 'success'
        });
      } else {
        await vehiclesApi.create(formData);
        setSnackbar({
          open: true,
          message: 'Veículo criado com sucesso',
          severity: 'success'
        });
      }
      handleClose();
      fetchVehicles();
    } catch (error) {
      console.error('Erro ao salvar veículo:', error);
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

  const handleFilterChange = (field: keyof VehicleFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleSortModelChange = (model: GridSortModel) => {
    if (model.length > 0) {
      const { field, sort } = model[0];
      setFilters(prev => ({
        ...prev,
        sort: field,
        order: sort || 'asc'
      }));
    }
  };

  const clearFilters = () => {
    setFilters({
      skip: 0,
      limit: 100,
      sort: 'price',
      order: 'asc'
    });
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
    { field: 'brand', headerName: 'Marca', width: 130, minWidth: 100 },
    { field: 'model', headerName: 'Modelo', width: 130, minWidth: 100 },
    { field: 'year', headerName: 'Ano', width: 80, minWidth: 70 },
    { field: 'color', headerName: 'Cor', width: 100, minWidth: 80 },
    { 
      field: 'price', 
      headerName: 'Preço', 
      width: 120,
      minWidth: 100,
      renderCell: (params) => formatCurrency(params.value)
    },
    // Mostrar status apenas para admin e vendedor
    ...(isCustomer(user) ? [] : [{
      field: 'status',
      headerName: 'Status',
      width: 120,
      minWidth: 100,
      renderCell: (params: any) => (
        <Chip
          label={params.value}
          color={getStatusColor(params.value) as any}
          size="small"
        />
      )
    }]),
    {
      field: 'actions',
      headerName: 'Ações',
      width: isCustomer(user) ? 100 : 150,
      minWidth: isCustomer(user) ? 80 : 120,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {getPageTitle()}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {getPageDescription()}
        </Typography>
      </Box>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterIcon />
              Filtros e Pesquisa
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                startIcon={showFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                onClick={() => setShowFilters(!showFilters)}
                variant="outlined"
                size="small"
              >
                {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
              </Button>
              {canCreateVehicles(user) && (
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleOpen}
                  variant="contained"
                  size="small"
                >
                  Novo Veículo
                </Button>
              )}
            </Box>
          </Box>

          <Collapse in={showFilters}>
            <Grid container spacing={2}>
              {/* Filtro de Status - apenas para admin e vendedor */}
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
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={vehicles}
              columns={columns}
              loading={loading}
              sortModel={[{ field: filters.sort || 'price', sort: filters.order || 'asc' }]}
              onSortModelChange={handleSortModelChange}
              initialState={{
                pagination: {
                  paginationModel: { pageSize: 10 }
                }
              }}
              pageSizeOptions={[10, 25, 50]}
              disableRowSelectionOnClick
              density="comfortable"
              sx={{
                '& .MuiDataGrid-cell': {
                  borderBottom: 'none',
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiDataGrid-columnHeader': {
                    backgroundColor: 'primary.main',
                  },
                },
                '& .MuiDataGrid-row:hover': {
                  backgroundColor: 'action.hover',
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
                      {isCustomer(user) ? 'Nenhum veículo disponível' : 'Nenhum veículo cadastrado'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {isCustomer(user) 
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
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Status</InputLabel>
                    <Select
                      name="status"
                      value={formData.status}
                      label="Status"
                      onChange={(e: SelectChangeEvent) => 
                        setFormData((prev: VehicleCreate) => ({ ...prev, status: e.target.value as VehicleStatus }))
                      }
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

      {/* Dialog de Compra - apenas para cliente */}
      <PurchaseDialog
        open={purchaseDialogOpen}
        onClose={() => setPurchaseDialogOpen(false)}
        vehicle={vehicleToPurchase}
        onPurchaseSuccess={handlePurchaseSuccess}
      />

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

export default VehiclesWithRoles; 