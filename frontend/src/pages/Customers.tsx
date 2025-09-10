import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  IconButton,
  Alert,
  Snackbar,
  Grid,
  Container,
  Card,
  CardContent,
  Collapse
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon, 
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import InputMask from 'react-input-mask';
import { Customer, CustomerCreate } from '../types';
import { customerService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { triggerDataRefresh, onDataRefresh, DATA_REFRESH_EVENTS } from '../utils/dataRefresh';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState<CustomerCreate>({
    name: '',
    email: '',
    phone: '',
    cpf: '',
    address: '',
    city: '',
    state: '',
    zip_code: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const { user } = useAuth();

  useEffect(() => {
    fetchCustomers();
  }, []);

  // Escutar mudanças de dados
  useEffect(() => {
    const cleanup = onDataRefresh(DATA_REFRESH_EVENTS.CUSTOMERS, () => {
      fetchCustomers();
    });

    return cleanup;
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const customers = await customerService.list();
      setCustomers(customers);
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao carregar clientes',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (customer?: Customer) => {
    if (customer) {
      setSelectedCustomer(customer);
      setFormData({
        name: customer.name,
        email: customer.email,
        phone: customer.phone,
        cpf: customer.cpf,
        address: customer.address,
        city: customer.city,
        state: customer.state,
        zip_code: customer.zip_code
      });
    } else {
      setSelectedCustomer(null);
      setFormData({
        name: '',
        email: '',
        phone: '',
        cpf: '',
        address: '',
        city: '',
        state: '',
        zip_code: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCustomer(null);
    setErrors({});
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    
    if (!formData.cpf.trim()) {
      newErrors.cpf = 'CPF é obrigatório';
    } else if (!/^\d{11}$/.test(formData.cpf)) {
      newErrors.cpf = 'CPF inválido';
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = 'Telefone é obrigatório';
    }
    
    if (!formData.address.trim()) {
      newErrors.address = 'Endereço é obrigatório';
    }
    
    if (!formData.city.trim()) {
      newErrors.city = 'Cidade é obrigatória';
    }
    
    if (!formData.state.trim()) {
      newErrors.state = 'UF é obrigatório';
    } else if (formData.state.length !== 2) {
      newErrors.state = 'UF deve ter exatamente 2 caracteres';
    }
    
    if (!formData.zip_code.trim()) {
      newErrors.zip_code = 'CEP é obrigatório';
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
      console.log('Dados sendo enviados:', formData);
      
      if (selectedCustomer) {
        await customerService.update(selectedCustomer.id, formData);
        setSnackbar({
          open: true,
          message: 'Cliente atualizado com sucesso!',
          severity: 'success'
        });
      } else {
        await customerService.create(formData);
        setSnackbar({
          open: true,
          message: 'Cliente criado com sucesso!',
          severity: 'success'
        });
      }
      
      fetchCustomers();
      
      // Notificar outras páginas sobre mudanças
      triggerDataRefresh(DATA_REFRESH_EVENTS.CUSTOMERS);
      
      handleCloseDialog();
    } catch (error: any) {
      console.error('Erro ao salvar cliente:', error);
      
      let errorMessage = 'Erro ao salvar cliente';
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response?.data?.details) {
        const details = error.response.data.details;
        errorMessage = details.map((d: any) => d.msg).join(', ');
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este cliente?')) {
      try {
        await customerService.delete(id);
        setSnackbar({
          open: true,
          message: 'Cliente excluído com sucesso!',
          severity: 'success'
        });
        fetchCustomers();
        
        // Notificar outras páginas sobre mudanças
        triggerDataRefresh(DATA_REFRESH_EVENTS.CUSTOMERS);
      } catch (error: any) {
        console.error('Erro ao excluir cliente:', error);
        
        let errorMessage = 'Erro ao excluir cliente';
        if (error.response?.data?.error) {
          errorMessage = error.response.data.error;
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setSnackbar({
          open: true,
          message: errorMessage,
          severity: 'error'
        });
      }
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchCustomers();
      return;
    }

    try {
      const results = await customerService.search(searchTerm);
      setCustomers(results);
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      setSnackbar({
        open: true,
        message: 'Erro ao buscar clientes',
        severity: 'error'
      });
    }
  };

  const clearSearch = () => {
    setSearchTerm('');
    fetchCustomers();
  };

  const columns: GridColDef[] = [
    { 
      field: 'name', 
      headerName: 'Nome', 
      flex: 1.5, 
      minWidth: 150,
      align: 'center' as const,
      headerAlign: 'center' as const
    },
    { 
      field: 'email', 
      headerName: 'Email', 
      flex: 2, 
      minWidth: 200,
      align: 'center' as const,
      headerAlign: 'center' as const
    },
    { 
      field: 'phone', 
      headerName: 'Telefone', 
      flex: 1.2, 
      minWidth: 130,
      align: 'center' as const,
      headerAlign: 'center' as const
    },
    { 
      field: 'cpf', 
      headerName: 'CPF', 
      flex: 1.1, 
      minWidth: 120,
      align: 'center' as const,
      headerAlign: 'center' as const
    },
    { 
      field: 'city', 
      headerName: 'Cidade', 
      flex: 1.2, 
      minWidth: 120,
      align: 'center' as const,
      headerAlign: 'center' as const
    },
    { 
      field: 'state', 
      headerName: 'UF', 
      flex: 0.8, 
      minWidth: 80,
      align: 'center' as const,
      headerAlign: 'center' as const
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
          <IconButton
            onClick={() => handleOpenDialog(params.row)}
            size="small"
          >
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton
            onClick={() => handleDelete(params.row.id)}
            size="small"
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      )
    }
  ];

  // Filtrar clientes com base no termo de busca
  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.cpf.includes(searchTerm) ||
    customer.phone.includes(searchTerm) ||
    customer.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Gerenciamento de Clientes
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gerencie o cadastro de clientes do sistema
          </Typography>
        </Box>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ minWidth: 140, height: 42 }}
        >
          Novo Cliente
        </Button>
      </Box>

      {/* Card de estatísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, backgroundColor: 'primary.light', borderRadius: 1 }}>
                  <PersonIcon color="primary" />
                </Box>
                <Box>
                  <Typography variant="h6" component="div">
                    {filteredCustomers.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm ? 'Clientes Encontrados' : 'Total de Clientes'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>Busca</Typography>
            <Button
              onClick={() => setShowFilters(!showFilters)}
              startIcon={showFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              variant="outlined"
              size="small"
              sx={{ minWidth: 140 }}
            >
              {showFilters ? 'Ocultar' : 'Mostrar'} Busca
            </Button>
          </Box>
          
          <Collapse in={showFilters}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={8}>
                <TextField
                  fullWidth
                  size="small"
                  label="Buscar por nome, email ou CPF"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  variant="outlined"
                />
              </Grid>
              
              <Grid item xs={12} sm={3} md={2}>
                <Button
                  onClick={handleSearch}
                  variant="contained"
                  fullWidth
                  size="small"
                  startIcon={<SearchIcon />}
                  sx={{ height: 40 }}
                >
                  Buscar
                </Button>
              </Grid>
              
              <Grid item xs={12} sm={3} md={2}>
                <Button
                  onClick={clearSearch}
                  variant="outlined"
                  fullWidth
                  size="small"
                  sx={{ height: 40 }}
                >
                  Limpar
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
              rows={filteredCustomers}
              columns={columns}
              loading={loading}
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
                      {searchTerm ? 'Nenhum cliente encontrado' : 'Nenhum cliente cadastrado'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchTerm 
                        ? 'Tente ajustar o termo de busca ou cadastre um novo cliente.'
                        : 'Cadastre o primeiro cliente para começar.'
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
          {selectedCustomer ? 'Editar Cliente' : 'Novo Cliente'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nome"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  error={!!errors.name}
                  helperText={errors.name}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  error={!!errors.email}
                  helperText={errors.email}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <InputMask
                  mask="(99) 99999-9999"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                >
                  {(inputProps: any) => (
                    <TextField
                      {...inputProps}
                      fullWidth
                      label="Telefone"
                      error={!!errors.phone}
                      helperText={errors.phone}
                      margin="normal"
                      required
                    />
                  )}
                </InputMask>
              </Grid>
              <Grid item xs={12} md={6}>
                <InputMask
                  mask="999.999.999-99"
                  value={formData.cpf}
                  onChange={(e) => setFormData({ ...formData, cpf: e.target.value.replace(/\D/g, '') })}
                >
                  {(inputProps: any) => (
                    <TextField
                      {...inputProps}
                      fullWidth
                      label="CPF"
                      error={!!errors.cpf}
                      helperText={errors.cpf}
                      margin="normal"
                      required
                    />
                  )}
                </InputMask>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Endereço"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  error={!!errors.address}
                  helperText={errors.address}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cidade"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  error={!!errors.city}
                  helperText={errors.city}
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="UF"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value.toUpperCase().slice(0, 2) })}
                  error={!!errors.state}
                  helperText={errors.state}
                  margin="normal"
                  required
                  inputProps={{
                    maxLength: 2,
                    style: { textTransform: 'uppercase' }
                  }}
                  placeholder="SP"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <InputMask
                  mask="99999-999"
                  value={formData.zip_code}
                  onChange={(e) => setFormData({ ...formData, zip_code: e.target.value.replace(/\D/g, '') })}
                >
                  {(inputProps: any) => (
                    <TextField
                      {...inputProps}
                      fullWidth
                      label="CEP"
                      error={!!errors.zip_code}
                      helperText={errors.zip_code}
                      margin="normal"
                      required
                    />
                  )}
                </InputMask>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button onClick={handleSubmit} variant="contained">
            {selectedCustomer ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar para notificações */}
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
    </Container>
  );
};

export default Customers;

