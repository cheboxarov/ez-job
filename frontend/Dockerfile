# Этап сборки
FROM node:20-alpine AS builder

WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm install --legacy-peer-deps

# Копирование конфигурационных файлов
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig*.json ./
COPY package*.json ./

# Копирование исходного кода
COPY src ./src
COPY public ./public

# Проверка наличия index.html
RUN test -f /app/index.html || (echo "index.html not found!" && ls -la /app && exit 1)

# Сборка приложения
RUN npm run build

# Этап production
FROM nginx:alpine

# Копирование собранных файлов из builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Порт для nginx
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]
