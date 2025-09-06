# 📊 Guia de População de Dados - Sistema FIAP III

Este documento descreve como popular o banco de dados com dados de exemplo para o sistema de vendas de veículos.

## 🚀 Opções de População

### 1. Script Interativo (Recomendado)
```bash
cd backend
./scripts/populate.sh
```

Este script oferece 4 opções:
- **Opção 1**: População básica (dados mínimos)
- **Opção 2**: População abrangente (dados moderados) 
- **Opção 3**: População avançada (dados completos) - **RECOMENDADO**
- **Opção 4**: Apenas criar admin padrão

### 2. Execução Direta dos Scripts

#### População Básica
```bash
cd backend
node scripts/populate-data.js
```

#### População Abrangente
```bash
cd backend
node scripts/populate-comprehensive-data.js
```

#### População Avançada (Recomendada)
```bash
cd backend
node scripts/populate-advanced-data.js
```

## 📈 Detalhes dos Dados Criados

### População Avançada (Recomendada)
- **👥 Usuários**: 6 usuários (1 admin + 3 vendedores + 2 clientes)
- **🚗 Veículos**: 20 veículos de marcas e modelos variados
- **👤 Clientes**: 15 clientes com dados completos
- **💰 Vendas**: 25 vendas com diferentes status e cenários

### Distribuição de Status
- **Veículos**: 60% disponíveis, 25% vendidos, 15% reservados
- **Vendas**: 50% pagas, 30% pendentes, 20% canceladas
- **Métodos de Pagamento**: Distribuição realística entre PIX, cartões, dinheiro e financiamento

## 🔑 Credenciais de Acesso

### Usuários Padrão
| Perfil | Email | Senha | Permissões |
|--------|--------|--------|------------|
| **Admin** | `admin@fiap.com` | `admin123` | Acesso total ao sistema |
| **Vendedor** | `carlos.vendedor@fiap.com` | `vendedor123` | Vendas, veículos, pagamentos |
| **Vendedor** | `ana.vendedora@fiap.com` | `vendedor123` | Vendas, veículos, pagamentos |
| **Cliente** | `cliente.joao@fiap.com` | `cliente123` | Compras, visualização |
| **Cliente** | `cliente.maria@fiap.com` | `cliente123` | Compras, visualização |

## 🎯 Cenários de Teste Incluídos

### Vendas Variadas
- ✅ Vendas pagas com diferentes métodos de pagamento
- ⏳ Vendas pendentes aguardando aprovação
- ❌ Vendas canceladas por diversos motivos
- 💰 Descontos aplicados (0% a 20%)
- 📅 Datas distribuídas nos últimos 6 meses

### Veículos Diversos
- 🏷️ 10 marcas diferentes (Toyota, Honda, VW, Ford, etc.)
- 🎨 9 cores variadas
- 📅 Anos de 2020 a 2024
- 💵 Preços realísticos baseados em marca e ano

### Clientes Completos
- 📧 Emails realísticos
- 📱 Telefones formatados corretamente
- 🆔 CPFs válidos matematicamente
- 🏠 Endereços completos em São Paulo

## ⚙️ Configuração Necessária

### Pré-requisitos
1. **Node.js** instalado (versão 14+)
2. **MongoDB** rodando e acessível
3. **Dependências** instaladas (`npm install`)
4. **Arquivo .env** configurado com string de conexão

### Variáveis de Ambiente
```env
MONGODB_URI=mongodb://localhost:27017/vehiclesales
DEFAULT_ADMIN_EMAIL=admin@fiap.com
DEFAULT_ADMIN_PASSWORD=admin123
```

## 🧹 Limpeza de Dados

⚠️ **ATENÇÃO**: O script de população avançada **limpa todos os dados existentes** antes de criar os novos dados.

Para preservar dados existentes, comente a linha:
```javascript
// await clearExistingData();
```

## 📊 Relatório de População

Após a execução, você verá um relatório detalhado:

```
📈 === RELATÓRIO DETALHADO ===
👥 Usuários: 6
🚗 Veículos: 20 (12 disponíveis, 5 vendidos, 3 reservados)
👤 Clientes: 15
💰 Vendas: 25 (12 pagas, 8 pendentes, 5 canceladas)
💵 Receita Total: R$ 1.234.567
💳 Métodos de Pagamento:
   PIX: 8 vendas
   CARTAO_CREDITO: 6 vendas
   FINANCIAMENTO: 5 vendas
   ...
```

## 🔍 Validações Incluídas

- ✅ CPFs matematicamente válidos
- ✅ Emails com formato correto
- ✅ Telefones com DDD brasileiro
- ✅ Preços sempre positivos
- ✅ Datas cronologicamente corretas
- ✅ Status de veículos consistentes com vendas

## 📝 Notas Importantes

1. **Senhas Padrão**: Altere as senhas em produção
2. **Dados Fictícios**: Todos os dados são fictícios para teste
3. **CPFs Válidos**: CPFs são válidos matematicamente mas fictícios
4. **Backup**: Faça backup antes de executar em produção

## 🆘 Solução de Problemas

### Erro de Conexão
```bash
# Verificar se MongoDB está rodando
sudo systemctl status mongod

# Iniciar MongoDB se necessário
sudo systemctl start mongod
```

### Erro de Dependências
```bash
# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install
```

### Erro de Permissão
```bash
# Dar permissão ao script
chmod +x scripts/populate.sh
```

---

**💡 Dica**: Use a população avançada para ter um ambiente completo de testes com cenários realísticos!
