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
  Divider
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Sale, Vehicle, PaymentStatus } from '../types';
import { salesApi, vehiclesApi, customerService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { isCustomer } from '../utils/permissions';

const MyPurchases: React.FC = () => {
  const [sales, setSales] = useState<Sale[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [customerCpf, setCustomerCpf] = useState<string>('');

  const { user } = useAuth();

  useEffect(() => {
    if (user && isCustomer(user)) {
      fetchCustomerData();
    }
  }, [user]);

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

  const columns: GridColDef[] = [
    { 
      field: 'id', 
      headerName: 'ID da Compra', 
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {params.value.substring(0, 8)}...
        </Typography>
      )
    },
    { 
      field: 'vehicle_id', 
      headerName: 'Veículo', 
      width: 200,
      renderCell: (params) => {
        const vehicle = vehicles.find(v => v.id === params.value);
        return vehicle ? (
          <Typography variant="body2">
            {vehicle.brand} {vehicle.model} ({vehicle.year})
          </Typography>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Veículo não encontrado
          </Typography>
        );
      }
    },
    { 
      field: 'sale_price', 
      headerName: 'Preço', 
      width: 130,
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'payment_code', 
      headerName: 'Código de Pagamento', 
      width: 180,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'payment_status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={getStatusText(params.value)} 
          color={getStatusColor(params.value) as any}
          size="small"
        />
      )
    },
    { 
      field: 'created_at', 
      headerName: 'Data da Compra', 
      width: 130,
      renderCell: (params) => formatDate(params.value)
    }
  ];

  // Verificar se o usuário é cliente
  if (!isCustomer(user)) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Esta página é apenas para clientes.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          {error}
        </Alert>
      </Box>
    );
  }

  // Estatísticas rápidas
  const totalCompras = sales.length;
  const comprasPagas = sales.filter(s => s.payment_status === PaymentStatus.PAID).length;
  const comprasPendentes = sales.filter(s => s.payment_status === PaymentStatus.PENDING).length;
  const comprasCanceladas = sales.filter(s => s.payment_status === PaymentStatus.CANCELLED).length;
  const valorTotal = sales.reduce((sum, s) => sum + s.sale_price, 0);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Minhas Compras
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Histórico de todas as suas compras de veículos
      </Typography>

      {/* Estatísticas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {totalCompras}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total de Compras
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                {comprasPagas}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Compras Pagas
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                {comprasPendentes}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pendentes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {formatCurrency(valorTotal)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Valor Total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabela de Compras */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={sales}
          columns={columns}
          loading={loading}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 10 }
            }
          }}
          pageSizeOptions={[10, 25, 50]}
          disableRowSelectionOnClick
          slots={{
            noRowsOverlay: () => (
              <Box
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Nenhuma compra encontrada
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Você ainda não fez nenhuma compra de veículo.
                </Typography>
              </Box>
            )
          }}
        />
      </Paper>

      {/* Instruções para pagamento */}
      {comprasPendentes > 0 && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Instruções para Pagamento:</strong><br />
            • Você tem {comprasPendentes} compra(s) pendente(s)<br />
            • Use o código de pagamento para efetuar o pagamento<br />
            • Após o pagamento, aguarde a confirmação do vendedor<br />
            • Em caso de dúvidas, entre em contato com nossa equipe
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default MyPurchases; 