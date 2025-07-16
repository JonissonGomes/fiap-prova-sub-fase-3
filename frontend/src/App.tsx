import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';
import Layout from './components/Layout';
import VehiclesWithRoles from './pages/VehiclesWithRoles';
import Sales from './pages/Sales';
import Payments from './pages/Payments';
import Customers from './pages/Customers';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import MyPurchases from './pages/MyPurchases';

// Componente para proteger rotas
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Componente para rotas públicas (redireciona se já autenticado)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return !isAuthenticated ? <>{children}</> : <Navigate to="/" />;
};

const AppContent: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Rotas públicas */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Rotas protegidas */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/vehicles" element={<VehiclesWithRoles />} />
                  <Route path="/sales" element={<Sales />} />
                                      <Route path="/payments" element={<Payments />} />
                    <Route path="/customers" element={<Customers />} />
                    <Route path="/my-purchases" element={<MyPurchases />} />
                    <Route path="/profile" element={<Profile />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App; 