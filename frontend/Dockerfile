# ── Stage 1: Build da SPA Nuxt ───────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copia package files primeiro para cachear camada de dependências
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copia todo o código-fonte
COPY . .

# A URL da API será substituída em runtime pelo Nginx (proxy reverso).
# O valor em build-time aponta para o proxy interno do Nginx.
ENV NUXT_PUBLIC_API_BASE=/__api__

RUN npm run build

# ── Stage 2: Nginx para servir a SPA + proxy reverso para a API ──────────────
FROM nginx:1.25-alpine

# Remove config padrão
RUN rm /etc/nginx/conf.d/default.conf

# Config customizada: serve a SPA + faz proxy /api -> backend
COPY nginx.conf /etc/nginx/conf.d/samba.conf

# Copia os arquivos estáticos buildados
COPY --from=builder /app/.output/public /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
