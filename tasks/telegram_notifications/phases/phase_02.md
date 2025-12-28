# Этап 2: Domain layer

## Описание
Создание доменных сущностей и интерфейсов (портов) для работы с Telegram уведомлениями.

## Подзадачи

1. **Создание entity `TelegramNotificationSettings`**
   - Файл: `domain/entities/telegram_notification_settings.py`
   - Dataclass с полями настроек

2. **Создание entity `TelegramLinkToken`**
   - Файл: `domain/entities/telegram_link_token.py`
   - Dataclass для временного токена привязки

3. **Создание интерфейса `TelegramNotificationSettingsRepositoryPort`**
   - Файл: `domain/interfaces/telegram_notification_settings_repository_port.py`
   - Методы: get_by_user_id, get_by_telegram_chat_id, create, update, delete

4. **Создание интерфейса `TelegramLinkTokenRepositoryPort`**
   - Файл: `domain/interfaces/telegram_link_token_repository_port.py`
   - Методы: create, get_by_token, delete_by_user_id, delete_expired

5. **Создание интерфейса `TelegramBotPort`**
   - Файл: `domain/interfaces/telegram_bot_port.py`
   - Методы: send_message, send_notification

## Зависимости
- Этап 1: Миграции БД (для понимания структуры)

## Критерии завершения
- [ ] Все entities созданы
- [ ] Все interfaces (порты) созданы
- [ ] Нет импортов внешних библиотек в domain слое

## Deliverables
- `domain/entities/telegram_notification_settings.py`
- `domain/entities/telegram_link_token.py`
- `domain/interfaces/telegram_notification_settings_repository_port.py`
- `domain/interfaces/telegram_link_token_repository_port.py`
- `domain/interfaces/telegram_bot_port.py`
