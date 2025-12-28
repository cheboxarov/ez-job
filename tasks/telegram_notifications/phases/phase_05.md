# Этап 5: Use cases

## Описание
Создание use cases для бизнес-логики работы с Telegram уведомлениями.

## Подзадачи

1. **`GenerateTelegramLinkTokenUseCase`**
   - Файл: `domain/use_cases/generate_telegram_link_token.py`
   - Создаёт временный токен
   - Удаляет предыдущие токены пользователя
   - Возвращает deep link

2. **`LinkTelegramAccountUseCase`**
   - Файл: `domain/use_cases/link_telegram_account.py`
   - Вызывается из бота при /start TOKEN
   - Валидирует токен и срок
   - Связывает chat_id с user_id
   - Создаёт/обновляет настройки
   - Удаляет использованный токен

3. **`UnlinkTelegramAccountUseCase`**
   - Файл: `domain/use_cases/unlink_telegram_account.py`
   - Удаляет привязку (обнуляет chat_id)
   - Отключает уведомления

4. **`UpdateTelegramNotificationSettingsUseCase`**
   - Файл: `domain/use_cases/update_telegram_notification_settings.py`
   - Обновляет настройки уведомлений
   - Проверяет что Telegram привязан для is_enabled

5. **`GetTelegramSettingsUseCase`**
   - Файл: `domain/use_cases/get_telegram_settings.py`
   - Возвращает текущие настройки
   - Создаёт дефолтные если не существуют

6. **`SendTelegramNotificationUseCase`**
   - Файл: `domain/use_cases/send_telegram_notification.py`
   - Получает настройки пользователя
   - Проверяет is_enabled и конкретный тип
   - Форматирует и отправляет

7. **`SendTestTelegramNotificationUseCase`**
   - Файл: `domain/use_cases/send_test_telegram_notification.py`
   - Отправляет тестовое сообщение
   - Проверяет что Telegram привязан

## Зависимости
- Этап 4: Telegram бот (для отправки сообщений)

## Критерии завершения
- [ ] Все use cases созданы
- [ ] Логика привязки/отвязки работает
- [ ] Настройки сохраняются и читаются
- [ ] Уведомления отправляются с учётом настроек

## Deliverables
- `domain/use_cases/generate_telegram_link_token.py`
- `domain/use_cases/link_telegram_account.py`
- `domain/use_cases/unlink_telegram_account.py`
- `domain/use_cases/update_telegram_notification_settings.py`
- `domain/use_cases/get_telegram_settings.py`
- `domain/use_cases/send_telegram_notification.py`
- `domain/use_cases/send_test_telegram_notification.py`
