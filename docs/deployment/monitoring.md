# Мониторинг и логирование

Настройка мониторинга и логирования для продакшена.

## Логирование

### Где хранятся логи

- **Backend:** `backend/logs/` или Docker volumes
- **Frontend:** nginx access/error logs
- **PostgreSQL:** Docker logs

### Просмотр логов

```bash
# Docker логи
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Файловые логи backend
tail -f backend/logs/*.log
```

### Уровни логирования

Настраиваются через переменную окружения `LOG_LEVEL`:
- `DEBUG` — детальная информация (только для разработки)
- `INFO` — общая информация
- `WARNING` — предупреждения
- `ERROR` — ошибки
- `CRITICAL` — критические ошибки

### Ротация логов

Backend использует loguru с автоматической ротацией:
- Ротация: ежедневно
- Хранение: 7 дней
- Формат: `{time}.log`

## Мониторинг

### Health Checks

#### Backend

```bash
curl http://localhost:8000/health
# Должен вернуть: {"status":"ok"}
```

#### PostgreSQL

```bash
docker-compose exec postgres pg_isready -U postgres
```

### Метрики

#### Использование ресурсов

```bash
# Docker stats
docker stats

# Системные метрики
htop
df -h
free -h
```

### Алерты

Рекомендуется настроить алерты на:
- Недоступность сервисов
- Высокое использование CPU/RAM
- Ошибки в логах
- Проблемы с БД

## Инструменты мониторинга

### Prometheus + Grafana (опционально)

Для продвинутого мониторинга можно настроить:
- Prometheus для сбора метрик
- Grafana для визуализации

### Логирование в облако

Можно настроить отправку логов в:
- ELK Stack
- Loki
- Cloud logging (AWS CloudWatch, Google Cloud Logging)

## Связанные разделы

- [Troubleshooting](../troubleshooting/deployment-issues.md) — решение проблем
