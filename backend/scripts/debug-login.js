require('dotenv').config({ path: './config.env' });
const express = require('express');
const mongoose = require('mongoose');
const { connectDatabase } = require('../src/config/database');
const User = require('../src/models/User');
const { body, validationResult } = require('express-validator');

async function debugLogin() {
  try {
    await connectDatabase();
    
    // Simular exatamente o que a API faz
    const testData = {
      email: 'admin@fiap.com',
      password: 'admin123'
    };
    
    console.log('\n🔍 === DEBUG DO PROCESSO DE LOGIN ===');
    console.log(`📧 Email testado: ${testData.email}`);
    console.log(`🔑 Senha testada: ${testData.password}`);
    
    // 1. Normalizar email como a validação faz
    const normalizedEmail = testData.email.toLowerCase().trim();
    console.log(`📧 Email normalizado: ${normalizedEmail}`);
    
    // 2. Buscar usuário exatamente como a API faz
    console.log('\n🔍 Buscando usuário...');
    const user = await User.findOne({ email: normalizedEmail });
    
    if (!user) {
      console.log('❌ Usuário não encontrado na busca normalizada');
      
      // Tentar busca sem normalização
      const userDirect = await User.findOne({ email: testData.email });
      if (userDirect) {
        console.log('✅ Usuário encontrado na busca direta');
        console.log(`📧 Email no banco: "${userDirect.email}"`);
        console.log(`📧 Email procurado: "${normalizedEmail}"`);
        console.log(`🔍 São iguais? ${userDirect.email === normalizedEmail}`);
      }
      return;
    }
    
    console.log(`✅ Usuário encontrado: ${user.name}`);
    console.log(`📧 Email no banco: "${user.email}"`);
    console.log(`📊 Status: ${user.status}`);
    console.log(`🔑 Role: ${user.role}`);
    
    // 3. Verificar status
    if (user.status !== 'ACTIVE') {
      console.log(`❌ Usuário não ativo: ${user.status}`);
      return;
    }
    
    console.log('✅ Status ativo');
    
    // 4. Testar senha
    console.log('\n🔒 Testando senha...');
    const isValidPassword = await user.comparePassword(testData.password);
    console.log(`🔓 Senha válida: ${isValidPassword}`);
    
    if (!isValidPassword) {
      console.log('❌ Senha inválida');
      
      // Debug do hash
      console.log(`🔍 Hash no banco: ${user.password.substring(0, 30)}...`);
      
      // Testar manualmente
      const bcrypt = require('bcryptjs');
      const manualTest = await bcrypt.compare(testData.password, user.password);
      console.log(`🧪 Teste manual: ${manualTest}`);
      
      return;
    }
    
    console.log('✅ Login seria bem-sucedido!');
    
    // 5. Simular validação do express-validator
    console.log('\n🔍 Testando validação do express-validator...');
    
    // Criar um mock request
    const mockReq = {
      body: testData
    };
    
    // Aplicar validações
    const loginValidation = [
      body('email').isEmail().normalizeEmail().withMessage('Email inválido'),
      body('password').notEmpty().withMessage('Senha é obrigatória')
    ];
    
    // Simular validação
    let validationErrors = [];
    
    // Validar email
    if (!testData.email.includes('@')) {
      validationErrors.push('Email inválido');
    }
    
    // Validar senha
    if (!testData.password || testData.password.trim() === '') {
      validationErrors.push('Senha é obrigatória');
    }
    
    if (validationErrors.length > 0) {
      console.log('❌ Erros de validação:', validationErrors);
    } else {
      console.log('✅ Validação passou');
    }
    
  } catch (error) {
    console.error('❌ Erro no debug:', error.message);
    console.error('Stack:', error.stack);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}

if (require.main === module) {
  debugLogin();
}

module.exports = debugLogin;
