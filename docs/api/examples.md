# Примеры использования API

Практические примеры использования API проекта "Вкатился".

## Полный цикл: регистрация → создание резюме → поиск вакансий → отклик

### 1. Регистрация

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Вход и получение токена

```bash
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "securepassword123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 3. Создание резюме

```bash
RESUME=$(curl -X POST http://localhost:8000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Опытный Python разработчик с 5+ годами опыта...",
    "user_parameters": "Ищу удаленную работу"
  }' | jq -r '.id')

echo "Resume ID: $RESUME"
```

### 4. Настройка фильтров

```bash
curl -X PUT "http://localhost:8000/api/resumes/$RESUME/filter-settings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "salary_min": 200000,
    "area": "Москва",
    "keywords": "Python, FastAPI, PostgreSQL",
    "stop_words": "стажер, junior"
  }'
```

### 5. Поиск вакансий

```bash
curl -X GET "http://localhost:8000/api/resumes/$RESUME/vacancies" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Генерация сопроводительного письма

```bash
VACANCY_ID="12345678"

curl -X POST "http://localhost:8000/api/vacancies/$VACANCY_ID/cover-letter" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"resume_id\": \"$RESUME\"
  }"
```

### 7. Отклик на вакансию

```bash
curl -X POST "http://localhost:8000/api/vacancies/$VACANCY_ID/respond" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"resume_id\": \"$RESUME\",
    \"cover_letter\": \"Уважаемый работодатель...\"
  }"
```

## Управление подпиской

### Получение текущей подписки

```bash
curl -X GET http://localhost:8000/api/subscription/my-plan \
  -H "Authorization: Bearer $TOKEN"
```

### Выбор плана и оплата

```bash
# Создание платежа
PAYMENT=$(curl -X POST http://localhost:8000/api/subscription/change-plan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "PLAN_1"
  }' | jq -r '.payment_url')

echo "Payment URL: $PAYMENT"
# Редирект пользователя на $PAYMENT
```

## Работа с Telegram

### Генерация ссылки для привязки

```bash
LINK=$(curl -X POST http://localhost:8000/api/telegram/generate-link \
  -H "Authorization: Bearer $TOKEN" | jq -r '.link')

echo "Telegram link: $LINK"
```

### Получение настроек

```bash
curl -X GET http://localhost:8000/api/telegram/settings \
  -H "Authorization: Bearer $TOKEN"
```

### Обновление настроек

```bash
curl -X PUT http://localhost:8000/api/telegram/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notify_new_messages": true,
    "notify_invitations": true,
    "notify_rejections": false
  }'
```

## Python примеры

```python
import httpx

BASE_URL = "http://localhost:8000"
token = None

# Регистрация
response = httpx.post(
    f"{BASE_URL}/auth/register",
    json={"email": "user@example.com", "password": "password123"}
)
user_data = response.json()

# Вход
response = httpx.post(
    f"{BASE_URL}/auth/login",
    json={"username": "user@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Создание резюме
headers = {"Authorization": f"Bearer {token}"}
response = httpx.post(
    f"{BASE_URL}/api/resumes",
    headers=headers,
    json={"content": "Резюме..."}
)
resume = response.json()

# Поиск вакансий
response = httpx.get(
    f"{BASE_URL}/api/resumes/{resume['id']}/vacancies",
    headers=headers
)
vacancies = response.json()
```

## JavaScript примеры

```javascript
const API_BASE_URL = 'http://localhost:8000';

// Вход
async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: email, password })
  });
  const data = await response.json();
  localStorage.setItem('auth_token', data.access_token);
  return data.access_token;
}

// Создание резюме
async function createResume(content) {
  const token = localStorage.getItem('auth_token');
  const response = await fetch(`${API_BASE_URL}/api/resumes`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content })
  });
  return await response.json();
}

// Использование
const token = await login('user@example.com', 'password123');
const resume = await createResume('Резюме...');
```

## Связанные разделы

- [API Overview](README.md) — обзор API
- [Аутентификация](authentication.md) — получение токена
