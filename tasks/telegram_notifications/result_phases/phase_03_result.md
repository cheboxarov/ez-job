# Результат этапа 3: Infrastructure layer (БД)

## Выполненные подзадачи
- [x] Создана SQLAlchemy модель `TelegramNotificationSettingsModel`
- [x] Создана SQLAlchemy модель `TelegramLinkTokenModel`
- [x] Реализован репозиторий `TelegramNotificationSettingsRepository`
- [x] Реализован репозиторий `TelegramLinkTokenRepository`
- [x] Расширен `UnitOfWorkPort` новыми репозиториями
- [x] Расширен `UnitOfWork` новыми репозиториями
- [x] Добавлены импорты моделей в `alembic/env.py`

## Созданные файлы
- `backend/infrastructure/database/models/telegram_notification_settings_model.py`
- `backend/infrastructure/database/models/telegram_link_token_model.py`
- `backend/infrastructure/database/repositories/telegram_notification_settings_repository.py`
- `backend/infrastructure/database/repositories/telegram_link_token_repository.py`

## Измененные файлы
- `backend/domain/interfaces/unit_of_work_port.py`
- `backend/infrastructure/database/unit_of_work.py`
- `backend/alembic/env.py`

## Изменения в плане
- Нет изменений

## Следующие шаги
- Этап 4: Telegram бот
