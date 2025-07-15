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
  Autocomplete
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Sale, SaleCreate, Vehicle, VehicleStatus, PaymentStatus } from '../types';
import { salesApi, vehiclesApi } from '../services/api';
import InputMask from 'react-input-mask';

const Sales: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [availableVehicles, setAvailableVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSale, setSelectedSale] = useState<Sale | null>(null);
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

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 100 },
    { 
      field: 'vehicle_id', 
      headerName: 'Veículo', 
      width: 200,
      renderCell: (params) => {
        const vehicle = vehicles.find(v => v.id === params.value);
        return vehicle ? `${vehicle.brand} ${vehicle.model} (${vehicle.year})` : params.value;
      }
    },
    { field: 'buyer_cpf', headerName: 'CPF do Comprador', width: 150 },
    { 
      field: 'sale_price', 
      headerName: 'Preço', 
      width: 120,
      renderCell: (params) => formatCurrency(params.value)
    },
    { field: 'payment_code', headerName: 'Código de Pagamento', width: 150 },
    { 
      field: 'payment_status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => {
        const statusColors = {
          [PaymentStatus.PENDING]: '#ed6c02',
          [PaymentStatus.PAID]: '#2e7d32',
          [PaymentStatus.CANCELLED]: '#d32f2f'
        };
        return (
          <Box
            sx={{
              backgroundColor: statusColors[params.value as PaymentStatus],
              color: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '0.75rem'
            }}
          >
            {getStatusText(params.value)}
          </Box>
        );
      }
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 200,
      renderCell: (params) => {
        // Não mostrar ações para vendas pagas ou canceladas
        if (params.row.payment_status === PaymentStatus.PAID || 
            params.row.payment_status === PaymentStatus.CANCELLED) {
          return null;
        }
        
        return (
          <Box>
            <IconButton
              size="small"
              onClick={() => handleOpenDialog(params.row)}
              color="primary"
            >
              <EditIcon />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => handleDelete(params.row.id)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        );
      }
    }
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h4">Vendas</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Nova Venda
            </Button>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ height: 600, width: '100%' }}>
            <DataGrid
              rows={sales}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: { pageSize: 10 }
                }
              }}
              pageSizeOptions={[10]}
              disableRowSelectionOnClick
              slots={{
                noRowsOverlay: () => (
                  <Box
                    sx={{
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="body1" color="text.secondary">
                      Nenhuma venda cadastrada
                    </Typography>
                  </Box>
                )
              }}
            />
          </Paper>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Sales;