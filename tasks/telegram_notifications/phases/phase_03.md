# Этап 3: Infrastructure layer (БД)

## Описание
Реализация SQLAlchemy моделей и репозиториев для работы с таблицами Telegram.

## Подзадачи

1. **Создание SQLAlchemy модели `TelegramNotificationSettingsModel`**
   - Файл: `infrastructure/database/models/telegram_notification_settings_model.py`
   - Маппинг на таблицу `telegram_notification_settings`

2. **Создание SQLAlchemy модели `TelegramLinkTokenModel`**
   - Файл: `infrastructure/database/models/telegram_link_token_model.py`
   - Маппинг на таблицу `telegram_link_tokens`

3. **Реализация `TelegramNotificationSettingsRepository`**
   - Файл: `infrastructure/database/repositories/telegram_notification_settings_repository.py`
   - Имплементация порта с async методами

4. **Реализация `TelegramLinkTokenRepository`**
   - Файл: `infrastructure/database/repositories/telegram_link_token_repository.py`
   - Имплементация порта с async методами

5. **Расширение UnitOfWork**
   - Добавить репозитории в `UnitOfWorkPort` и реализацию
   - Обновить `unit_of_work.py`

## Зависимости
- Этап 1: Миграции БД (таблицы должны существовать)
- Этап 2: Domain layer (интерфейсы для имплементации)

## Критерии завершения
- [ ] Модели созданы и корректно маппятся
- [ ] Репозитории имплементируют порты
- [ ] CRUD операции работают
- [ ] UnitOfWork расширен

## Deliverables
- `infrastructure/database/models/telegram_notification_settings_model.py`
- `infrastructure/database/models/telegram_link_token_model.py`
- `infrastructure/database/repositories/telegram_notification_settings_repository.py`
- `infrastructure/database/repositories/telegram_link_token_repository.py`
- Обновлённый `infrastructure/database/unit_of_work.py`
