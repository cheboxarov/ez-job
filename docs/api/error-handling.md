# Обработка ошибок

Документация по обработке ошибок в API.

## Формат ошибок

Все ошибки возвращаются в формате:

```json
{
  "detail": "Описание ошибки"
}
```

## HTTP коды ошибок

### 400 Bad Request

Неверные данные запроса или ошибка валидации.

**Пример:**
```json
{
  "detail": "Validation error: email is required"
}
```

### 401 Unauthorized

Требуется аутентификация или токен неверен/истек.

**Пример:**
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden

Недостаточно прав для выполнения операции.

**Пример:**
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found

Ресурс не найден.

**Пример:**
```json
{
  "detail": "Resume with ID 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### 500 Internal Server Error

Внутренняя ошибка сервера.

**Пример:**
```json
{
  "detail": "Internal server error"
}
```

## Коды ошибок приложения

Некоторые операции могут возвращать специфичные коды ошибок:

- `SUBSCRIPTION_LIMIT_EXCEEDED` — превышен лимит подписки
- `RESUME_NOT_FOUND` — резюме не найдено
- `VACANCY_NOT_FOUND` — вакансия не найдена
- `PAYMENT_FAILED` — ошибка платежа

## Обработка ошибок на клиенте

### JavaScript/TypeScript

```typescript
async function apiRequest(url: string, options: RequestInit) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      
      switch (response.status) {
        case 401:
          // Токен истек, перенаправление на вход
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          // Недостаточно прав
          console.error('Forbidden:', error.detail);
          break;
        case 404:
          // Ресурс не найден
          console.error('Not found:', error.detail);
          break;
        default:
          console.error('Error:', error.detail);
      }
      
      throw new Error(error.detail);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
}
```

### Python

```python
import httpx

def api_request(method: str, url: str, **kwargs):
    try:
        response = httpx.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Токен истек
            print("Token expired, please login again")
        elif e.response.status_code == 403:
            # Недостаточно прав
            print("Forbidden:", e.response.json()["detail"])
        elif e.response.status_code == 404:
            # Ресурс не найден
            print("Not found:", e.response.json()["detail"])
        else:
            print("Error:", e.response.json()["detail"])
        raise
```

## Retry логика

Для нестабильных операций рекомендуется использовать retry:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def api_request_with_retry(url: str):
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()
```

## Связанные разделы

- [API Overview](README.md) — обзор API
- [Аутентификация](authentication.md) — обработка ошибок аутентификации
