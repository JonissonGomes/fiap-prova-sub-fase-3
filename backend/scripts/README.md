# 📊 Scripts de População de Dados - FIAP III

Este diretório contém scripts para popular o banco de dados com dados de exemplo para demonstração e testes.

## 🚀 Execução Rápida

```bash
# Executar script interativo (RECOMENDADO)
./populate.sh

# Ou executar diretamente a população avançada
node populate-advanced-data.js
```

## 📁 Arquivos Disponíveis

### Scripts de População

| Script | Descrição | Dados Criados |
|--------|-----------|---------------|
| `populate-data.js` | População básica original | 4 veículos, 2 clientes |
| `populate-comprehensive-data.js` | População abrangente | 10 veículos, 10 clientes, 10 vendas |
| `populate-advanced-data.js` | **População avançada** ⭐ | 20 veículos, 15 clientes, 25 vendas |
| `populate.sh` | Script interativo | Escolha entre as opções acima |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | Este arquivo |
| `../POPULATE_DATA_GUIDE.md` | Guia detalhado completo |

## 🎯 População Avançada (Recomendada)

O script `populate-advanced-data.js` cria um ambiente completo de testes:

### 👥 Usuários (6 total)
- **1 Administrador**: Acesso total ao sistema
- **3 Vendedores**: Podem gerenciar vendas e veículos
- **2 Clientes**: Podem realizar compras

### 🚗 Veículos (20 total)
- **10 marcas diferentes**: Toyota, Honda, VW, Ford, Chevrolet, Nissan, Hyundai, Renault, Peugeot, Fiat
- **Modelos variados**: 4 modelos por marca
- **Anos**: 2020-2024
- **Cores**: 9 opções diferentes
- **Preços**: Calculados realisticamente baseados em marca e ano

### 👤 Clientes (15 total)
- **CPFs válidos**: Gerados matematicamente corretos
- **Emails realísticos**: Baseados nos nomes
- **Telefones**: Com DDDs brasileiros válidos
- **Endereços completos**: Localizados em São Paulo

### 💰 Vendas (25 total)
- **Status distribuído**: 50% pagas, 30% pendentes, 20% canceladas
- **5 métodos de pagamento**: PIX, cartões, dinheiro, financiamento
- **Descontos**: 0% a 20% aplicados aleatoriamente
- **Datas**: Distribuídas nos últimos 6 meses
- **Notas detalhadas**: Explicam cada transação

## 📊 Dados Gerados

### Estatísticas Típicas
```
👥 Usuários: 7 (incluindo admin padrão)
🚗 Veículos: 20 (variação de disponíveis/vendidos/reservados)
👤 Clientes: 15
💰 Vendas: 25
💵 Receita Total: R$ 1.200.000+ (varia conforme descontos)
```

### Métodos de Pagamento
- **PIX**: ~20% das vendas
- **Cartão de Crédito**: ~20% das vendas
- **Cartão de Débito**: ~25% das vendas
- **Dinheiro**: ~25% das vendas
- **Financiamento**: ~10% das vendas

## 🔑 Credenciais Padrão

| Perfil | Email | Senha | Funcionalidades |
|--------|--------|--------|-----------------|
| **Admin** | `admin@fiap.com` | `admin123` | • Dashboard completo<br>• Gerenciar tudo<br>• Relatórios avançados |
| **Vendedor 1** | `carlos.vendedor@fiap.com` | `vendedor123` | • Gerenciar vendas<br>• Gerenciar veículos<br>• Aprovar pagamentos |
| **Vendedor 2** | `ana.vendedora@fiap.com` | `vendedor123` | • Gerenciar vendas<br>• Gerenciar veículos<br>• Aprovar pagamentos |
| **Cliente 1** | `cliente.joao@fiap.com` | `cliente123` | • Visualizar veículos<br>• Realizar compras<br>• Acompanhar pedidos |
| **Cliente 2** | `cliente.maria@fiap.com` | `cliente123` | • Visualizar veículos<br>• Realizar compras<br>• Acompanhar pedidos |

## 🛠️ Pré-requisitos

### Sistema
- **Node.js** 14+ instalado
- **MongoDB** rodando
- **Dependências** instaladas (`npm install`)

### Configuração
```env
MONGODB_URI=mongodb://localhost:27017/unified_vehicle_db
DEFAULT_ADMIN_EMAIL=admin@fiap.com
DEFAULT_ADMIN_PASSWORD=admin123
```

## 🚨 Avisos Importantes

### ⚠️ Limpeza de Dados
O script avançado **REMOVE TODOS OS DADOS EXISTENTES** antes de criar novos dados.

Para preservar dados, comente esta linha:
```javascript
// await clearExistingData();
```

### 🔒 Segurança
- Senhas padrão são **apenas para desenvolvimento**
- **ALTERE AS SENHAS** em produção
- CPFs são **matematicamente válidos** mas **fictícios**

## 🎪 Cenários de Teste Incluídos

### Vendas Realísticas
- ✅ **Vendas Pagas**: Com data de pagamento
- ⏳ **Vendas Pendentes**: Aguardando aprovação
- ❌ **Vendas Canceladas**: Com motivos específicos
- 💰 **Descontos Variados**: 0% a 20%
- 📅 **Histórico**: Últimos 6 meses

### Status de Veículos
- 🟢 **Disponíveis**: Prontos para venda
- 🔴 **Vendidos**: Já foram comprados
- 🟡 **Reservados**: Em processo de venda

### Métodos de Pagamento
- 💳 **Cartões**: Crédito e débito
- 💰 **Dinheiro**: À vista
- 📱 **PIX**: Transferência instantânea
- 🏦 **Financiamento**: Aprovado pelo banco

## 🐛 Solução de Problemas

### MongoDB não conecta
```bash
# Verificar se está rodando
sudo systemctl status mongod

# Iniciar se necessário
sudo systemctl start mongod
```

### Erro de permissão no script
```bash
chmod +x populate.sh
```

### Dependências ausentes
```bash
npm install
```

### Erro de duplicação de dados
Os scripts verificam dados existentes e podem ser executados múltiplas vezes.

## 📈 Exemplo de Uso

```bash
# 1. Navegar para a pasta backend
cd backend

# 2. Executar script interativo
./scripts/populate.sh

# 3. Escolher opção 3 (População avançada)

# 4. Aguardar conclusão e ver relatório

# 5. Iniciar servidor
npm start

# 6. Acessar sistema com credenciais fornecidas
```

## 🎯 Próximos Passos

Após executar a população:

1. **Iniciar o servidor backend**: `npm start`
2. **Iniciar o frontend**: Navegar para `/frontend` e executar `npm start`
3. **Fazer login** com as credenciais fornecidas
4. **Explorar** as funcionalidades com dados realísticos
5. **Testar** diferentes perfis de usuário

---

💡 **Dica**: Use sempre a população avançada para ter um ambiente completo de demonstração!
