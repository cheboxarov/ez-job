# Этап 1: Миграции БД

## Описание
Создание таблиц в базе данных для хранения настроек Telegram уведомлений и временных токенов привязки.

## Подзадачи

1. **Создание миграции для таблицы `telegram_notification_settings`**
   - Технологии: Alembic, SQLAlchemy
   - Поля: id, user_id, telegram_chat_id, telegram_username, is_enabled, notify_* флаги, timestamps

2. **Создание миграции для таблицы `telegram_link_tokens`**
   - Технологии: Alembic, SQLAlchemy
   - Поля: id, user_id, token, expires_at, created_at
   - Индекс на token для быстрого поиска

3. **Применение миграций**
   - Выполнение `alembic upgrade head`
   - Проверка создания таблиц

## Зависимости
- Нет зависимостей (первый этап)

## Критерии завершения
- [ ] Миграция создана и применена
- [ ] Таблицы существуют в БД
- [ ] FK constraint на users работает
- [ ] Уникальный индекс на token

## Deliverables
- `alembic/versions/xxxx_create_telegram_tables.py`
