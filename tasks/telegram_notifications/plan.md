# План проекта: Система Telegram уведомлений

## Обзор проекта
- **Тип**: Интеграция Telegram бота + расширение существующего приложения
- **Цель**: Уведомления пользователей в Telegram о событиях (собеседования, формы, отклики)
- **Технологии**: Python, FastAPI, aiogram/python-telegram-bot, PostgreSQL, React, TypeScript
- **Статус**: Планирование
- **Версия плана**: 1.0

## Принятые решения
- Username бота: через переменные окружения (`TELEGRAM_BOT_USERNAME`)
- Тестовое уведомление: да (endpoint + кнопка на фронте)
- Rate limiting: нет
- Режим работы бота: polling
- Inline кнопки: да (ссылки на чаты и вакансии)

## Этапы работы

| Этап | Название | Статус | Зависимости | Прогресс |
|------|----------|--------|-------------|----------|
| 1 | Миграции БД | Не начато | - | 0% |
| 2 | Domain layer | Не начато | Этап 1 | 0% |
| 3 | Infrastructure layer (БД) | Не начато | Этап 2 | 0% |
| 4 | Telegram бот | Не начато | Этап 3 | 0% |
| 5 | Use cases | Не начато | Этап 4 | 0% |
| 6 | API endpoints | Не начато | Этап 5 | 0% |
| 7 | Интеграция с EventPublisher | Не начато | Этап 6 | 0% |
| 8 | Frontend | Не начато | Этап 6 | 0% |

## Архитектура системы

### Новые таблицы БД
```
telegram_notification_settings
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── telegram_chat_id (BIGINT, nullable)
├── telegram_username (VARCHAR(255), nullable)
├── is_enabled (BOOLEAN, default=false)
├── notify_call_request (BOOLEAN, default=true)
├── notify_external_action (BOOLEAN, default=true)
├── notify_question_answered (BOOLEAN, default=true)
├── notify_message_suggestion (BOOLEAN, default=true)
├── notify_vacancy_response (BOOLEAN, default=true)
├── linked_at (DATETIME, nullable)
├── created_at (DATETIME)
└── updated_at (DATETIME)

telegram_link_tokens
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── token (VARCHAR(64), unique)
├── expires_at (DATETIME)
└── created_at (DATETIME)
```

### Структура новых файлов

```
backend/
├── domain/
│   ├── entities/
│   │   ├── telegram_notification_settings.py
│   │   └── telegram_link_token.py
│   ├── interfaces/
│   │   ├── telegram_notification_settings_repository_port.py
│   │   ├── telegram_link_token_repository_port.py
│   │   └── telegram_bot_port.py
│   └── use_cases/
│       ├── generate_telegram_link_token.py
│       ├── link_telegram_account.py
│       ├── unlink_telegram_account.py
│       ├── update_telegram_notification_settings.py
│       ├── get_telegram_settings.py
│       ├── send_telegram_notification.py
│       └── send_test_telegram_notification.py
├── infrastructure/
│   ├── database/
│   │   ├── models/
│   │   │   ├── telegram_notification_settings_model.py
│   │   │   └── telegram_link_token_model.py
│   │   └── repositories/
│   │       ├── telegram_notification_settings_repository.py
│   │       └── telegram_link_token_repository.py
│   └── telegram/
│       ├── telegram_bot.py
│       └── telegram_notification_formatter.py
├── presentation/
│   ├── routers/
│   │   └── telegram_router.py
│   └── dto/
│       ├── telegram_request.py
│       └── telegram_response.py
├── alembic/versions/
│   └── xxxx_create_telegram_tables.py
└── config.py (расширение)

frontend/src/
├── pages/
│   └── SettingsPage.tsx
├── api/
│   └── telegram.ts
└── types/
    └── api.ts (расширение)
```

### Архитектурные принципы
- **Чистая архитектура**: Domain → Use Cases → Infrastructure → Presentation
- **Интерфейсы первые**: Сначала порты, потом реализации
- **YAGNI**: Только необходимые методы

### Переменные окружения
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_BOT_USERNAME=my_hh_bot
FRONTEND_URL=https://app.example.com
```

## Flow привязки Telegram
```
User → Frontend (кнопка "Привязать") 
    → POST /api/telegram/generate-link
    → Backend создаёт токен
    → Возвращает deep link
    → Frontend открывает t.me/bot?start=TOKEN
    → User нажимает Start в боте
    → Бот получает /start TOKEN
    → Бот валидирует токен, связывает chat_id с user_id
    → Бот отправляет "Успешно!"
    → Frontend polling обнаруживает привязку
    → UI показывает настройки уведомлений
```

## Flow отправки уведомления
```
Worker создаёт AgentAction/VacancyResponse
    → EventPublisher публикует событие
    → WebSocket отправляет на фронт (как сейчас)
    → TelegramNotificationSubscriber получает событие
    → Проверяет настройки пользователя
    → Форматирует сообщение с inline кнопками
    → Отправляет через TelegramBot
```

## История изменений
- v1.0 - Первоначальный план (2025-12-28)
