# Аутентификация

Документация по аутентификации в API проекта "Вкатился".

## Методы аутентификации

API использует **JWT (JSON Web Tokens)** для аутентификации пользователей.

## Получение токена

### Регистрация

Создание нового аккаунта и получение токена.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Вход

Получение токена для существующего пользователя.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepassword123"
  }'
```

### Вход через HeadHunter

Альтернативный способ входа через HeadHunter.

**Endpoint:** `POST /api/hh-auth/login-by-code`

**Request Body:**
```json
{
  "code": "hh_auth_code_from_redirect"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

## Использование токена

Токен передается в заголовке `Authorization` с префиксом `Bearer`:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Пример запроса с токеном:**
```bash
TOKEN="your-jwt-token-here"

curl -X GET http://localhost:8000/api/resumes \
  -H "Authorization: Bearer $TOKEN"
```

## Время жизни токена

По умолчанию токен действителен **7200000 секунд** (примерно 83 дня).

Это значение можно изменить через переменную окружения `JWT_LIFETIME_SECONDS`.

## Обновление токена

Текущая версия API не поддерживает refresh tokens. При истечении токена необходимо войти заново.

## Восстановление пароля

### Запрос восстановления

**Endpoint:** `POST /auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### Сброс пароля

**Endpoint:** `POST /auth/reset-password`

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "password": "newpassword123"
}
```

## Верификация email

### Запрос верификации

**Endpoint:** `POST /auth/request-verify-token`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### Подтверждение верификации

**Endpoint:** `POST /auth/verify`

**Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

## Обработка ошибок

### 401 Unauthorized

Токен отсутствует, неверен или истек.

```json
{
  "detail": "Not authenticated"
}
```

**Решение:**
- Проверьте наличие токена в заголовке
- Убедитесь, что токен не истек
- Войдите заново для получения нового токена

### 403 Forbidden

Недостаточно прав для выполнения операции.

```json
{
  "detail": "Not enough permissions"
}
```

## Безопасность

1. **Храните токен безопасно** — не передавайте в URL или логах
2. **Используйте HTTPS** — в продакшене всегда используйте HTTPS
3. **Не передавайте токен в публичных местах** — только через заголовки

## Связанные разделы

- [API Overview](README.md) — обзор API
- [Error Handling](error-handling.md) — обработка ошибок
