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
  Chip
} from '@mui/material';
import { DataGrid, GridColDef, GridSortModel } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, FilterList as FilterIcon } from '@mui/icons-material';
import { NumericFormat } from 'react-number-format';
import { Vehicle, VehicleCreate, VehicleStatus, VehicleFilters } from '../types';
import { vehiclesApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Vehicles: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [showFilters, setShowFilters] = useState(false);
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

  const { user } = useAuth();

  useEffect(() => {
    fetchVehicles();
  }, [filters]);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const data = await vehiclesApi.list(filters);
      setVehicles(data);
    } catch (error) {
      console.error('Erro ao buscar veículos:', error);
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
        fetchVehicles();
      } catch (error) {
        console.error('Erro ao excluir veículo:', error);
      }
    }
  };

  const handleStatusChange = async (id: string, status: VehicleStatus) => {
    try {
      await vehiclesApi.updateStatus(id, status);
      fetchVehicles();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      if (selectedVehicle) {
        await vehiclesApi.update(selectedVehicle.id, formData);
      } else {
        await vehiclesApi.create(formData);
      }
      handleClose();
      fetchVehicles();
    } catch (error) {
      console.error('Erro ao salvar veículo:', error);
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

  const columns: GridColDef[] = [
    { field: 'brand', headerName: 'Marca', width: 150 },
    { field: 'model', headerName: 'Modelo', width: 150 },
    { field: 'year', headerName: 'Ano', width: 100 },
    { field: 'color', headerName: 'Cor', width: 120 },
    { 
      field: 'price', 
      headerName: 'Preço', 
      width: 150,
      renderCell: (params) => formatCurrency(params.value)
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={getStatusColor(params.value) as any}
          size="small"
        />
      )
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 200,
      renderCell: (params) => (
        <Box>
          {(user?.role === 'ADMIN' || user?.role === 'SALES') && (
            <>
              <IconButton onClick={() => handleEdit(params.row)} size="small">
                <EditIcon />
              </IconButton>
              {user?.role === 'ADMIN' && (
                <IconButton onClick={() => handleDelete(params.row.id)} size="small">
                  <DeleteIcon />
                </IconButton>
              )}
            </>
          )}
        </Box>
      )
    }
  ];

  const canManageVehicles = user?.role === 'ADMIN' || user?.role === 'SALES';

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Gerenciamento de Veículos
      </Typography>

      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Filtros</Typography>
          <Box>
            <Button
              startIcon={<FilterIcon />}
              onClick={() => setShowFilters(!showFilters)}
              variant="outlined"
              sx={{ mr: 1 }}
            >
              {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
            </Button>
            {canManageVehicles && (
              <Button
                startIcon={<AddIcon />}
                onClick={handleOpen}
                variant="contained"
              >
                Novo Veículo
              </Button>
            )}
          </Box>
        </Box>

        {showFilters && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status || ''}
                  onChange={(e: SelectChangeEvent) => handleFilterChange('status', e.target.value || undefined)}
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value={VehicleStatus.AVAILABLE}>Disponível</MenuItem>
                  <MenuItem value={VehicleStatus.RESERVED}>Reservado</MenuItem>
                  <MenuItem value={VehicleStatus.SOLD}>Vendido</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Marca"
                value={filters.brand || ''}
                onChange={(e) => handleFilterChange('brand', e.target.value || undefined)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Modelo"
                value={filters.model || ''}
                onChange={(e) => handleFilterChange('model', e.target.value || undefined)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Preço Mínimo"
                type="number"
                value={filters.min_price || ''}
                onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Preço Máximo"
                type="number"
                value={filters.max_price || ''}
                onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                onClick={clearFilters}
                variant="outlined"
                fullWidth
              >
                Limpar Filtros
              </Button>
            </Grid>
          </Grid>
        )}
      </Paper>

      <DataGrid
        rows={vehicles}
        columns={columns}
        loading={loading}
        autoHeight
        disableRowSelectionOnClick
        sortingMode="server"
        onSortModelChange={handleSortModelChange}
        initialState={{
          pagination: {
            paginationModel: { page: 0, pageSize: 10 }
          },
          sorting: {
            sortModel: [{ field: filters.sort || 'price', sort: filters.order || 'asc' }]
          }
        }}
        pageSizeOptions={[10, 25, 50]}
      />

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
    </Box>
  );
};

export default Vehicles;
