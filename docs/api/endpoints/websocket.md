# WebSocket API

Документация WebSocket API для real-time обновлений.

## Подключение

**URL:** `ws://localhost:8000/ws?token=<jwt_token>`

**Аутентификация:** Требуется JWT токен в query параметре

**Пример:**
```javascript
const token = localStorage.getItem('auth_token');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
```

## События

### События от сервера

#### vacancy_response_created

Уведомление о создании отклика на вакансию.

```json
{
  "type": "vacancy_response_created",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "vacancy_name": "Python Developer",
    "created_at": "2025-01-28T10:00:00Z"
  }
}
```

#### agent_action_created

Уведомление о новом действии агента.

```json
{
  "type": "agent_action_created",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "action_type": "reply_to_message",
    "entity_type": "chat"
  }
}
```

#### subscription_updated

Уведомление об обновлении подписки.

```json
{
  "type": "subscription_updated",
  "data": {
    "plan_name": "PLAN_1",
    "responses_count": 25,
    "limit": 50
  }
}
```

## Использование на клиенте

### JavaScript/TypeScript

```typescript
const token = localStorage.getItem('auth_token');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  switch (message.type) {
    case 'vacancy_response_created':
      // Обработка создания отклика
      break;
    case 'agent_action_created':
      // Обработка действия агента
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

## Связанные разделы

- [API Overview](../README.md) — обзор API
- [Components: WebSocket](../../components/websocket.md) — детальная документация
