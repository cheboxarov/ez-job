# SSL сертификаты

Настройка HTTPS для продакшена с использованием Let's Encrypt.

## Получение сертификатов

### Использование Certbot

```bash
# Установка Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

Certbot автоматически:
- Получит сертификаты
- Настроит nginx
- Настроит автоматическое обновление

## Настройка nginx для SSL

### Базовая конфигурация

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Автоматическое обновление

Certbot автоматически настраивает cron для обновления сертификатов.

Проверка:
```bash
sudo certbot renew --dry-run
```

## Проверка SSL

```bash
# Проверка сертификата
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Онлайн проверка
# Используйте https://www.ssllabs.com/ssltest/
```

## Связанные разделы

- [Деплой через Docker](docker-deployment.md) — общий деплой
