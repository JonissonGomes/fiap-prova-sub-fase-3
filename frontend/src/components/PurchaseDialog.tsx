import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Chip
} from '@mui/material';
import { Vehicle, Customer, SaleCreate, VehicleStatus } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { salesService, customerService, vehiclesApi } from '../services/api';

interface PurchaseDialogProps {
  open: boolean;
  onClose: () => void;
  vehicle: Vehicle | null;
  onPurchaseSuccess: () => void;
}

const PurchaseDialog: React.FC<PurchaseDialogProps> = ({ 
  open, 
  onClose, 
  vehicle, 
  onPurchaseSuccess 
}) => {
  const { user } = useAuth();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [paymentCode, setPaymentCode] = useState<string>('');
  const [confirming, setConfirming] = useState(false);

  const fetchCustomerData = useCallback(async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      // Buscar dados do cliente pelo email do usuário
      const customers = await customerService.list();
      const foundCustomer = customers.find(c => c.email === user.email);
      setCustomer(foundCustomer || null);
    } catch (error) {
      console.error('Erro ao buscar dados do cliente:', error);
      setError('Erro ao carregar dados do cliente');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (open && user) {
      fetchCustomerData();
    }
  }, [open, user, fetchCustomerData]);

  useEffect(() => {
    if (open) {
      // Gerar código de pagamento aleatório
      const generatePaymentCode = () => {
        return 'PAY-' + Math.random().toString(36).substr(2, 9).toUpperCase();
      };
      setPaymentCode(generatePaymentCode());
    }
  }, [open]);

  const handleConfirmPurchase = async () => {
    if (!user || !vehicle || !customer) return;

    setConfirming(true);
    setError('');
    setSuccess('');

    try {
      // Criar a venda
      const saleData: SaleCreate = {
        customer_id: customer.id,
        vehicle_id: vehicle.id,
        payment_method: 'PIX',
        notes: `Código de pagamento: ${paymentCode}`
      };

      await salesService.create(saleData);

      // Atualizar status do veículo para reservado
      await vehiclesApi.updateStatus(vehicle.id, VehicleStatus.RESERVED);

      setSuccess('Compra realizada com sucesso! Código de pagamento: ' + paymentCode);
      
      // Aguardar 2 segundos e fechar o diálogo
      setTimeout(() => {
        onPurchaseSuccess();
        onClose();
      }, 2000);

    } catch (error: any) {
      console.error('Erro ao processar compra:', error);
      setError(error.response?.data?.detail || 'Erro ao processar compra');
    } finally {
      setConfirming(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const handleClose = () => {
    setError('');
    setSuccess('');
    setConfirming(false);
    onClose();
  };

  if (!vehicle) return null;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Typography variant="h5" component="div">
          Confirmar Compra
        </Typography>
      </DialogTitle>

      <DialogContent>
        {loading && (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {!loading && (
          <Grid container spacing={3}>
            {/* Informações do Veículo */}
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Informações do Veículo
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Marca/Modelo:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {vehicle.brand} {vehicle.model}
                  </Typography>
                </Box>

                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Ano:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {vehicle.year}
                  </Typography>
                </Box>

                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Cor:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {vehicle.color}
                  </Typography>
                </Box>

                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Status:
                  </Typography>
                  <Chip 
                    label={vehicle.status} 
                    color={vehicle.status === VehicleStatus.AVAILABLE ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box>
                  <Typography variant="h6" color="primary">
                    Preço: {formatCurrency(vehicle.price)}
                  </Typography>
                </Box>
              </Paper>
            </Grid>

            {/* Informações do Cliente */}
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Dados do Comprador
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                {customer ? (
                  <>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Nome:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {customer.name}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        CPF:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {customer.cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Email:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {customer.email}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Telefone:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {customer.phone.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3')}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Endereço:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {customer.address}, {customer.city} - {customer.state}
                      </Typography>
                    </Box>
                  </>
                ) : (
                  <Alert severity="warning">
                    Dados do cliente não encontrados. Verifique se seu cadastro está completo.
                  </Alert>
                )}
              </Paper>
            </Grid>

            {/* Informações de Pagamento */}
            <Grid item xs={12}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Informações de Pagamento
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Código de Pagamento"
                      value={paymentCode}
                      variant="outlined"
                      disabled
                      helperText="Código gerado automaticamente para identificar o pagamento"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Valor Total"
                      value={formatCurrency(vehicle.price)}
                      variant="outlined"
                      disabled
                    />
                  </Grid>
                </Grid>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Instruções de Pagamento:</strong><br />
                    • Guarde o código de pagamento: <strong>{paymentCode}</strong><br />
                    • O pagamento será processado após a confirmação<br />
                    • Você receberá um email com as instruções de pagamento<br />
                    • O veículo ficará reservado até a confirmação do pagamento
                  </Typography>
                </Alert>
              </Paper>
            </Grid>
          </Grid>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={handleClose} disabled={confirming}>
          Cancelar
        </Button>
        <Button
          onClick={handleConfirmPurchase}
          variant="contained"
          disabled={!customer || confirming || loading}
          startIcon={confirming ? <CircularProgress size={20} /> : null}
        >
          {confirming ? 'Processando...' : 'Confirmar Compra'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PurchaseDialog; 