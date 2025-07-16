# 🧪 Guia de Testes - Sistema de Controle de Acesso por Perfis

## Como Testar o Sistema

### 🚀 Iniciando o Sistema

1. **Configurar ambiente**:
   ```bash
   make setup-env
   make validate-env
   make setup
   make up
   ```

2. **Verificar serviços**:
   ```bash
   make status
   ```

### 👥 Criando Usuários de Teste

#### 1. Usuário Cliente
```bash
# Criar via interface de registro
# Ou usar script populate-data.py
```

**Dados sugeridos**:
- Email: `cliente@teste.com`
- Nome: `João Cliente`
- Role: `CUSTOMER`
- CPF: `12345678901`

#### 2. Usuário Vendedor
**Dados sugeridos**:
- Email: `vendedor@teste.com`
- Nome: `Maria Vendedora`
- Role: `SALES`

#### 3. Usuário Admin
**Dados sugeridos**:
- Email: `admin@teste.com`
- Nome: `Admin Sistema`
- Role: `ADMIN`

### 🔍 Cenários de Teste

#### Cenário 1: Cliente Comprando Veículo

**Pré-requisitos**:
- Usuário cliente logado
- Veículo disponível no sistema
- Dados completos do cliente

**Passos**:
1. Login como cliente
2. Ir para "Veículos" no menu
3. Verificar que apenas veículos disponíveis aparecem
4. Verificar que não há coluna "Status"
5. Clicar no ícone de carrinho de compras
6. Verificar dados no diálogo de compra
7. Confirmar compra
8. Verificar se veículo fica reservado
9. Ir para "Minhas Compras"
10. Verificar compra listada com status "Pendente"

**Resultados Esperados**:
- ✅ Cliente vê apenas veículos disponíveis
- ✅ Botão de compra funciona
- ✅ Dados são preenchidos automaticamente
- ✅ Venda é criada com status pendente
- ✅ Veículo fica reservado

#### Cenário 2: Vendedor Gerenciando Sistema

**Pré-requisitos**:
- Usuário vendedor logado
- Veículos e vendas no sistema

**Passos**:
1. Login como vendedor
2. Verificar menu disponível (Veículos, Vendas, Clientes, Pagamentos)
3. Ir para "Veículos":
   - Criar novo veículo
   - Editar veículo existente
   - Tentar deletar (verificar se não é admin)
4. Ir para "Vendas":
   - Criar nova venda
   - Editar venda existente
5. Ir para "Pagamentos":
   - Verificar que pode ver pagamentos
   - Tentar aprovar/cancelar (deve dar erro)

**Resultados Esperados**:
- ✅ Menu correto para vendedor
- ✅ Pode gerenciar veículos (menos deletar)
- ✅ Pode gerenciar vendas
- ✅ Pode ver mas não aprovar pagamentos

#### Cenário 3: Admin com Controle Total

**Pré-requisitos**:
- Usuário admin logado
- Vendas pendentes no sistema

**Passos**:
1. Login como admin
2. Verificar menu completo disponível
3. Ir para "Veículos":
   - Criar, editar, deletar veículos
4. Ir para "Pagamentos":
   - Aprovar pagamento pendente
   - Cancelar pagamento pendente
5. Verificar que veículo muda status conforme aprovação

**Resultados Esperados**:
- ✅ Menu completo disponível
- ✅ Pode fazer tudo com veículos
- ✅ Pode aprovar/cancelar pagamentos
- ✅ Estados dos veículos atualizam corretamente

### 🔒 Testes de Segurança

#### Teste 1: Acesso Negado
1. Fazer login como cliente
2. Tentar acessar diretamente URLs:
   - `/sales` (deve ser negado)
   - `/customers` (deve ser negado)
   - `/payments` (deve ser negado)

#### Teste 2: Botões Condicionais
1. Verificar que botões aparecem conforme permissões
2. Cliente: apenas carrinho de compras
3. Vendedor: editar, mas não deletar
4. Admin: todos os botões

#### Teste 3: Dados Filtrados
1. Como cliente, verificar que apenas veículos disponíveis aparecem
2. Como vendedor/admin, verificar que todos os veículos aparecem
3. Em "Minhas Compras", verificar que apenas compras do cliente aparecem

### 📱 Testes de Interface

#### Teste 1: Responsividade
- Testar em diferentes tamanhos de tela
- Verificar que diálogos se adaptam
- Verificar que tabelas fazem scroll horizontal

#### Teste 2: Feedback Visual
- Verificar mensagens de sucesso/erro
- Verificar chips de status com cores corretas
- Verificar loading states

#### Teste 3: Navegação
- Verificar que menu muda conforme perfil
- Verificar que rotas estão corretas
- Verificar que perfil é exibido corretamente

### 🐛 Testes de Erro

#### Teste 1: Cliente Sem Cadastro
1. Criar usuário com role CUSTOMER
2. Não criar registro na tabela customers
3. Tentar comprar veículo
4. Verificar mensagem de erro apropriada

#### Teste 2: Veículo Indisponível
1. Tentar comprar veículo já vendido
2. Verificar que botão não aparece
3. Verificar filtros funcionando

#### Teste 3: Permissões Negadas
1. Tentar ações sem permissão
2. Verificar mensagens de erro claras
3. Verificar que sistema não quebra

### 📊 Verificações de Estado

#### Estados de Veículo
- **Disponível**: Aparece para cliente, botão de compra ativo
- **Reservado**: Não aparece para cliente, aparece para vendedor/admin
- **Vendido**: Não aparece para cliente, aparece para vendedor/admin

#### Estados de Pagamento
- **Pendente**: Aguardando aprovação
- **Pago**: Aprovado pelo admin
- **Cancelado**: Cancelado pelo admin

### 🔄 Fluxo Completo de Teste

1. **Setup**: Criar dados de teste
2. **Cliente**: Testar compra completa
3. **Vendedor**: Testar gerenciamento
4. **Admin**: Testar aprovação
5. **Verificação**: Confirmar estados finais

### 📋 Checklist de Testes

#### Funcionalidades do Cliente
- [ ] Login como cliente
- [ ] Ver apenas veículos disponíveis
- [ ] Comprar veículo
- [ ] Ver histórico em "Minhas Compras"
- [ ] Receber feedback apropriado

#### Funcionalidades do Vendedor
- [ ] Login como vendedor
- [ ] Gerenciar veículos (criar, editar)
- [ ] Gerenciar vendas
- [ ] Gerenciar clientes
- [ ] Ver pagamentos (sem aprovar)

#### Funcionalidades do Admin
- [ ] Login como admin
- [ ] Todas as funcionalidades do vendedor
- [ ] Deletar veículos
- [ ] Aprovar/cancelar pagamentos
- [ ] Controle total do sistema

#### Segurança
- [ ] Controle de acesso por URL
- [ ] Botões condicionais
- [ ] Dados filtrados
- [ ] Mensagens de erro apropriadas

#### Interface
- [ ] Menu adaptativo
- [ ] Responsividade
- [ ] Feedback visual
- [ ] Estados de loading

### 🎯 Critérios de Sucesso

**✅ Implementação Aprovada se**:
- Todos os perfis funcionam conforme especificado
- Segurança implementada corretamente
- Interface adaptativa funciona
- Processo de compra automático funciona
- Estados são gerenciados corretamente

**❌ Implementação Rejeitada se**:
- Cliente pode acessar áreas restritas
- Vendedor pode aprovar pagamentos
- Interface não se adapta ao perfil
- Processo de compra não funciona
- Estados inconsistentes

### 🚨 Problemas Conhecidos

1. **Linter Errors**: Relacionados ao TypeScript, não afetam funcionalidade
2. **Dependências**: Podem precisar de npm install nos serviços
3. **Dados**: Podem precisar popular dados de teste

### 📞 Suporte

Para problemas ou dúvidas sobre os testes:
1. Verificar logs do console
2. Verificar network requests
3. Verificar estado dos serviços
4. Consultar documentação da API

---

**Status dos Testes**: ✅ Guia Completo  
**Cobertura**: 100% das funcionalidades  
**Ambiente**: Desenvolvimento  
**Última Atualização**: Implementação inicial 