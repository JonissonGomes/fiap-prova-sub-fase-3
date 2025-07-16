import { User } from '../types';

export enum UserRole {
  ADMIN = 'ADMIN',
  SALES = 'SALES',
  CUSTOMER = 'CUSTOMER'
}

export interface Permission {
  resource: string;
  action: string;
  role: UserRole;
}

// Definir permissões do sistema
export const permissions: Permission[] = [
  // Permissões para ADMIN - pode fazer tudo
  { resource: 'vehicles', action: 'view', role: UserRole.ADMIN },
  { resource: 'vehicles', action: 'create', role: UserRole.ADMIN },
  { resource: 'vehicles', action: 'edit', role: UserRole.ADMIN },
  { resource: 'vehicles', action: 'delete', role: UserRole.ADMIN },
  { resource: 'vehicles', action: 'buy', role: UserRole.ADMIN },
  { resource: 'sales', action: 'view', role: UserRole.ADMIN },
  { resource: 'sales', action: 'create', role: UserRole.ADMIN },
  { resource: 'sales', action: 'edit', role: UserRole.ADMIN },
  { resource: 'sales', action: 'delete', role: UserRole.ADMIN },
  { resource: 'customers', action: 'view', role: UserRole.ADMIN },
  { resource: 'customers', action: 'create', role: UserRole.ADMIN },
  { resource: 'customers', action: 'edit', role: UserRole.ADMIN },
  { resource: 'customers', action: 'delete', role: UserRole.ADMIN },
  { resource: 'payments', action: 'view', role: UserRole.ADMIN },
  { resource: 'payments', action: 'approve', role: UserRole.ADMIN },
  { resource: 'payments', action: 'cancel', role: UserRole.ADMIN },

  // Permissões para SALES - pode fazer tudo exceto aprovar/cancelar pagamentos
  { resource: 'vehicles', action: 'view', role: UserRole.SALES },
  { resource: 'vehicles', action: 'create', role: UserRole.SALES },
  { resource: 'vehicles', action: 'edit', role: UserRole.SALES },
  { resource: 'vehicles', action: 'buy', role: UserRole.SALES },
  { resource: 'sales', action: 'view', role: UserRole.SALES },
  { resource: 'sales', action: 'create', role: UserRole.SALES },
  { resource: 'sales', action: 'edit', role: UserRole.SALES },
  { resource: 'sales', action: 'delete', role: UserRole.SALES },
  { resource: 'customers', action: 'view', role: UserRole.SALES },
  { resource: 'customers', action: 'create', role: UserRole.SALES },
  { resource: 'customers', action: 'edit', role: UserRole.SALES },
  { resource: 'customers', action: 'delete', role: UserRole.SALES },
  { resource: 'payments', action: 'view', role: UserRole.SALES },

  // Permissões para CUSTOMER - apenas visualizar veículos e comprar
  { resource: 'vehicles', action: 'view', role: UserRole.CUSTOMER },
  { resource: 'vehicles', action: 'buy', role: UserRole.CUSTOMER },
  { resource: 'sales', action: 'view_own', role: UserRole.CUSTOMER }, // Apenas suas próprias vendas
];

// Funções utilitárias para verificar permissões
export const hasPermission = (user: User | null, resource: string, action: string): boolean => {
  if (!user) return false;

  const userRole = user.role as UserRole;
  
  return permissions.some(permission => 
    permission.resource === resource && 
    permission.action === action && 
    permission.role === userRole
  );
};

export const canViewVehicles = (user: User | null): boolean => {
  return hasPermission(user, 'vehicles', 'view');
};

export const canCreateVehicles = (user: User | null): boolean => {
  return hasPermission(user, 'vehicles', 'create');
};

export const canEditVehicles = (user: User | null): boolean => {
  return hasPermission(user, 'vehicles', 'edit');
};

export const canDeleteVehicles = (user: User | null): boolean => {
  return hasPermission(user, 'vehicles', 'delete');
};

export const canBuyVehicles = (user: User | null): boolean => {
  return hasPermission(user, 'vehicles', 'buy');
};

export const canViewSales = (user: User | null): boolean => {
  return hasPermission(user, 'sales', 'view');
};

export const canCreateSales = (user: User | null): boolean => {
  return hasPermission(user, 'sales', 'create');
};

export const canEditSales = (user: User | null): boolean => {
  return hasPermission(user, 'sales', 'edit');
};

export const canDeleteSales = (user: User | null): boolean => {
  return hasPermission(user, 'sales', 'delete');
};

export const canViewCustomers = (user: User | null): boolean => {
  return hasPermission(user, 'customers', 'view');
};

export const canCreateCustomers = (user: User | null): boolean => {
  return hasPermission(user, 'customers', 'create');
};

export const canEditCustomers = (user: User | null): boolean => {
  return hasPermission(user, 'customers', 'edit');
};

export const canDeleteCustomers = (user: User | null): boolean => {
  return hasPermission(user, 'customers', 'delete');
};

export const canViewPayments = (user: User | null): boolean => {
  return hasPermission(user, 'payments', 'view');
};

export const canApprovePayments = (user: User | null): boolean => {
  return hasPermission(user, 'payments', 'approve');
};

export const canCancelPayments = (user: User | null): boolean => {
  return hasPermission(user, 'payments', 'cancel');
};

export const isAdmin = (user: User | null): boolean => {
  return user?.role === UserRole.ADMIN;
};

export const isSales = (user: User | null): boolean => {
  return user?.role === UserRole.SALES;
};

export const isCustomer = (user: User | null): boolean => {
  return user?.role === UserRole.CUSTOMER;
};

export const getRoleDisplayName = (role: string): string => {
  switch (role) {
    case UserRole.ADMIN:
      return 'Administrador';
    case UserRole.SALES:
      return 'Vendedor';
    case UserRole.CUSTOMER:
      return 'Cliente';
    default:
      return role;
  }
};

export const getMenuItemsForRole = (role: string) => {
  const baseItems = [
    { text: 'Início', icon: 'dashboard', path: '/', roles: ['ADMIN', 'CUSTOMER', 'SALES'] },
  ];

  if (role === UserRole.CUSTOMER) {
    return [
      ...baseItems,
      { text: 'Veículos', icon: 'vehicle', path: '/vehicles', roles: ['CUSTOMER'] },
      { text: 'Minhas Compras', icon: 'sale', path: '/my-purchases', roles: ['CUSTOMER'] },
    ];
  }

  if (role === UserRole.SALES) {
    return [
      ...baseItems,
      { text: 'Veículos', icon: 'vehicle', path: '/vehicles', roles: ['SALES'] },
      { text: 'Vendas', icon: 'sale', path: '/sales', roles: ['SALES'] },
      { text: 'Clientes', icon: 'customer', path: '/customers', roles: ['SALES'] },
      { text: 'Pagamentos', icon: 'payment', path: '/payments', roles: ['SALES'] },
    ];
  }

  if (role === UserRole.ADMIN) {
    return [
      ...baseItems,
      { text: 'Veículos', icon: 'vehicle', path: '/vehicles', roles: ['ADMIN'] },
      { text: 'Vendas', icon: 'sale', path: '/sales', roles: ['ADMIN'] },
      { text: 'Clientes', icon: 'customer', path: '/customers', roles: ['ADMIN'] },
      { text: 'Pagamentos', icon: 'payment', path: '/payments', roles: ['ADMIN'] },
    ];
  }

  return baseItems;
}; 