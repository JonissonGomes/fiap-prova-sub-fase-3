# Unified Vehicle Sales API

API unificada para o sistema de vendas de veículos, consolidando as funcionalidades dos 4 microserviços originais em uma única aplicação Node.js.

## 🚀 Funcionalidades

### Autenticação (`/auth`)
- Registro e login de usuários
- Validação e renovação de tokens JWT
- Gerenciamento de perfis
- Controle de acesso baseado em roles (ADMIN, SALES, CUSTOMER)

### Veículos (`/vehicles`)
- CRUD completo de veículos
- Controle de status (DISPONÍVEL, RESERVADO, VENDIDO)
- Filtros e busca avançada
- Webhooks para atualização de status

### Clientes (`/customers`)
- Gerenciamento de clientes
- Validação de CPF
- Busca por CPF, email, telefone
- Soft delete

### Vendas (`/sales`)
- Processo completo de vendas
- Controle de status de pagamento
- Estatísticas de vendas
- Integração com veículos e clientes

### Rate Limiting (`/rate-limit`)
- Controle de taxa de requisições
- Configuração dinâmica
- Estatísticas de uso

## 🛠️ Tecnologias

- **Node.js** 18+
- **Express.js** - Framework web
- **MongoDB** - Banco de dados
- **Mongoose** - ODM
- **JWT** - Autenticação
- **bcryptjs** - Hash de senhas
- **express-rate-limit** - Rate limiting
- **express-validator** - Validação de dados

## 📦 Instalação

### Pré-requisitos
- Node.js 18+
- MongoDB
- npm ou yarn

### 1. Clonar e instalar dependências
```bash
cd unified-api
npm install
```

### 2. Configurar variáveis de ambiente
```bash
cp config.env .env
# Editar .env com suas configurações
```

### 3. Iniciar MongoDB
```bash
# Com Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Ou instalar localmente
```

### 4. Popular dados iniciais
```bash
npm run populate
```

### 5. Iniciar a aplicação
```bash
# Desenvolvimento
npm run dev

# Produção
npm start
```

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Servidor
PORT=3001
NODE_ENV=development

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=unified_vehicle_db

# JWT
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=24h
REFRESH_TOKEN_SECRET=your-refresh-token-secret
REFRESH_TOKEN_EXPIRES_IN=7d

# Admin padrão
DEFAULT_ADMIN_EMAIL=admin@vehiclesales.com
DEFAULT_ADMIN_PASSWORD=admin123

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## 📚 API Endpoints

### Autenticação
```
POST /auth/register     - Registrar usuário
POST /auth/login        - Fazer login
POST /auth/refresh      - Renovar token
GET  /auth/validate     - Validar token
POST /auth/logout       - Fazer logout
GET  /auth/profile      - Obter perfil
PUT  /auth/profile      - Atualizar perfil
GET  /auth/users        - Listar usuários (admin)
```

### Veículos
```
GET    /vehicles              - Listar veículos
GET    /vehicles/available    - Veículos disponíveis
GET    /vehicles/:id          - Obter veículo
POST   /vehicles              - Criar veículo
PUT    /vehicles/:id          - Atualizar veículo
DELETE /vehicles/:id          - Deletar veículo
PATCH  /vehicles/:id/status   - Atualizar status
```

### Clientes
```
GET    /customers           - Listar clientes
GET    /customers/:id       - Obter cliente
GET    /customers/cpf/:cpf  - Buscar por CPF
POST   /customers           - Criar cliente
PUT    /customers/:id       - Atualizar cliente
DELETE /customers/:id       - Deletar cliente
```

### Vendas
```
GET    /sales                    - Listar vendas
GET    /sales/:id                - Obter venda
POST   /sales                    - Criar venda
POST   /sales/purchase           - Realizar compra
PUT    /sales/:id                - Atualizar venda
PUT    /sales/:id/status         - Atualizar status
PATCH  /sales/:id/payment/confirm - Confirmar pagamento
DELETE /sales/:id                - Deletar venda
```

## 🔐 Autenticação

A API usa JWT para autenticação. Inclua o token no header:

```
Authorization: Bearer <token>
```

### Roles disponíveis:
- **ADMIN**: Acesso total
- **SALES**: Gerenciar veículos, clientes e vendas
- **CUSTOMER**: Acesso limitado

## 🚦 Rate Limiting

- **Global**: 100 requisições por 15 minutos
- **Login**: 5 tentativas por 15 minutos
- **Registro**: 20 tentativas por 15 minutos

## 🐳 Docker

```bash
# Build
docker build -t unified-vehicle-api .

# Run
docker run -p 3001:3001 --env-file .env unified-vehicle-api
```

## 📊 Monitoramento

### Health Check
```
GET /health
```

### Rate Limit Stats (admin)
```
GET /rate-limit/stats
GET /rate-limit/config
```

## 🧪 Testes

```bash
npm test
```

## 🔄 Migração dos Microserviços

Esta API unifica as funcionalidades dos seguintes microserviços:

1. **auth-service** → `/auth`
2. **core-service** → `/vehicles`
3. **customer-service** → `/customers`
4. **sales-service** → `/sales`

### Compatibilidade
- Mantém compatibilidade com as APIs originais
- Mesmos endpoints e estruturas de dados
- Rate limiting preservado
- Sistema de autenticação melhorado

## 📝 Logs

A aplicação gera logs estruturados com informações de:
- Requisições HTTP
- Operações de banco de dados
- Autenticação e autorização
- Erros e exceções

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
src/
├── config/          # Configurações
├── middleware/      # Middlewares
├── models/          # Modelos Mongoose
├── routes/          # Rotas da API
├── utils/           # Utilitários
└── server.js        # Arquivo principal
```

### Scripts Disponíveis
```bash
npm start          # Iniciar produção
npm run dev        # Iniciar desenvolvimento
npm run populate   # Popular dados
npm test           # Executar testes
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
