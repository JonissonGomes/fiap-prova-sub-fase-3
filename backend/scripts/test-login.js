require('dotenv').config({ path: './config.env' });
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const User = require('../src/models/User');
const bcrypt = require('bcryptjs');

async function testLogin() {
  try {
    await connectDatabase();
    
    const testCredentials = [
      { email: 'admin@fiap.com', password: 'admin123' },
      { email: 'carlos.vendedor@fiap.com', password: 'vendedor123' },
      { email: 'cliente.joao@fiap.com', password: 'cliente123' }
    ];
    
    console.log('\n🔐 === TESTE DE LOGIN ===');
    
    for (const credentials of testCredentials) {
      console.log(`\nTestando: ${credentials.email}`);
      
      // Buscar usuário
      const user = await User.findOne({ email: credentials.email });
      
      if (!user) {
        console.log('❌ Usuário não encontrado');
        continue;
      }
      
      console.log(`✅ Usuário encontrado: ${user.name}`);
      console.log(`📊 Status: ${user.status}`);
      console.log(`🔑 Role: ${user.role}`);
      
      // Testar senha
      const isValidPassword = await user.comparePassword(credentials.password);
      
      if (isValidPassword) {
        console.log('🔓 Senha VÁLIDA');
      } else {
        console.log('🔒 Senha INVÁLIDA');
        
        // Testar manualmente
        const manualTest = await bcrypt.compare(credentials.password, user.password);
        console.log(`🧪 Teste manual bcrypt: ${manualTest ? 'VÁLIDA' : 'INVÁLIDA'}`);
        
        // Verificar se a senha não foi hashada corretamente
        console.log(`🔍 Hash da senha: ${user.password.substring(0, 20)}...`);
      }
      
      console.log('─'.repeat(50));
    }
    
  } catch (error) {
    console.error('❌ Erro no teste:', error.message);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  testLogin();
}

module.exports = testLogin;
