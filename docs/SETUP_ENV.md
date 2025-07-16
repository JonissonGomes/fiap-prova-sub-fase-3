# Configuração do Arquivo .env

Este projeto agora utiliza variáveis de ambiente carregadas a partir de um arquivo `.env` para maior segurança e flexibilidade na configuração.

## Passos para Configurar

### 1. Criar o arquivo .env

Na raiz do projeto, crie um arquivo `.env` copiando o conteúdo do arquivo `.env.example`:

```bash
cp .env.example .env
```

### 2. Verificar as Variáveis

O arquivo `.env` contém todas as variáveis de ambiente necessárias para executar o projeto:

- **Keycloak**: Configurações do servidor de autenticação
- **Redis**: URL do servidor Redis para rate limiting
- **MongoDB**: URLs e configurações dos bancos de dados de cada serviço
- **Serviços**: URLs para comunicação entre microserviços
- **Frontend**: Configurações do React

### 3. Personalizar se Necessário

Você pode personalizar as variáveis conforme sua necessidade:

- Para produção, altere os valores de senhas e secrets
- Para desenvolvimento local, os valores padrão devem funcionar
- Para diferentes ambientes, crie arquivos `.env.development`, `.env.production`, etc.

### 4. Executar o Projeto

Após criar o arquivo `.env`, você pode executar o projeto normalmente:

```bash
docker-compose up -d
```

## Segurança

⚠️ **IMPORTANTE**: 
- O arquivo `.env` está no `.gitignore` e não deve ser commitado
- Nunca compartilhe o arquivo `.env` em repositórios públicos
- Use valores seguros para senhas e secrets em produção

## Variáveis por Serviço

### Keycloak
- `KEYCLOAK_ADMIN`: Usuário administrador
- `KEYCLOAK_ADMIN_PASSWORD`: Senha do administrador
- `KEYCLOAK_URL`: URL do servidor Keycloak
- `KEYCLOAK_REALM`: Nome do realm
- `KEYCLOAK_CLIENT_ID`: ID do cliente
- `KEYCLOAK_CLIENT_SECRET`: Secret do cliente

### Bancos de Dados
- `AUTH_MONGODB_URL`: MongoDB do serviço de autenticação
- `CORE_MONGODB_URL`: MongoDB do serviço de veículos
- `SALES_MONGODB_URL`: MongoDB do serviço de vendas
- `CUSTOMER_MONGODB_URL`: MongoDB do serviço de clientes

### URLs dos Serviços
- `AUTH_SERVICE_URL`: URL do serviço de autenticação
- `CORE_SERVICE_URL`: URL do serviço de veículos
- `CUSTOMER_SERVICE_URL`: URL do serviço de clientes

### Frontend
- `REACT_APP_*`: Variáveis específicas do React
- `CHOKIDAR_USEPOLLING`: Para hot reload em alguns sistemas 