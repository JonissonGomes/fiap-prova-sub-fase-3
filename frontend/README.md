# Sistema de Vendas de Veículos da FIAP

Frontend do sistema de gerenciamento de veículos, vendas e pagamentos.

## Visão Geral
Interface web para gerenciamento de veículos e vendas, construída com React e Material-UI.

## Funcionalidades
- Cadastro e gerenciamento de veículos
- Cadastro e acompanhamento de vendas
- Controle de status de veículos e vendas
- Dashboard com informações gerais

## Fluxo de Venda
1. Selecione um veículo disponível
2. Preencha os dados do comprador e pagamento
3. Ao criar a venda:
   - O veículo é automaticamente marcado como RESERVADO
   - A venda é criada com status PENDENTE
4. Após confirmação do pagamento:
   - O veículo é marcado como VENDIDO
   - A venda é atualizada para status PAGO
5. Se a venda for cancelada:
   - O veículo volta para DISPONÍVEL
   - A venda é atualizada para status CANCELADA

## Tecnologias Utilizadas

- React
- TypeScript
- Material-UI
- React Router
- Axios

## Pré-requisitos

- Node.js (versão 14 ou superior)
- npm (gerenciador de pacotes do Node.js)

## Instalação

1. Clone o repositório:
```bash
git clone
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VEHICLES_SERVICE_URL=http://localhost:8001
REACT_APP_SALES_SERVICE_URL=http://localhost:8002
REACT_APP_PAYMENTS_SERVICE_URL=http://localhost:8003
```

## Execução

1. Inicie o servidor de desenvolvimento:
```bash
npm start
```

2. Acesse a aplicação no navegador:
```
http://localhost:3000
```

## Scripts Disponíveis

- `npm start`: Inicia o servidor de desenvolvimento
- `npm test`: Executa os testes
- `npm run build`: Cria a versão de produção
- `npm run lint`: Executa o linter
- `npm run format`: Formata o código

## Arquitetura de Pastas

```
frontend/
├── public/                    # Arquivos estáticos públicos
│   ├── index.html            # Template HTML principal
│   ├── favicon.ico           # Ícone do site
│   └── manifest.json         # Configuração PWA
│
├── src/                      # Código fonte da aplicação
│   ├── assets/              # Recursos estáticos
│   │   ├── images/         # Imagens
│   │   └── styles/         # Estilos globais
│   │
│   ├── components/          # Componentes reutilizáveis
│   │   ├── common/         # Componentes comuns
│   │   │   ├── Button/     # Botões personalizados
│   │   │   ├── Card/       # Cards reutilizáveis
│   │   │   └── Table/      # Tabelas personalizadas
│   │   │
│   │   ├── layout/         # Componentes de layout
│   │   │   ├── Header/     # Cabeçalho
│   │   │   ├── Sidebar/    # Menu lateral
│   │   │   └── Footer/     # Rodapé
│   │   │
│   │   └── forms/          # Componentes de formulário
│   │       ├── Input/      # Campos de entrada
│   │       ├── Select/     # Seletores
│   │       └── DatePicker/ # Seletores de data
│   │
│   ├── pages/              # Páginas da aplicação
│   │   ├── Dashboard/      # Página inicial
│   │   ├── Vehicles/       # Gerenciamento de veículos
│   │   ├── Sales/          # Gerenciamento de vendas
│   │   └── Reports/        # Relatórios
│   │
│   ├── services/           # Serviços de API
│   │   ├── api.ts         # Configuração do Axios
│   │   ├── vehicle.ts     # Serviço de veículos
│   │   └── sale.ts        # Serviço de vendas
│   │
│   ├── types/             # Definições de tipos
│   │   ├── vehicle.ts     # Tipos de veículos
│   │   └── sale.ts        # Tipos de vendas
│   │
│   ├── utils/             # Funções utilitárias
│   │   ├── formatters.ts  # Funções de formatação
│   │   └── validators.ts  # Funções de validação
│   │
│   ├── hooks/             # Hooks personalizados
│   │   ├── useAuth.ts     # Hook de autenticação
│   │   └── useForm.ts     # Hook de formulário
│   │
│   ├── context/           # Contextos React
│   │   ├── AuthContext.ts # Contexto de autenticação
│   │   └── ThemeContext.ts # Contexto de tema
│   │
│   ├── routes/            # Configuração de rotas
│   │   └── index.tsx      # Definição das rotas
│   │
│   ├── App.tsx            # Componente principal
│   └── index.tsx          # Ponto de entrada
│
├── tests/                 # Testes automatizados
│   ├── unit/             # Testes unitários
│   ├── integration/      # Testes de integração
│   └── e2e/             # Testes end-to-end
│
├── .env                  # Variáveis de ambiente
├── .eslintrc.js         # Configuração do ESLint
├── .prettierrc          # Configuração do Prettier
├── tsconfig.json        # Configuração do TypeScript
├── package.json         # Dependências e scripts
└── README.md            # Documentação
```

## Contribuição

1. Crie uma branch para sua feature:
```bash
git checkout -b feature/nova-feature
```

2. Faça commit das suas alterações:
```bash
git commit -m "feat: adiciona nova feature"
```

3. Envie para o repositório:
```bash
git push origin feature/nova-feature
```

4. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT.

## Comandos de Execução

### Desenvolvimento
```bash
# Instalar dependências
npm install
# ou
yarn install

# Iniciar o servidor de desenvolvimento
npm start
# ou
yarn start

# Construir para produção
npm run build
# ou
yarn build
```

### Docker
```bash
# Construir a imagem
docker build -t frontend .

# Executar o container
docker run -p 3000:3000 frontend

# Executar com variáveis de ambiente
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  -e REACT_APP_SALES_API_URL=http://localhost:8001 \
  frontend
```

### Docker Compose
```bash
# Iniciar o frontend com os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar os serviços
docker-compose down
```

### Testes
```bash
# Executar todos os testes
npm test
# ou
yarn test

# Executar testes com cobertura
npm run test:coverage
# ou
yarn test:coverage

# Executar testes em modo watch
npm run test:watch
# ou
yarn test:watch
```

### Qualidade de Código
```bash
# Executar linter
npm run lint
# ou
yarn lint

# Verificar tipos
npm run type-check
# ou
yarn type-check

# Formatar código
npm run format
# ou
yarn format
``` 