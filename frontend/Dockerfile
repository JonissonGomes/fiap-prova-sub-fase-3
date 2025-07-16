FROM node:18-alpine as builder

WORKDIR /app

# Instalar dependências
COPY package*.json ./
RUN npm install --only=production

# Copiar código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Servidor nginx para produção
FROM nginx:alpine

# Copiar build para nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Configuração nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Expor porta
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 