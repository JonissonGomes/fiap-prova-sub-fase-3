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
  Snackbar
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Payment, Sale, Vehicle, PaymentStatus } from '../types';
import { salesApi, vehiclesApi } from '../services/api';

const Payments: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSale, setSelectedSale] = useState<Sale | null>(null);
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
      // Filtrar apenas vendas que não estão canceladas
      const activeSales = data.filter(sale => sale.payment_status !== PaymentStatus.REJECTED);
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

  const getStatusText = (status: PaymentStatus) => {
    if (status === PaymentStatus.APPROVED) {
      return 'Aprovado';
    }
    if (status === PaymentStatus.REJECTED) {
      return 'Cancelado';
    }
    return 'Pendente';
  };

  const handleStatusChange = async (saleId: string, status: PaymentStatus) => {
    try {
      const sale = sales.find(s => s.id === saleId);
      if (!sale) return;

      switch (status) {
        case PaymentStatus.APPROVED:
          // Notificar webhook de pagamento
          await salesApi.confirmPayment(saleId);
          await vehiclesApi.updateStatus(sale.vehicle_id, 'VENDIDO');
          break;
        case PaymentStatus.REJECTED:
          await salesApi.cancelPayment(saleId);
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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 100 },
    { field: 'buyer_cpf', headerName: 'CPF do Comprador', width: 150 },
    { field: 'payment_code', headerName: 'Código de Pagamento', width: 200 },
    { 
      field: 'sale_price', 
      headerName: 'Valor', 
      width: 120,
      renderCell: (params) => formatCurrency(params.value)
    },
    {
      field: 'payment_status',
      headerName: 'Status',
      width: 150,
      renderCell: (params) => {
        const statusColors = {
          [PaymentStatus.PENDING]: '#ed6c02',
          [PaymentStatus.APPROVED]: '#2e7d32',
          [PaymentStatus.REJECTED]: '#d32f2f'
        };
        return (
          <Typography sx={{ color: statusColors[params.value as PaymentStatus] }}>
            {getStatusText(params.value)}
          </Typography>
        );
      }
    },
    {
      field: 'actions',
      headerName: 'Ações',
      width: 200,
      renderCell: (params) => {
        if (params.row.payment_status === PaymentStatus.APPROVED || 
            params.row.payment_status === PaymentStatus.REJECTED) {
          return null;
        }
        
        return (
          <Box>
            <Button
              color="success"
              variant="outlined"
              size="small"
              onClick={() => handleStatusChange(params.row.id, PaymentStatus.APPROVED)}
              sx={{ mr: 1 }}
            >
              Aprovar
            </Button>
            <Button
              color="error"
              variant="outlined"
              size="small"
              onClick={() => handleStatusChange(params.row.id, PaymentStatus.REJECTED)}
            >
              Cancelar
            </Button>
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
            <Typography variant="h4">Pagamentos</Typography>
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
                      Não há pagamentos pendentes
                    </Typography>
                  </Box>
                )
              }}
            />
          </Paper>
        </Grid>
      </Grid>

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

export default Payments; 