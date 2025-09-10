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
  Grid,
  Avatar,
  CssBaseline,
  Divider,
  // Card,
  // CardContent,
  // Stepper,
  // Step,
  StepLabel
} from '@mui/material';
import { 
  DirectionsCar as CarIcon,
  PersonAdd as PersonAddIcon,
  Visibility,
  VisibilityOff,
  Business as BusinessIcon,
  Person as PersonIcon
} from '@mui/icons-material';
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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2
      }}
    >
      <CssBaseline />
      <Container component="main" maxWidth="md">
        <Paper
          elevation={24}
          sx={{
            padding: { xs: 3, md: 4 },
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            {/* Logo e Título */}
            <Avatar
              sx={{
                m: 2,
                bgcolor: 'primary.main',
                width: 80,
                height: 80,
                boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
              }}
            >
              <CarIcon sx={{ fontSize: 40 }} />
            </Avatar>
            
            <Typography 
              component="h1" 
              variant="h4" 
              sx={{ 
                mb: 1,
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}
            >
              Criar Conta
            </Typography>
            
            <Typography 
              component="h2" 
              variant="h6" 
              sx={{ 
                mb: 4,
                color: 'text.secondary',
                fontWeight: 400,
                textAlign: 'center'
              }}
            >
              Junte-se ao nosso sistema de vendas de veículos
            </Typography>
            
            {errors.submit && (
              <Alert 
                severity="error" 
                sx={{ 
                  width: '100%', 
                  mb: 3,
                  borderRadius: 2,
                  '& .MuiAlert-message': {
                    fontSize: '0.9rem'
                  }
                }}
              >
                {errors.submit}
              </Alert>
            )}
            
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
              <Grid container spacing={3}>
                {/* Informações Básicas */}
                <Grid item xs={12}>
                  <Typography variant="h6" sx={{ mb: 2, color: 'primary.main', fontWeight: 'bold' }}>
                    Informações Básicas
                  </Typography>
                </Grid>
                
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
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&:hover fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
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
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&:hover fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl 
                    fullWidth 
                    margin="normal" 
                    error={!!errors.role}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&:hover fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  >
                    <InputLabel id="role-label">Tipo de Usuário</InputLabel>
                    <Select
                      labelId="role-label"
                      id="role"
                      value={formData.role}
                      label="Tipo de Usuário"
                      onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                    >
                      <MenuItem value="CUSTOMER">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <PersonIcon />
                          <Box>
                            <Typography variant="body1">Cliente</Typography>
                            <Typography variant="caption" color="text.secondary">
                              Comprar veículos
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                      <MenuItem value="SALES">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <BusinessIcon />
                          <Box>
                            <Typography variant="body1">Vendedor</Typography>
                            <Typography variant="caption" color="text.secondary">
                              Gerenciar vendas
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                      <MenuItem value="ADMIN">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <BusinessIcon />
                          <Box>
                            <Typography variant="body1">Administrador</Typography>
                            <Typography variant="caption" color="text.secondary">
                              Acesso total
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                    </Select>
                    {errors.role && (
                      <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                        {errors.role}
                      </Typography>
                    )}
                  </FormControl>
                </Grid>

                {/* Informações do Cliente */}
                {isCustomer && (
                  <>
                    <Grid item xs={12}>
                      <Typography variant="h6" sx={{ mb: 2, color: 'primary.main', fontWeight: 'bold' }}>
                        Informações do Cliente
                      </Typography>
                    </Grid>
                    
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
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 2,
                                '&:hover fieldset': {
                                  borderColor: 'primary.main',
                                },
                              },
                            }}
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
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 2,
                                '&:hover fieldset': {
                                  borderColor: 'primary.main',
                                },
                              },
                            }}
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
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            '&:hover fieldset': {
                              borderColor: 'primary.main',
                            },
                          },
                        }}
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
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            '&:hover fieldset': {
                              borderColor: 'primary.main',
                            },
                          },
                        }}
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
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            '&:hover fieldset': {
                              borderColor: 'primary.main',
                            },
                          },
                        }}
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
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 2,
                                '&:hover fieldset': {
                                  borderColor: 'primary.main',
                                },
                              },
                            }}
                          />
                        )}
                      </InputMask>
                    </Grid>
                  </>
                )}
                
                {/* Senhas */}
                <Grid item xs={12}>
                  <Typography variant="h6" sx={{ mb: 2, color: 'primary.main', fontWeight: 'bold' }}>
                    Segurança
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="password"
                    label="Senha"
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    autoComplete="new-password"
                    value={formData.password}
                    onChange={handleChange('password')}
                    error={!!errors.password}
                    helperText={errors.password}
                    InputProps={{
                      endAdornment: (
                        <Button
                          onClick={() => setShowPassword(!showPassword)}
                          sx={{ minWidth: 'auto', p: 1 }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </Button>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&:hover fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    margin="normal"
                    required
                    fullWidth
                    name="confirmPassword"
                    label="Confirmar Senha"
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange('confirmPassword')}
                    error={!!errors.confirmPassword}
                    helperText={errors.confirmPassword}
                    InputProps={{
                      endAdornment: (
                        <Button
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          sx={{ minWidth: 'auto', p: 1 }}
                        >
                          {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                        </Button>
                      ),
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        '&:hover fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                    }}
                  />
                </Grid>
              </Grid>
              
              <Button
                type="submit"
                fullWidth
                variant="contained"
                startIcon={!isLoading && <PersonAddIcon />}
                disabled={isLoading}
                sx={{
                  mt: 4,
                  mb: 3,
                  py: 1.5,
                  borderRadius: 2,
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                  boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)',
                    boxShadow: '0 12px 40px rgba(102, 126, 234, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease-in-out',
                }}
              >
                {isLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Criar Conta'
                )}
              </Button>
              
              <Divider sx={{ my: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  ou
                </Typography>
              </Divider>
              
              <Box textAlign="center">
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Já tem uma conta?
                </Typography>
                <Link 
                  component={RouterLink} 
                  to="/login" 
                  variant="body1"
                  sx={{
                    fontWeight: 'bold',
                    textDecoration: 'none',
                    color: 'primary.main',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Faça login aqui
                </Link>
              </Box>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default Register;