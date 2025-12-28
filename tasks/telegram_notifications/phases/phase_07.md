# Этап 7: Интеграция с EventPublisher

## Описание
Подключение отправки Telegram уведомлений к существующей системе событий.

## Подзадачи

1. **Создание Telegram subscriber**
   - Либо расширение `EventPublisher`
   - Либо отдельный subscriber в Event Bus
   - При публикации события → вызов SendTelegramNotificationUseCase

2. **Расширение фабрики событий**
   - Файл: `application/factories/event_factory.py`
   - Добавить создание TelegramBot и use cases

3. **Подключение к существующим use cases**
   - `CreateAgentActionWithNotificationUseCase` - добавить Telegram
   - `CreateVacancyResponseWithNotificationUseCase` - добавить Telegram

## Зависимости
- Этап 6: API endpoints (инфраструктура готова)

## Критерии завершения
- [ ] При создании AgentAction отправляется Telegram (если включено)
- [ ] При создании VacancyResponse отправляется Telegram (если включено)
- [ ] Типы уведомлений фильтруются по настройкам
- [ ] Ошибки Telegram не блокируют основной flow

## Deliverables
- Обновлённый `infrastructure/events/event_publisher.py` или новый subscriber
- Обновлённый `application/factories/event_factory.py`
