# Troubleshooting деплоя

Решение проблем при развертывании проекта.

## Частые проблемы

### Контейнеры не запускаются

**Проблема:** Контейнеры падают сразу после запуска.

**Решение:**
1. Проверьте логи: `docker-compose logs`
2. Проверьте переменные окружения: `docker-compose config`
3. Убедитесь, что порты не заняты: `netstat -tulpn | grep :8000`

### Ошибки подключения к БД

**Проблема:** Backend не может подключиться к PostgreSQL.

**Решение:**
1. Проверьте, что postgres контейнер запущен: `docker-compose ps`
2. Проверьте переменные окружения БД в `.env`
3. Проверьте логи postgres: `docker-compose logs postgres`
4. Попробуйте подключиться вручную: `docker-compose exec postgres psql -U postgres`

### Ошибки миграций

**Проблема:** Миграции не применяются или падают с ошибкой.

**Решение:**
1. Проверьте текущую версию: `docker-compose exec backend alembic current`
2. Проверьте логи: `docker-compose logs backend | grep alembic`
3. Сделайте бэкап перед откатом: `docker-compose exec postgres pg_dump -U postgres hh_db > backup.sql`
4. Откатите миграцию: `docker-compose exec backend alembic downgrade -1`

### Проблемы с nginx

**Проблема:** Frontend не доступен или возвращает ошибки.

**Решение:**
1. Проверьте конфигурацию nginx: `docker-compose exec frontend nginx -t`
2. Проверьте логи: `docker-compose logs frontend`
3. Убедитесь, что backend доступен: `curl http://backend:8000/health`

## Логи для диагностики

### Backend логи

```bash
docker-compose logs backend | tail -100
```

### Frontend логи

```bash
docker-compose logs frontend | tail -100
```

### PostgreSQL логи

```bash
docker-compose logs postgres | tail -100
```

## Контакты поддержки

Если проблема не решена:
1. Соберите логи всех сервисов
2. Соберите информацию о системе
3. Создайте issue в репозитории

## Связанные разделы

- [Troubleshooting](../troubleshooting/deployment-issues.md) — общий troubleshooting
