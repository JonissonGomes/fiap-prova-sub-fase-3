# Dockerfile otimizado para Render
FROM node:18-alpine

# Instalar dumb-init para melhor gerenciamento de processos
RUN apk add --no-cache dumb-init

# Atualizar npm para versão mais recente e configurar
RUN npm install -g npm@10.2.4 && \
    npm config set fund false && \
    npm config set audit false

# Criar usuário não-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json .npmrc ./

# Instalar dependências de produção com configurações otimizadas
RUN npm ci --omit=dev --no-audit --no-fund && \
    npm cache clean --force

# Copiar código da aplicação
COPY src ./src
COPY scripts ./scripts

# Alterar proprietário dos arquivos
RUN chown -R nodejs:nodejs /app

# Mudar para usuário não-root
USER nodejs

# Expor porta (Render usa a variável PORT)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3002) + '/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })" || exit 1

# Usar dumb-init para melhor gerenciamento de sinais
ENTRYPOINT ["dumb-init", "--"]

# Comando de inicialização
CMD ["npm", "start"]
