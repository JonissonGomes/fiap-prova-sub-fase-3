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
  SelectChangeEvent
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Sale, SaleCreate, Vehicle, VehicleStatus, PaymentStatus } from '../types';
import { salesApi, vehiclesApi } from '../services/api';
import InputMask from 'react-input-mask';

const Sales: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
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
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Erro ao carregar veículos. Verifique se o serviço está rodando.',
        severity: 'error'
      });
      setVehicles([]);
    }
  };

  const handleOpenDialog = (sale?: Sale) => {
    if (sale) {
      setSelectedSale(sale);
      setFormData(sale);
    } else {
      setSelectedSale(null);
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
    setFormData({
      vehicle_id: '',
      buyer_cpf: '',
      sale_price: 0,
      payment_code: ''
    });
  };

  const handleVehicleChange = (event: SelectChangeEvent<string>) => {
    const vehicleId = event.target.value;
    const selectedVehicle = vehicles.find(v => v.id === vehicleId);
    
    setFormData(prev => ({
      ...prev,
      vehicle_id: vehicleId,
      sale_price: selectedVehicle ? selectedVehicle.price : 0
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
      const selectedVehicle = vehicles.find(v => v.id === formData.vehicle_id);
      if (selectedVehicle && formData.sale_price < selectedVehicle.price) {
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
        case PaymentStatus.APPROVED:
          await salesApi.confirmPayment(id);
          await vehiclesApi.updateStatus(sale.vehicle_id, 'VENDIDO');
          break;
        case PaymentStatus.REJECTED:
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

  const columns: GridColDef[] = [
    {
      field: 'vehicle_id',
      headerName: 'Veículo',
      width: 200,
      valueGetter: (params) => {
        const vehicle = vehicles.find(v => v.id === params.row.vehicle_id);
        return vehicle ? `${vehicle.brand} ${vehicle.model}` : params.row.vehicle_id;
      }
    },
    { field: 'buyer_cpf', headerName: 'CPF do Cliente', width: 150 },
    {
      field: 'sale_price',
      headerName: 'Preço',
      width: 150,
      valueFormatter: (params) =>
        new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL'
        }).format(params.value)
    },
    { field: 'payment_code', headerName: 'Código de Pagamento', width: 200 },
    {
      field: 'payment_status',
      headerName: 'Status da venda',
      width: 250,
      renderCell: (params) => {
        const statusColors = {
          [PaymentStatus.PENDING]: '#ed6c02',
          [PaymentStatus.APPROVED]: '#2e7d32',
          [PaymentStatus.REJECTED]: '#d32f2f'
        };
        return (
          <Box>
            <Typography sx={{ color: statusColors[params.value as PaymentStatus] }}>
              {params.value}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
              Atualizado em: {new Date(params.row.updated_at).toLocaleString('pt-BR')}
            </Typography>
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
        if (params.row.payment_status === PaymentStatus.APPROVED || 
            params.row.payment_status === PaymentStatus.REJECTED) {
          return null;
        }
        
        return (
          <Box>
            <IconButton
              color="primary"
              onClick={() => handleOpenDialog(params.row)}
              size="small"
            >
              <EditIcon />
            </IconButton>
            <IconButton
              color="error"
              onClick={() => handleDelete(params.row.id)}
              size="small"
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
              <FormControl fullWidth>
                <InputLabel>Veículo</InputLabel>
                <Select
                  value={formData.vehicle_id}
                  onChange={handleVehicleChange}
                  label="Veículo"
                  required
                >
                  {vehicles && vehicles.length > 0 ? (
                    vehicles
                      .filter(vehicle => vehicle.status === VehicleStatus.AVAILABLE)
                      .map(vehicle => (
                        <MenuItem key={vehicle.id} value={vehicle.id}>
                          {`${vehicle.brand} ${vehicle.model} - ${vehicle.year}`}
                        </MenuItem>
                      ))
                  ) : (
                    <MenuItem disabled>Nenhum veículo disponível</MenuItem>
                  )}
                </Select>
              </FormControl>
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