# Этап 6: API endpoints

## Описание
Создание REST API эндпоинтов для управления Telegram настройками с фронтенда.

## Подзадачи

1. **Создание DTO запросов**
   - Файл: `presentation/dto/telegram_request.py`
   - `UpdateTelegramNotificationSettingsRequest`

2. **Создание DTO ответов**
   - Файл: `presentation/dto/telegram_response.py`
   - `TelegramNotificationSettingsResponse`
   - `TelegramLinkResponse`

3. **Создание роутера**
   - Файл: `presentation/routers/telegram_router.py`
   - Эндпоинты:
     - `GET /api/telegram/settings` - получить настройки
     - `PUT /api/telegram/settings` - обновить настройки
     - `POST /api/telegram/generate-link` - сгенерировать ссылку привязки
     - `POST /api/telegram/unlink` - отвязать аккаунт
     - `POST /api/telegram/test` - отправить тестовое уведомление

4. **Регистрация роутера**
   - Добавить в `presentation/app.py`

## Зависимости
- Этап 5: Use cases (бизнес-логика для эндпоинтов)

## Критерии завершения
- [ ] Все эндпоинты работают
- [ ] Аутентификация через get_current_user
- [ ] Валидация входных данных
- [ ] Корректные HTTP статусы

## Deliverables
- `presentation/dto/telegram_request.py`
- `presentation/dto/telegram_response.py`
- `presentation/routers/telegram_router.py`
- Обновлённый `presentation/app.py`
