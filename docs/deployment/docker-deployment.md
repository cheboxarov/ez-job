# Деплой через Docker

Пошаговая инструкция по развертыванию проекта через Docker.

## Структура docker-compose.yml

Проект использует Docker Compose для оркестрации контейнеров:

- **postgres** — база данных PostgreSQL
- **backend** — FastAPI приложение
- **frontend** — React приложение (nginx)

## Сборка образов

```bash
# Сборка всех образов
docker-compose build

# Сборка конкретного сервиса
docker-compose build backend
docker-compose build frontend
```

## Запуск контейнеров

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск с логами
docker-compose up

# Запуск конкретного сервиса
docker-compose up -d postgres
docker-compose up -d backend
docker-compose up -d frontend
```

## Проверка работоспособности

### Проверка статуса контейнеров

```bash
docker-compose ps
```

Все сервисы должны быть в статусе `Up`.

### Проверка логов

```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Логи в реальном времени
docker-compose logs -f backend
```

### Проверка health checks

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# PostgreSQL
docker-compose exec postgres pg_isready -U postgres
```

## Применение миграций

Миграции применяются автоматически при запуске backend контейнера.

Для ручного применения:

```bash
docker-compose exec backend alembic upgrade head
```

## Обновление приложения

### 1. Остановка контейнеров

```bash
docker-compose down
```

### 2. Обновление кода

```bash
git pull origin main
```

### 3. Пересборка образов

```bash
docker-compose build
```

### 4. Запуск с новой версией

```bash
docker-compose up -d
```

### 5. Применение миграций (если есть новые)

```bash
docker-compose exec backend alembic upgrade head
```

## Откат изменений

### Откат к предыдущей версии

```bash
# Остановка
docker-compose down

# Откат кода
git checkout <previous-commit>

# Пересборка и запуск
docker-compose build
docker-compose up -d
```

### Откат миграций БД

```bash
# Откат на одну миграцию
docker-compose exec backend alembic downgrade -1

# Откат к конкретной версии
docker-compose exec backend alembic downgrade <revision>
```

## Управление данными

### Резервное копирование БД

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U postgres hh_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Или через docker
docker-compose exec -T postgres pg_dump -U postgres hh_db > backup.sql
```

### Восстановление из бэкапа

```bash
# Восстановление
docker-compose exec -T postgres psql -U postgres hh_db < backup.sql
```

### Очистка данных

```bash
# Остановка и удаление контейнеров с данными
docker-compose down -v

# ВНИМАНИЕ: Это удалит все данные!
```

## Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Использование диска
docker system df
```

## Проблемы?

См. [Troubleshooting деплоя](troubleshooting-deployment.md)
