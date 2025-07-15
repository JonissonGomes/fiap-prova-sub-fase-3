import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import InputMask from 'react-input-mask';
import { useAuth } from '../contexts/AuthContext';
import { customerService } from '../services/api';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'CUSTOMER',
    // Campos do cliente (obrigatórios para CUSTOMER)
    cpf: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Senha deve ter pelo menos 8 caracteres';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirmação de senha é obrigatória';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Senhas não coincidem';
    }

    if (!formData.role) {
      newErrors.role = 'Tipo de usuário é obrigatório';
    }

    // Validações específicas para CUSTOMER
    if (formData.role === 'CUSTOMER') {
      if (!formData.cpf.trim()) {
        newErrors.cpf = 'CPF é obrigatório para clientes';
      } else if (formData.cpf.replace(/\D/g, '').length !== 11) {
        newErrors.cpf = 'CPF deve ter 11 dígitos';
      }

      if (!formData.phone.trim()) {
        newErrors.phone = 'Telefone é obrigatório para clientes';
      }

      if (!formData.address.trim()) {
        newErrors.address = 'Endereço é obrigatório para clientes';
      }

      if (!formData.city.trim()) {
        newErrors.city = 'Cidade é obrigatória para clientes';
      }

      if (!formData.state.trim()) {
        newErrors.state = 'Estado é obrigatório para clientes';
      }

      if (!formData.zip_code.trim()) {
        newErrors.zip_code = 'CEP é obrigatório para clientes';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Primeiro, registrar o usuário
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: formData.role as 'ADMIN' | 'CUSTOMER' | 'SALES'
      });

      // Se for CUSTOMER, criar também o registro de cliente
      if (formData.role === 'CUSTOMER') {
        try {
          await customerService.create({
            name: formData.name,
            email: formData.email,
            phone: formData.phone.replace(/\D/g, ''),
            cpf: formData.cpf.replace(/\D/g, ''),
            address: formData.address,
            city: formData.city,
            state: formData.state,
            zip_code: formData.zip_code.replace(/\D/g, '')
          });
        } catch (customerError) {
          console.error('Erro ao criar registro de cliente:', customerError);
          // Não falha o registro se não conseguir criar o cliente
        }
      }

      navigate('/');
    } catch (err: any) {
      setErrors({
        submit: err.response?.data?.detail || 'Erro ao criar conta'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
    
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const isCustomer = formData.role === 'CUSTOMER';

  return (
    <Container component="main" maxWidth="md">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Criar Conta
          </Typography>
          
          {errors.submit && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.submit}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="name"
                  label="Nome Completo"
                  name="name"
                  autoComplete="name"
                  autoFocus
                  value={formData.name}
                  onChange={handleChange('name')}
                  error={!!errors.name}
                  helperText={errors.name}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email"
                  name="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange('email')}
                  error={!!errors.email}
                  helperText={errors.email}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth margin="normal" error={!!errors.role}>
                  <InputLabel id="role-label">Tipo de Usuário</InputLabel>
                  <Select
                    labelId="role-label"
                    id="role"
                    value={formData.role}
                    label="Tipo de Usuário"
                    onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  >
                    <MenuItem value="CUSTOMER">Cliente</MenuItem>
                    <MenuItem value="SALES">Vendedor</MenuItem>
                    <MenuItem value="ADMIN">Administrador</MenuItem>
                  </Select>
                  {errors.role && (
                    <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                      {errors.role}
                    </Typography>
                  )}
                </FormControl>
              </Grid>

              {isCustomer && (
                <>
                  <Grid item xs={12} md={6}>
                    <InputMask
                      mask="999.999.999-99"
                      value={formData.cpf}
                      onChange={handleChange('cpf')}
                    >
                      {(inputProps: any) => (
                        <TextField
                          {...inputProps}
                          margin="normal"
                          required
                          fullWidth
                          label="CPF"
                          error={!!errors.cpf}
                          helperText={errors.cpf}
                        />
                      )}
                    </InputMask>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <InputMask
                      mask="(99) 99999-9999"
                      value={formData.phone}
                      onChange={handleChange('phone')}
                    >
                      {(inputProps: any) => (
                        <TextField
                          {...inputProps}
                          margin="normal"
                          required
                          fullWidth
                          label="Telefone"
                          error={!!errors.phone}
                          helperText={errors.phone}
                        />
                      )}
                    </InputMask>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      margin="normal"
                      required
                      fullWidth
                      label="Endereço"
                      value={formData.address}
                      onChange={handleChange('address')}
                      error={!!errors.address}
                      helperText={errors.address}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <TextField
                      margin="normal"
                      required
                      fullWidth
                      label="Cidade"
                      value={formData.city}
                      onChange={handleChange('city')}
                      error={!!errors.city}
                      helperText={errors.city}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <TextField
                      margin="normal"
                      required
                      fullWidth
                      label="Estado"
                      value={formData.state}
                      onChange={handleChange('state')}
                      error={!!errors.state}
                      helperText={errors.state}
                      inputProps={{ maxLength: 2 }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <InputMask
                      mask="99999-999"
                      value={formData.zip_code}
                      onChange={handleChange('zip_code')}
                    >
                      {(inputProps: any) => (
                        <TextField
                          {...inputProps}
                          margin="normal"
                          required
                          fullWidth
                          label="CEP"
                          error={!!errors.zip_code}
                          helperText={errors.zip_code}
                        />
                      )}
                    </InputMask>
                  </Grid>
                </>
              )}
              
              <Grid item xs={12} md={6}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Senha"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange('password')}
                  error={!!errors.password}
                  helperText={errors.password}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Confirmar Senha"
                  type="password"
                  id="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange('confirmPassword')}
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword}
                />
              </Grid>
            </Grid>
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Criar Conta'}
            </Button>
            
            <Grid container justifyContent="flex-end">
              <Grid item>
                <Link component={RouterLink} to="/login" variant="body2">
                  Já tem uma conta? Faça login
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;