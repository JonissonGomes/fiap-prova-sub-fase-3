# Documentação da API - Sistema de Vendas de Veículos

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 

## 📋 Visão Geral

Este documento descreve as APIs dos microsserviços do sistema de vendas de veículos, incluindo autenticação, autorização e funcionalidades específicas de cada serviço.

## 🔐 Configuração do Keycloak

### Pré-requisitos
Antes de usar as APIs, é necessário configurar o Keycloak:

```bash
# 1. Iniciar Keycloak
make keycloak

# 2. Configurar automaticamente
make keycloak-setup

# 3. Obter client secret
make keycloak-secret

# 4. Validar configuração
make keycloak-validate
```

### Credenciais Padrão
- **Console Admin**: http://localhost:8080/admin (admin/admin123)
- **Usuário da aplicação**: admin/admin123 (role: ADMIN)

### Verificação Rápida
```bash
# Testar se Keycloak está funcionando
curl http://localhost:8080/realms/vehicle-sales

# Testar autenticação
curl -X POST http://localhost:8002/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🔑 Autenticação e Autorização

### Fluxo de Autenticação
1. **Login**: POST `/auth/login` → Recebe `access_token` e `refresh_token`
2. **Uso**: Incluir header `Authorization: Bearer <access_token>` em todas as requisições
3. **Renovação**: POST `/auth/refresh` quando token expira
4. **Logout**: POST `/auth/logout` para invalidar tokens

### Roles Disponíveis
- **ADMIN**: Acesso total ao sistema
- **SALES**: Gerenciamento de vendas e relatórios
- **CUSTOMER**: Acesso básico para compras

### Headers Obrigatórios
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## 🛡️ Rate Limiting

### Limites por Tipo de Endpoint
- **Autenticação**: 5 requests/minuto
- **Geral**: 100 requests/minuto
- **Listagem**: 30 requests/minuto
- **Admin**: 50 requests/minuto

### Headers de Resposta
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Erro 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

## 🔧 Auth Service (porta 8002)

### Base URL
```
http://localhost:8002
```

### Endpoints

#### POST /auth/register
Registra um novo usuário no sistema.

**Request:**
```json
{
  "username": "joao.silva",
  "email": "joao@example.com",
  "password": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login
Autentica um usuário e retorna tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300,
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

#### POST /auth/refresh
Renova o access token usando o refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

#### POST /auth/logout
Invalida os tokens do usuário.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/profile
Retorna informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "ADMIN",
  "status": "ACTIVE",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /auth/profile
Atualiza informações do usuário autenticado.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "first_name": "João",
  "last_name": "Silva",
  "email": "joao.silva@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "joao.silva",
  "email": "joao.silva@example.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": "CUSTOMER",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Rate Limiting Endpoints (Admin only)

#### GET /rate-limit/stats
Retorna estatísticas de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "total_requests": 1500,
  "blocked_requests": 25,
  "active_limits": {
    "192.168.1.100": {
      "requests": 95,
      "limit": 100,
      "reset_time": "2024-01-01T00:05:00Z"
    }
  }
}
```

#### GET /rate-limit/config
Retorna configuração de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "limits": {
    "auth": 5,
    "general": 100,
    "listing": 30,
    "admin": 50
  },
  "window_seconds": 60,
  "redis_enabled": true
}
```

#### DELETE /rate-limit/reset
Reseta contadores de rate limiting.

**Headers:**
```http
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "message": "Rate limit counters reset successfully"
}
```

## 🚗 Core Service (porta 8000)

### Base URL
```
http://localhost:8000
```

### Endpoints

#### GET /vehicles
Lista veículos com filtros opcionais.

**Query Parameters:**
- `status`: DISPONIVEL, RESERVADO, VENDIDO
- `marca`: Marca do veículo
- `modelo`: Modelo do veículo
- `ano_min`: Ano mínimo
- `ano_max`: Ano máximo
- `preco_min`: Preço mínimo
- `preco_max`: Preço máximo
- `sort_by`: campo para ordenação (preco, ano, marca)
- `sort_order`: asc ou desc
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "vehicles": [
    {
      "id": "uuid",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2023,
      "preco": 85000.00,
      "status": "DISPONIVEL",
      "cor": "Branco",
      "combustivel": "Flex",
      "km": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /vehicles
Cria um novo veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /vehicles/{id}
Retorna detalhes de um veículo específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 95000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /vehicles/{id}
Atualiza um veículo existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "preco": 90000.00,
  "km": 1000,
  "status": "DISPONIVEL"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "marca": "Honda",
  "modelo": "Civic",
  "ano": 2023,
  "preco": 90000.00,
  "status": "DISPONIVEL",
  "cor": "Preto",
  "combustivel": "Flex",
  "km": 1000,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /vehicles/{id}
Remove um veículo.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 💰 Sales Service (porta 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /sales
Lista vendas com filtros opcionais.

**Query Parameters:**
- `status`: PENDENTE, APROVADA, REJEITADA, CANCELADA
- `vehicle_id`: ID do veículo
- `customer_id`: ID do cliente
- `date_from`: Data inicial (YYYY-MM-DD)
- `date_to`: Data final (YYYY-MM-DD)
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sales": [
    {
      "id": "uuid",
      "vehicle_id": "uuid",
      "customer_id": "uuid",
      "total_amount": 85000.00,
      "status": "APROVADA",
      "payment_method": "FINANCIAMENTO",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /sales
Cria uma nova venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "PENDENTE",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /sales/{id}
Retorna detalhes de uma venda específica.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "down_payment": 25000.00,
  "financing_months": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /sales/{id}
Atualiza uma venda existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "status": "APROVADA",
  "notes": "Aprovação automática - documentos ok"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "vehicle_id": "uuid",
  "customer_id": "uuid",
  "total_amount": 85000.00,
  "status": "APROVADA",
  "payment_method": "FINANCIAMENTO",
  "notes": "Aprovação automática - documentos ok",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /sales/{id}/approve
Aprova uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "notes": "Documentos verificados e aprovados"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "APROVADA",
  "message": "Venda aprovada com sucesso"
}
```

#### POST /sales/{id}/reject
Rejeita uma venda.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "reason": "Documentos incompletos",
  "notes": "Falta comprovante de renda"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "status": "REJEITADA",
  "message": "Venda rejeitada"
}
```

## 👥 Customer Service (porta 8003)

### Base URL
```
http://localhost:8003
```

### Endpoints

#### GET /customers
Lista clientes com filtros opcionais.

**Query Parameters:**
- `name`: Nome do cliente
- `email`: Email do cliente
- `cpf`: CPF do cliente
- `phone`: Telefone do cliente
- `city`: Cidade do cliente
- `state`: Estado do cliente
- `page`: Página (padrão: 1)
- `limit`: Itens por página (padrão: 20)

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "customers": [
    {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(11) 99999-9999",
      "cpf": "123.456.789-00",
      "address": "Rua das Flores, 123",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01234-567",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

#### POST /customers
Cria um novo cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /customers/{id}
Retorna detalhes de um cliente específico.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 88888-8888",
  "cpf": "987.654.321-00",
  "address": "Av. Paulista, 456",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310-100",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /customers/{id}
Atualiza um cliente existente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "phone": "(11) 77777-7777",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "(11) 77777-7777",
  "cpf": "987.654.321-00",
  "address": "Rua Nova, 789",
  "city": "Rio de Janeiro",
  "state": "RJ",
  "zip_code": "20000-000",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /customers/{id}
Remove um cliente.

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (204):**
```
No content
```

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

#### 400 - Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid request data",
  "details": {
    "email": ["Invalid email format"],
    "cpf": ["CPF is required"]
  }
}
```

#### 401 - Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

#### 403 - Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

#### 404 - Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

#### 409 - Conflict
```json
{
  "error": "Conflict",
  "message": "Resource already exists",
  "details": {
    "field": "email",
    "value": "user@example.com"
  }
}
```

#### 422 - Unprocessable Entity
```json
{
  "error": "Validation error",
  "message": "The given data was invalid",
  "details": {
    "cpf": ["CPF already exists"],
    "email": ["Email format is invalid"]
  }
}
```

#### 429 - Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again later.",
  "retry_after": 60
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```bash
# Verificar se Keycloak está rodando
make keycloak-validate

# Verificar se client secret está correto
cat /tmp/keycloak-credentials-development.env

# Reconfigurar Keycloak
make keycloak-setup
make keycloak-secret
```

#### 2. Rate Limiting
```bash
# Verificar estatísticas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/rate-limit/stats

# Resetar contadores (admin only)
curl -X DELETE -H "Authorization: Bearer <admin_token>" \
  http://localhost:8002/rate-limit/reset
```

#### 3. Serviços Indisponíveis
```bash
# Verificar status
make status

# Verificar logs
make logs

# Reiniciar serviços
make restart
```

## 📚 Recursos Adicionais

### Documentação
- [Guia de Início Rápido](../docs/KEYCLOAK_QUICKSTART.md)
- [Keycloak em Produção](../docs/KEYCLOAK_PRODUCTION_GUIDE.md)
- [Arquitetura](../docs/ARCHITECTURE.md)
- [Deploy](../docs/DEPLOYMENT.md)

### Ferramentas Úteis
- **Postman Collection**: `docs/postman_collection.json`
- **Swagger UI**: Disponível em cada serviço (`/docs`)
- **Keycloak Console**: http://localhost:8080/admin

### Comandos Úteis
```bash
make keycloak-validate    # Validar configuração
make keycloak-quickstart  # Guia rápido
make test-rate-limiting   # Testar rate limiting
make docs                 # Mostrar documentação
``` 