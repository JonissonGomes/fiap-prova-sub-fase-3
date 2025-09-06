require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const User = require('../src/models/User');
const bcrypt = require('bcryptjs');

async function checkUsers() {
  try {
    await connectDatabase();
    
    const users = await User.find({}, 'email name role status password');
    
    console.log('\n👥 === USUÁRIOS NO BANCO DE DADOS ===');
    console.log(`Total de usuários: ${users.length}`);
    console.log('');
    
    for (const user of users) {
      console.log(`📧 Email: ${user.email}`);
      console.log(`👤 Nome: ${user.name}`);
      console.log(`🔑 Role: ${user.role}`);
      console.log(`📊 Status: ${user.status}`);
      console.log(`🔒 Hash da senha: ${user.password ? 'Presente' : 'AUSENTE'}`);
      
      // Testar senha padrão
      if (user.password) {
        const senhas = ['admin123', 'vendedor123', 'cliente123'];
        let senhaCorreta = null;
        
        for (const senha of senhas) {
          const isValid = await bcrypt.compare(senha, user.password);
          if (isValid) {
            senhaCorreta = senha;
            break;
          }
        }
        
        if (senhaCorreta) {
          console.log(`✅ Senha testada: ${senhaCorreta} - VÁLIDA`);
        } else {
          console.log(`❌ Nenhuma senha padrão válida encontrada`);
        }
      }
      
      console.log('─'.repeat(50));
    }
    
    console.log('\n🔑 === CREDENCIAIS PARA TESTE ===');
    console.log('👑 Admin: admin@fiap.com / admin123');
    console.log('💼 Vendedor: carlos.vendedor@fiap.com / vendedor123');
    console.log('💼 Vendedor: ana.vendedora@fiap.com / vendedor123');
    console.log('👤 Cliente: cliente.joao@fiap.com / cliente123');
    console.log('👤 Cliente: cliente.maria@fiap.com / cliente123');
    console.log('');
    
  } catch (error) {
    console.error('❌ Erro ao verificar usuários:', error.message);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  checkUsers();
}

module.exports = checkUsers;
