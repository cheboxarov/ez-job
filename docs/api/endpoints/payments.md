# Эндпоинты: Платежи

Документация эндпоинтов для работы с платежами (после интеграции ЮКассы).

## Базовый путь

```
/api/payments
```

## Создание платежа

**Endpoint:** `POST /api/payments`

**Описание:** Создание платежа для оплаты подписки.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "plan_name": "PLAN_1"
}
```

**Response:** `201 Created`
```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_url": "https://yookassa.ru/checkout/payments/...",
  "amount": 990.0,
  "currency": "RUB"
}
```

## Получение статуса платежа

**Endpoint:** `GET /api/payments/{payment_id}`

**Описание:** Получение информации о платеже.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "succeeded",
  "amount": 990.0,
  "created_at": "2025-01-28T10:00:00Z",
  "paid_at": "2025-01-28T10:05:00Z"
}
```

## Webhook от ЮКассы

**Endpoint:** `POST /api/payments/webhook`

**Описание:** Эндпоинт для получения уведомлений от ЮКассы о статусе платежа.

**Аутентификация:** Не требуется (проверка подписи)

**Request Body:** JSON от ЮКассы

**Response:** `200 OK`

## Страница успешной оплаты

**Endpoint:** `GET /api/payments/success`

**Описание:** Обработка возврата пользователя после оплаты.

**Аутентификация:** Не требуется

**Query Parameters:**
- `payment_id` (string) — ID платежа

**Response:** `200 OK` — информация о платеже и подписке

## Связанные разделы

- [Подписки](subscriptions.md) — управление подписками
- [API Overview](../README.md) — обзор API
