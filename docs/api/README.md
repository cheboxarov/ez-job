# API Документация

Документация REST API проекта "AutoOffer".

## Базовый URL

```
http://localhost:8000  # Development
https://api.example.com  # Production
```

## Формат данных

Все запросы и ответы используют формат **JSON**.

## Аутентификация

API использует **JWT (JSON Web Tokens)** для аутентификации. Токен передается в заголовке `Authorization`:

```
Authorization: Bearer <token>
```

Подробнее см. [Аутентификация](authentication.md).

## Коды ответов

- `200 OK` — успешный запрос
- `201 Created` — ресурс создан
- `400 Bad Request` — ошибка валидации
- `401 Unauthorized` — требуется аутентификация
- `403 Forbidden` — недостаточно прав
- `404 Not Found` — ресурс не найден
- `500 Internal Server Error` — внутренняя ошибка сервера

## Версионирование

Текущая версия API: **v1.0.0**

## Rate Limiting

[Описать лимиты, если есть]

## Структура документации

- **[Аутентификация](authentication.md)** — получение и использование токенов
- **[Эндпоинты](endpoints/)** — детальная документация всех эндпоинтов:
  - [Резюме](endpoints/resumes.md)
  - [Вакансии](endpoints/vacancies.md)
  - [Подписки](endpoints/subscriptions.md)
  - [Платежи](endpoints/payments.md)
  - [Telegram](endpoints/telegram.md)
  - [Чаты](endpoints/chats.md)
  - [WebSocket](endpoints/websocket.md)
- **[Примеры использования](examples.md)** — практические примеры
- **[Обработка ошибок](error-handling.md)** — формат ошибок и их обработка

## Swagger UI

Интерактивная документация API доступна по адресу:

```
http://localhost:8000/docs
```

## Связанные разделы

- [Архитектура](../architecture/README.md) — понимание структуры API
- [Development](../development/README.md) — разработка новых эндпоинтов
