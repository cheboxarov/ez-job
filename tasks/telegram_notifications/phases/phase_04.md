# Этап 4: Telegram бот

## Описание
Реализация Telegram бота с поддержкой команд привязки/отвязки и отправки уведомлений с inline кнопками.

## Подзадачи

1. **Расширение конфигурации**
   - Файл: `config.py`
   - Добавить `TelegramConfig` с полями: bot_token, bot_username, link_token_ttl_seconds, frontend_url
   - Загрузка из переменных окружения

2. **Создание форматтера уведомлений**
   - Файл: `infrastructure/telegram/telegram_notification_formatter.py`
   - Методы форматирования для разных типов событий
   - Генерация inline клавиатуры с кнопками

3. **Реализация Telegram бота**
   - Файл: `infrastructure/telegram/telegram_bot.py`
   - Библиотека: aiogram 3.x или python-telegram-bot
   - Handlers: /start, /start TOKEN, /unlink, /help
   - Методы: send_message, send_notification
   - Polling режим

4. **Интеграция с FastAPI**
   - Запуск бота как background task при старте приложения
   - Graceful shutdown при остановке

## Зависимости
- Этап 3: Infrastructure layer (репозитории для работы с БД)

## Критерии завершения
- [ ] Бот запускается вместе с FastAPI
- [ ] Команда /start TOKEN работает
- [ ] Команда /unlink работает
- [ ] Уведомления отправляются с inline кнопками
- [ ] Graceful shutdown работает

## Deliverables
- Обновлённый `config.py`
- `infrastructure/telegram/telegram_notification_formatter.py`
- `infrastructure/telegram/telegram_bot.py`
- Обновлённый `presentation/app.py` (запуск бота)
