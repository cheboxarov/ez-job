# WebSocket

Документация WebSocket сервера для real-time коммуникации.

## Назначение

WebSocket используется для отправки real-time уведомлений клиентам о событиях в системе:

- Создание откликов
- Новые действия агента
- Обновления подписки
- Другие события

## Подключение

### URL

```
ws://localhost:8000/ws?token=<jwt_token>
```

### Аутентификация

Токен передается в query параметре `token`.

### Пример подключения

```javascript
const token = localStorage.getItem('auth_token');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

## События

### vacancy_response_created

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

### agent_action_created

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

### subscription_updated

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

### React Hook

```typescript
import { useEffect, useState } from 'react';

function useWebSocket() {
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };
    
    return () => ws.close();
  }, []);
  
  return messages;
}
```

## Связанные разделы

- [API: WebSocket](../api/endpoints/websocket.md) — детальная документация API
