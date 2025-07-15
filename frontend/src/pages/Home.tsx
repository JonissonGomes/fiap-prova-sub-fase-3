import React from 'react';
import { Box, Typography, Grid, Paper, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Sistema de Vendas de Veículos da FIAP
      </Typography>
      <Typography variant="body1" paragraph>
        O sistema foi desenvolvido para a disciplina de Arquitetura de Software do curso de Desenvolvimento de Sistemas da FIAP, com o intuito de aplicar os conceitos de arquitetura de software e de microserviços.
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Veículos
            </Typography>
            <Typography variant="body2" paragraph>
              Gerencie o cadastro de veículos, incluindo marca, modelo, ano, cor e preço.
            </Typography>
            <Button
              variant="contained"
              component={RouterLink}
              to="/vehicles"
              fullWidth
            >
              Acessar
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Vendas
            </Typography>
            <Typography variant="body2" paragraph>
              Registre vendas de veículos, acompanhe o status e gerencie os pagamentos.
            </Typography>
            <Button
              variant="contained"
              component={RouterLink}
              to="/sales"
              fullWidth
            >
              Acessar
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Pagamentos
            </Typography>
            <Typography variant="body2" paragraph>
              Acompanhe e gerencie os pagamentos das vendas realizadas no sistema de forma direta.
            </Typography>
            <Button
              variant="contained"
              component={RouterLink}
              to="/payments"
              fullWidth
            >
              Acessar
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Home; 