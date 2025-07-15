# Configuração Manual do Keycloak

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 

## Acesso ao Console Admin

1. **Abrir o navegador** e acessar: `http://localhost:8080/admin`
2. **Fazer login** com:
   - Usuário: `admin`
   - Senha: `admin123`

## Passo 1: Criar o Realm

1. **Clique em "Create Realm"** (ou no dropdown "Master" → "Create Realm")
2. **Preencha os dados**:
   - **Realm name**: `vehicle-sales`
   - **Display name**: `Vehicle Sales`
   - **Enabled**: ✅ (marcado)
3. **Clique em "Create"**

## Passo 2: Criar o Client

1. **No menu lateral**, clique em **"Clients"**
2. **Clique em "Create client"**
3. **Preencha os dados**:
   - **Client type**: `OpenID Connect`
   - **Client ID**: `vehicle-sales-app`
   - **Name**: `Vehicle Sales App`
   - **Description**: `Client for Vehicle Sales Application`
4. **Clique em "Next"**

### Configurações de Capacidade
- **Client authentication**: ✅ (ON)
- **Authorization**: ❌ (OFF)
- **Standard flow**: ✅ (ON)
- **Direct access grants**: ✅ (ON)
- **Implicit flow**: ❌ (OFF)
- **Service accounts roles**: ✅ (ON)

5. **Clique em "Next"**

### Configurações de Login
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Valid post logout redirect URIs**: 
  - `http://localhost:3000/*`
  - `http://localhost:3001/*`
- **Web origins**: 
  - `http://localhost:3000`
  - `http://localhost:3001`

6. **Clique em "Save"**

## Passo 3: Obter o Client Secret

1. **Na página do client criado**, clique na aba **"Credentials"**
2. **Copie o "Client secret"** que aparece no campo
3. **Anote este valor** - você precisará dele nos arquivos .env

## Passo 4: Criar as Roles

1. **No menu lateral**, clique em **"Realm roles"**
2. **Clique em "Create role"**
3. **Crie as seguintes roles**:

### Role ADMIN
- **Role name**: `ADMIN`
- **Description**: `Administrator role`
- **Clique em "Save"**

### Role CUSTOMER  
- **Role name**: `CUSTOMER`
- **Description**: `Customer role`
- **Clique em "Save"**

### Role SALES
- **Role name**: `SALES`
- **Description**: `Sales role`
- **Clique em "Save"**

## Passo 5: Configurar as Variáveis de Ambiente

Após obter o client secret, adicione as seguintes variáveis aos seus arquivos .env:

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=vehicle-sales
KEYCLOAK_CLIENT_ID=vehicle-sales-app
KEYCLOAK_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
```

## Passo 6: Criar um Usuário de Teste (Opcional)

1. **No menu lateral**, clique em **"Users"**
2. **Clique em "Add user"**
3. **Preencha os dados**:
   - **Username**: `admin@test.com`
   - **Email**: `admin@test.com`
   - **First name**: `Admin`
   - **Last name**: `User`
   - **Email verified**: ✅ (ON)
   - **Enabled**: ✅ (ON)
4. **Clique em "Create"**

### Definir Senha
1. **Clique na aba "Credentials"**
2. **Clique em "Set password"**
3. **Preencha**:
   - **Password**: `admin123`
   - **Password confirmation**: `admin123`
   - **Temporary**: ❌ (OFF)
4. **Clique em "Save"**

### Atribuir Role
1. **Clique na aba "Role mapping"**
2. **Clique em "Assign role"**
3. **Selecione a role "ADMIN"**
4. **Clique em "Assign"**

## Verificação

Para verificar se tudo está funcionando:

1. **Acesse**: `http://localhost:8080/realms/vehicle-sales/protocol/openid-connect/auth?client_id=vehicle-sales-app&response_type=code&redirect_uri=http://localhost:3000`
2. **Faça login** com o usuário criado
3. **Deve redirecionar** para localhost:3000 (mesmo que dê erro, o importante é que o Keycloak funcione)

## Informações Importantes

- **URL do Keycloak**: `http://localhost:8080`
- **Realm**: `vehicle-sales`
- **Client ID**: `vehicle-sales-app`
- **Client Secret**: (obtido no passo 3)
- **Admin Console**: `http://localhost:8080/admin`
- **Usuário Admin**: `admin` / `admin123` 