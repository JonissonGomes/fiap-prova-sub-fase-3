require('dotenv').config({ path: './config.env' });

console.log('\n🔍 === VERIFICAÇÃO DA CONFIGURAÇÃO DA API ===');
console.log('\n📋 Variáveis de ambiente:');
console.log(`MONGODB_URL: ${process.env.MONGODB_URL || 'NÃO DEFINIDA'}`);
console.log(`MONGODB_DB_NAME: ${process.env.MONGODB_DB_NAME || 'NÃO DEFINIDA'}`);
console.log(`NODE_ENV: ${process.env.NODE_ENV || 'NÃO DEFINIDA'}`);
console.log(`PORT: ${process.env.PORT || 'NÃO DEFINIDA'}`);

// Simular o que a API faz
const mongoUrl = process.env.MONGODB_URL || 'mongodb://localhost:27017';
const dbName = process.env.MONGODB_DB_NAME || 'unified_vehicle_db';
const connectionString = `${mongoUrl}/${dbName}`;

console.log('\n🔗 String de conexão que seria usada:');
console.log(`${connectionString}`);

console.log('\n📁 Arquivo config.env existe?');
const fs = require('fs');
const configExists = fs.existsSync('./config.env');
console.log(`${configExists ? '✅' : '❌'} config.env: ${configExists}`);

if (configExists) {
  console.log('\n📄 Conteúdo do config.env:');
  const configContent = fs.readFileSync('./config.env', 'utf8');
  const lines = configContent.split('\n').filter(line => 
    line.trim() && !line.startsWith('#') && line.includes('MONGODB')
  );
  lines.forEach(line => console.log(`  ${line}`));
}

console.log('\n🎯 Para testar a conexão da API:');
console.log('  curl -s http://localhost:3002/vehicles | jq . | head -10');

process.exit(0);
