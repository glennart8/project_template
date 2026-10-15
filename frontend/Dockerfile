# Steg 1: bygg frontend till färdiga filer.
FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Steg 2: Caddy serverar filerna och skickar /api vidare till backend.
# Det är den enda containern med en öppen port.
FROM caddy:2.11-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv

EXPOSE 80
