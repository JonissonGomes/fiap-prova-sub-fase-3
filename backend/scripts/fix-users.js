require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const User = require('../src/models/User');
const { logger } = require('../src/utils/logger');

async function fixUsers() {
  try {
    await connectDatabase();
    
    console.log('\n🔍 === DIAGNÓSTICO E CORREÇÃO DE USUÁRIOS ===');
    
    // 1. Verificar todos os usuários existentes
    const allUsers = await User.find({});
    console.log(`\n📊 Total de usuários encontrados: ${allUsers.length}`);
    
    if (allUsers.length > 0) {
      console.log('\n👥 Usuários existentes:');
      allUsers.forEach((user, index) => {
        console.log(`  ${index + 1}. ${user.email} (${user.role}) - ${user.status}`);
      });
    }
    
    // 2. Verificar se os usuários FIAP existem
    const fiapUsers = [
      { email: 'admin@fiap.com', name: 'Administrador FIAP', role: 'ADMIN', password: 'admin123' },
      { email: 'carlos.vendedor@fiap.com', name: 'Carlos Silva Vendedor', role: 'SALES', password: 'vendedor123' },
      { email: 'ana.vendedora@fiap.com', name: 'Ana Costa Vendedora', role: 'SALES', password: 'vendedor123' },
      { email: 'pedro.vendedor@fiap.com', name: 'Pedro Santos Vendedor', role: 'SALES', password: 'vendedor123' },
      { email: 'cliente.joao@fiap.com', name: 'João Paulo Cliente', role: 'CUSTOMER', password: 'cliente123' },
      { email: 'cliente.maria@fiap.com', name: 'Maria Silva Cliente', role: 'CUSTOMER', password: 'cliente123' }
    ];
    
    console.log('\n🔧 === VERIFICANDO E CRIANDO USUÁRIOS FIAP ===');
    
    let usersCreated = 0;
    let usersUpdated = 0;
    
    for (const userData of fiapUsers) {
      const existingUser = await User.findOne({ email: userData.email });
      
      if (existingUser) {
        console.log(`✅ ${userData.email} já existe`);
        
        // Verificar se precisa atualizar dados
        let needsUpdate = false;
        if (existingUser.name !== userData.name) {
          existingUser.name = userData.name;
          needsUpdate = true;
        }
        if (existingUser.role !== userData.role) {
          existingUser.role = userData.role;
          needsUpdate = true;
        }
        if (existingUser.status !== 'ACTIVE') {
          existingUser.status = 'ACTIVE';
          needsUpdate = true;
        }
        
        if (needsUpdate) {
          await existingUser.save();
          console.log(`  🔄 Atualizado: ${userData.email}`);
          usersUpdated++;
        }
      } else {
        console.log(`➕ Criando: ${userData.email}`);
        
        const newUser = new User({
          email: userData.email,
          name: userData.name,
          password: userData.password,
          role: userData.role,
          status: 'ACTIVE'
        });
        
        await newUser.save();
        console.log(`  ✅ Criado: ${userData.email}`);
        usersCreated++;
      }
    }
    
    // 3. Verificar total final
    const finalCount = await User.countDocuments();
    console.log(`\n📊 === RESULTADO FINAL ===`);
    console.log(`👥 Total de usuários: ${finalCount}`);
    console.log(`➕ Usuários criados: ${usersCreated}`);
    console.log(`🔄 Usuários atualizados: ${usersUpdated}`);
    
    // 4. Listar todos os usuários finais
    const finalUsers = await User.find({}, 'email name role status').sort({ email: 1 });
    console.log('\n📋 Lista final de usuários:');
    finalUsers.forEach((user, index) => {
      console.log(`  ${index + 1}. ${user.email}`);
      console.log(`     Nome: ${user.name}`);
      console.log(`     Role: ${user.role}`);
      console.log(`     Status: ${user.status}`);
      console.log(`     ─────────────────────────`);
    });
    
    // 5. Testar login de cada usuário FIAP
    console.log('\n🔐 === TESTE DE LOGIN ===');
    for (const userData of fiapUsers) {
      const user = await User.findOne({ email: userData.email });
      if (user) {
        const isValid = await user.comparePassword(userData.password);
        console.log(`${userData.email}: ${isValid ? '✅ LOGIN OK' : '❌ LOGIN FALHOU'}`);
      }
    }
    
    console.log('\n🎉 Correção de usuários concluída!');
    
  } catch (error) {
    console.error('❌ Erro ao corrigir usuários:', error.message);
    logger.error('Erro ao corrigir usuários:', error);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  fixUsers();
}

module.exports = fixUsers;
