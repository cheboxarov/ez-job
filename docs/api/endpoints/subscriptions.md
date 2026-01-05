# Эндпоинты: Подписки

Документация эндпоинтов для работы с подписками.

## Базовый путь

```
/api/subscription
```

## Получение текущей подписки

**Endpoint:** `GET /api/subscription/my-plan`

**Описание:** Получение информации о текущем плане подписки пользователя.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_name": "PLAN_1",
  "response_limit": 50,
  "reset_period_seconds": 86400,
  "responses_count": 25,
  "period_started_at": "2025-01-28T10:00:00Z",
  "next_reset_at": "2025-01-29T10:00:00Z",
  "seconds_until_reset": 43200,
  "started_at": "2025-01-01T00:00:00Z",
  "expires_at": "2025-01-31T23:59:59Z",
  "days_remaining": 3
}
```

## Получение лимитов откликов

**Endpoint:** `GET /api/subscription/daily-responses`

**Описание:** Получение информации о количестве откликов за текущий период.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "count": 25,
  "limit": 50,
  "remaining": 25,
  "period_started_at": "2025-01-28T10:00:00Z",
  "seconds_until_reset": 43200
}
```

## Получение списка планов

**Endpoint:** `GET /api/subscription/plans`

**Описание:** Получение списка всех доступных планов подписки.

**Аутентификация:** Не требуется

**Response:** `200 OK`
```json
{
  "plans": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "FREE",
      "response_limit": 10,
      "reset_period_seconds": 2592000,
      "duration_days": 0,
      "price": 0.0
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "PLAN_1",
      "response_limit": 50,
      "reset_period_seconds": 86400,
      "duration_days": 30,
      "price": 990.0
    }
  ]
}
```

## Смена плана подписки

**Endpoint:** `POST /api/subscription/change-plan`

**Описание:** Изменение плана подписки (для платных планов создается платеж).

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "plan_name": "PLAN_1"
}
```

**Response:** `200 OK` — обновленная подписка или URL для оплаты

## Связанные разделы

- [Платежи](payments.md) — оплата подписки
- [API Overview](../README.md) — обзор API
