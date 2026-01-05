# Миграции базы данных

Работа с миграциями Alembic в продакшене.

## Применение миграций

### Автоматическое применение

Миграции применяются автоматически при запуске backend контейнера:

```bash
docker-compose up -d backend
```

В логах должно быть:
```
INFO  [alembic.runtime.migration] Running upgrade ... -> ..., description
```

### Ручное применение

```bash
# Применение всех миграций
docker-compose exec backend alembic upgrade head

# Или локально
cd backend
alembic upgrade head
```

## Проверка текущей версии

```bash
docker-compose exec backend alembic current
```

## Создание новых миграций

### Автогенерация

```bash
# Создание миграции на основе изменений моделей
docker-compose exec backend alembic revision --autogenerate -m "description"

# Или локально
cd backend
alembic revision --autogenerate -m "description"
```

### Ручное создание

```bash
docker-compose exec backend alembic revision -m "description"
```

## Откат миграций

```bash
# Откат на одну миграцию
docker-compose exec backend alembic downgrade -1

# Откат к конкретной версии
docker-compose exec backend alembic downgrade <revision>

# Откат всех миграций (ОПАСНО!)
docker-compose exec backend alembic downgrade base
```

## История миграций

```bash
# Просмотр истории
docker-compose exec backend alembic history

# Просмотр текущей версии
docker-compose exec backend alembic current
```

## Резервное копирование перед миграциями

**ВАЖНО:** Всегда делайте бэкап перед применением миграций в продакшене!

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U postgres hh_db > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
```

## Связанные разделы

- [Деплой через Docker](docker-deployment.md) — общий деплой
- [Troubleshooting: БД](../troubleshooting/database-issues.md) — проблемы с миграциями
