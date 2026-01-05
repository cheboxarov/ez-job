# Проблемы при деплое

Решение проблем при развертывании системы.

## Проблемы с Docker

### Контейнеры не запускаются

**Проблема:** Контейнеры падают сразу после запуска.

**Решение:**
1. Проверьте логи: `docker-compose logs`
2. Проверьте переменные окружения: `docker-compose config`
3. Проверьте, что порты не заняты: `netstat -tulpn | grep :8000`
4. Проверьте доступное место на диске: `df -h`

### Ошибки при сборке образов

**Проблема:** `docker-compose build` падает с ошибками.

**Решение:**
1. Проверьте Dockerfile на ошибки
2. Очистите кэш: `docker system prune -a`
3. Пересоберите образ: `docker-compose build --no-cache`

## Проблемы с nginx

### Frontend не доступен

**Проблема:** 502 Bad Gateway или страница не загружается.

**Решение:**
1. Проверьте конфигурацию nginx: `docker-compose exec frontend nginx -t`
2. Проверьте логи: `docker-compose logs frontend`
3. Убедитесь, что backend доступен: `curl http://backend:8000/health`

### Ошибки проксирования

**Проблема:** API запросы не проходят через nginx.

**Решение:**
1. Проверьте конфигурацию `/api` location в nginx.conf
2. Проверьте, что backend контейнер запущен
3. Проверьте сеть Docker: `docker network ls`

## Проблемы с SSL

### Сертификат не работает

**Проблема:** Ошибки SSL при доступе к сайту.

**Решение:**
1. Проверьте сертификат: `openssl s_client -connect yourdomain.com:443`
2. Проверьте срок действия: `certbot certificates`
3. Обновите сертификат: `sudo certbot renew`

### Автообновление не работает

**Проблема:** Сертификат не обновляется автоматически.

**Решение:**
1. Проверьте cron: `sudo crontab -l`
2. Проверьте права доступа к сертификатам
3. Запустите обновление вручную: `sudo certbot renew --dry-run`

## Проблемы с мониторингом

### Логи не пишутся

**Проблема:** Логи не сохраняются.

**Решение:**
1. Проверьте права доступа к директории логов
2. Проверьте Docker volumes: `docker volume ls`
3. Проверьте настройки логирования в коде

### Health checks не работают

**Проблема:** Health checks падают.

**Решение:**
1. Проверьте endpoint: `curl http://localhost:8000/health`
2. Проверьте конфигурацию healthcheck в docker-compose.yml
3. Проверьте логи контейнера

## Связанные разделы

- [Deployment: Troubleshooting](../deployment/troubleshooting-deployment.md) — детальный troubleshooting
- [Troubleshooting: Общие проблемы](common-issues.md) — другие проблемы
