# Проблемы с базой данных

Решение проблем с PostgreSQL и миграциями.

## Проблемы подключения

### Не могу подключиться к БД

**Проблема:** Ошибка подключения к PostgreSQL.

**Решение:**
1. Проверьте, что PostgreSQL запущен:
```bash
docker-compose ps postgres
```

2. Проверьте переменные окружения:
```bash
echo $DB_HOST
echo $DB_USER
echo $DB_PASSWORD
```

3. Попробуйте подключиться вручную:
```bash
docker-compose exec postgres psql -U postgres -d hh_db
```

### Ошибка аутентификации

**Проблема:** `password authentication failed`.

**Решение:**
1. Проверьте пароль в `.env`
2. Пересоздайте пользователя БД:
```bash
docker-compose exec postgres psql -U postgres
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hh_db TO your_user;
```

## Проблемы с миграциями

### Миграции не применяются

**Проблема:** Ошибки при применении миграций.

**Решение:**
1. Проверьте текущую версию:
```bash
docker-compose exec backend alembic current
```

2. Проверьте логи:
```bash
docker-compose logs backend | grep alembic
```

3. Примените миграции вручную:
```bash
docker-compose exec backend alembic upgrade head
```

### Конфликт миграций

**Проблема:** Конфликт при применении миграций.

**Решение:**
1. Сделайте бэкап БД
2. Проверьте историю миграций: `alembic history`
3. Откатите проблемную миграцию: `alembic downgrade -1`
4. Исправьте миграцию и примените заново

## Проблемы с производительностью

### Медленные запросы

**Проблема:** Запросы к БД выполняются медленно.

**Решение:**
1. Проверьте индексы:
```sql
SELECT * FROM pg_indexes WHERE tablename = 'your_table';
```

2. Используйте EXPLAIN для анализа запросов:
```sql
EXPLAIN ANALYZE SELECT * FROM your_table WHERE ...;
```

3. Оптимизируйте запросы (избегайте N+1 проблем)

### Высокое использование диска

**Проблема:** БД занимает много места.

**Решение:**
1. Проверьте размер БД:
```sql
SELECT pg_size_pretty(pg_database_size('hh_db'));
```

2. Очистите старые данные (если нужно)
3. Настройте ротацию логов

## Восстановление данных

### Восстановление из бэкапа

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U postgres hh_db > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U postgres hh_db < backup.sql
```

### Восстановление после сбоя

1. Остановите приложение
2. Восстановите БД из бэкапа
3. Проверьте целостность данных
4. Запустите приложение

## Связанные разделы

- [Deployment: Миграции БД](../deployment/database-migrations.md) — работа с миграциями
- [Troubleshooting: Общие проблемы](common-issues.md) — другие проблемы
