# Эндпоинты: Telegram

Документация эндпоинтов для работы с Telegram интеграцией.

## Базовый путь

```
/api/telegram
```

## Генерация ссылки для привязки

**Endpoint:** `POST /api/telegram/generate-link`

**Описание:** Генерация временной ссылки для привязки Telegram аккаунта.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "link": "https://t.me/your_bot?start=token123",
  "expires_at": "2025-01-28T10:10:00Z"
}
```

## Получение настроек уведомлений

**Endpoint:** `GET /api/telegram/settings`

**Описание:** Получение настроек Telegram уведомлений.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "is_enabled": true,
  "telegram_username": "username",
  "notify_new_messages": true,
  "notify_invitations": true,
  "notify_rejections": false
}
```

## Обновление настроек уведомлений

**Endpoint:** `PUT /api/telegram/settings`

**Описание:** Обновление настроек Telegram уведомлений.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "notify_new_messages": true,
  "notify_invitations": true,
  "notify_rejections": false
}
```

**Response:** `200 OK` — обновленные настройки

## Отвязка Telegram аккаунта

**Endpoint:** `DELETE /api/telegram/unlink`

**Описание:** Отвязка Telegram аккаунта от пользователя.

**Аутентификация:** Требуется

**Response:** `204 No Content`

## Связанные разделы

- [API Overview](../README.md) — обзор API
- [Components: Telegram Bot](../../components/telegram-bot.md) — документация бота
