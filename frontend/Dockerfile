# Этап сборки
FROM node:20-alpine AS builder

WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm install --legacy-peer-deps

# Копирование исходного кода
COPY . .

# Сборка приложения (vite сам проверяет типы через плагин)
RUN npx vite build

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
