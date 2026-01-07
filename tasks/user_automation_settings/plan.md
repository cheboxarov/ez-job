# План проекта: Настройки автоматизации пользователя

## Обзор проекта
- **Тип**: Расширение функциональности backend и frontend
- **Цель**: Создать систему настроек автоматизации для пользователей с автоматической отправкой ответов на вопросы в чатах и объединить страницы настроек на фронтенде
- **Технологии**: Python (FastAPI, SQLAlchemy, Alembic), TypeScript (React, Ant Design)
- **Статус**: Планирование
- **Версия плана**: 1.0

## Этапы работы

| Этап | Название | Статус | Зависимости | Прогресс |
|------|----------|--------|-------------|----------|
| 1 | Создание доменной модели и интерфейсов для настроек автоматизации | Не начато | - | 0% |
| 2 | Создание инфраструктурного слоя для настроек автоматизации | Не начато | Этап 1 | 0% |
| 3 | Создание use cases для работы с настройками автоматизации | Не начато | Этап 2 | 0% |
| 4 | Создание API endpoints для настроек автоматизации | Не начато | Этап 3 | 0% |
| 5 | Добавление поля sended в AgentAction.data и миграция БД | Не начато | - | 0% |
| 6 | Модификация воркера для автоматической отправки сообщений | Не начато | Этапы 2, 5 | 0% |
| 7 | Создание endpoint для ручной отправки AgentAction | Не начато | Этап 5 | 0% |
| 8 | Объединение страниц настроек на фронтенде | Не начато | Этап 4 | 0% |
| 9 | Обновление компонента ActionCard для работы с sended | Не начато | Этап 7 | 0% |

## Архитектура системы

### Структура проекта:
- **Backend**: Чистая архитектура с разделением на слои Domain → Use Cases → Infrastructure → Presentation
- **Frontend**: React приложение с TypeScript и Ant Design
- **База данных**: PostgreSQL с миграциями через Alembic

### Архитектурные принципы:
- **Чистая архитектура**: Разделение на слои с зависимостями внутрь
- **Интерфейсы первые**: Начинаем с абстракций, не зависящих от библиотек
- **YAGNI принцип**: Создаем только используемые методы и функции
- **Слои**: Domain → Use Cases → Infrastructure → Presentation

## Детальное описание этапов

### Этап 1: Создание доменной модели и интерфейсов для настроек автоматизации

#### Описание
Создание доменной сущности UserAutomationSettings и интерфейса репозитория по аналогии с TelegramNotificationSettings. Сущность будет содержать поле auto_reply_to_questions_in_chats (bool, по умолчанию False) для управления автоматической отправкой ответов на вопросы в чатах.

#### Подзадачи
1. Создать доменную сущность UserAutomationSettings
   - Технологии: Python dataclasses
   - Ресурсы: domain/entities/user_automation_settings.py
   - Детали: Создать dataclass с полями: id (UUID), user_id (UUID), auto_reply_to_questions_in_chats (bool, default=False), created_at (datetime), updated_at (datetime). Структура аналогична TelegramNotificationSettings

2. Создать интерфейс репозитория UserAutomationSettingsRepositoryPort
   - Технологии: Python ABC
   - Ресурсы: domain/interfaces/user_automation_settings_repository_port.py
   - Детали: Определить абстрактные методы: get_by_user_id(user_id: UUID) -> UserAutomationSettings | None, create(settings: UserAutomationSettings) -> UserAutomationSettings, update(settings: UserAutomationSettings) -> UserAutomationSettings. Методы аналогичны TelegramNotificationSettingsRepositoryPort

#### Зависимости
- Завершение этапа: -
- Требуемые ресурсы: Структура проекта, пример TelegramNotificationSettings
- Внешние зависимости: -

#### Критерии завершения
- [ ] Создан файл domain/entities/user_automation_settings.py с доменной сущностью UserAutomationSettings
- [ ] Создан файл domain/interfaces/user_automation_settings_repository_port.py с интерфейсом репозитория
- [ ] Доменная сущность содержит все необходимые поля с правильными типами
- [ ] Интерфейс репозитория содержит методы get_by_user_id, create, update

#### Deliverables
- domain/entities/user_automation_settings.py - доменная сущность
- domain/interfaces/user_automation_settings_repository_port.py - интерфейс репозитория

---

### Этап 2: Создание инфраструктурного слоя для настроек автоматизации

#### Описание
Реализация SQLAlchemy модели, репозитория и интеграция в UnitOfWork для работы с настройками автоматизации в базе данных.

#### Подзадачи
1. Создать SQLAlchemy модель UserAutomationSettingsModel
   - Технологии: SQLAlchemy, PostgreSQL
   - Ресурсы: infrastructure/database/models/user_automation_settings_model.py
   - Детали: Создать модель с таблицей user_automation_settings, полями: id (UUID, PK), user_id (UUID, FK users.id, unique), auto_reply_to_questions_in_chats (Boolean, default=False), created_at (DateTime), updated_at (DateTime). Добавить индексы и constraints аналогично TelegramNotificationSettingsModel

2. Создать миграцию Alembic для таблицы user_automation_settings
   - Технологии: Alembic
   - Ресурсы: backend/alembic/versions/XXXX_create_user_automation_settings.py
   - Детали: **ВАЖНО: Миграцию нужно создавать через команду `alembic revision --autogenerate -m "create_user_automation_settings"` из директории backend.** После создания миграции проверить и при необходимости отредактировать функции upgrade() и downgrade(). В upgrade создать таблицу user_automation_settings с полями из модели, добавить foreign key на users.id с CASCADE, unique constraint на user_id. Убедиться что модель UserAutomationSettingsModel зарегистрирована в alembic/env.py перед созданием миграции

3. Создать репозиторий UserAutomationSettingsRepository
   - Технологии: SQLAlchemy AsyncSession
   - Ресурсы: infrastructure/database/repositories/user_automation_settings_repository.py
   - Детали: Реализовать UserAutomationSettingsRepositoryPort с методами get_by_user_id, create, update. Добавить приватный метод _to_domain для преобразования модели в доменную сущность. Логика аналогична TelegramNotificationSettingsRepository

4. Интегрировать репозиторий в UnitOfWork
   - Технологии: Python
   - Ресурсы: infrastructure/database/unit_of_work.py, domain/interfaces/unit_of_work_port.py
   - Детали: Добавить свойство user_automation_settings_repository в UnitOfWorkPort и UnitOfWork. Инициализировать репозиторий в UnitOfWork.__enter__ аналогично telegram_notification_settings_repository

5. Зарегистрировать модель в Alembic env.py
   - Технологии: Alembic
   - Ресурсы: backend/alembic/env.py
   - Детали: Добавить импорт модели user_automation_settings_model в секцию импортов моделей

#### Зависимости
- Завершение этапа: Этап 1
- Требуемые ресурсы: База данных PostgreSQL, Alembic настроен
- Внешние зависимости: -

#### Критерии завершения
- [ ] Создан файл infrastructure/database/models/user_automation_settings_model.py с SQLAlchemy моделью
- [ ] Модель зарегистрирована в alembic/env.py (перед созданием миграции)
- [ ] Создана миграция Alembic через команду `alembic revision --autogenerate -m "create_user_automation_settings"` из директории backend
- [ ] Миграция содержит корректные функции upgrade() и downgrade()
- [ ] Создан файл infrastructure/database/repositories/user_automation_settings_repository.py с реализацией репозитория
- [ ] Репозиторий интегрирован в UnitOfWork (добавлен в интерфейс и реализацию)
- [ ] Миграция успешно применяется к базе данных через `alembic upgrade head`

#### Deliverables
- infrastructure/database/models/user_automation_settings_model.py - SQLAlchemy модель
- backend/alembic/versions/XXXX_create_user_automation_settings.py - миграция
- infrastructure/database/repositories/user_automation_settings_repository.py - репозиторий
- Обновленные файлы: infrastructure/database/unit_of_work.py, domain/interfaces/unit_of_work_port.py, backend/alembic/env.py

---

### Этап 3: Создание use cases для работы с настройками автоматизации

#### Описание
Создание use cases для получения и обновления настроек автоматизации пользователя. Логика аналогична use cases для TelegramNotificationSettings.

#### Подзадачи
1. Создать GetUserAutomationSettingsUseCase
   - Технологии: Python
   - Ресурсы: domain/use_cases/get_user_automation_settings.py
   - Детали: Создать use case который получает настройки по user_id. Если настройки не существуют, создает их с дефолтными значениями (auto_reply_to_questions_in_chats=False). Логика аналогична GetTelegramSettingsUseCase

2. Создать UpdateUserAutomationSettingsUseCase
   - Технологии: Python
   - Ресурсы: domain/use_cases/update_user_automation_settings.py
   - Детали: Создать use case для обновления настроек автоматизации. Принимает user_id и auto_reply_to_questions_in_chats. Получает существующие настройки, обновляет поле, сохраняет и возвращает обновленную сущность. Логика аналогична UpdateTelegramNotificationSettingsUseCase

#### Зависимости
- Завершение этапа: Этап 2
- Требуемые ресурсы: Репозиторий настроек автоматизации
- Внешние зависимости: -

#### Критерии завершения
- [ ] Создан файл domain/use_cases/get_user_automation_settings.py с GetUserAutomationSettingsUseCase
- [ ] Создан файл domain/use_cases/update_user_automation_settings.py с UpdateUserAutomationSettingsUseCase
- [ ] GetUserAutomationSettingsUseCase создает настройки с дефолтными значениями если их нет
- [ ] UpdateUserAutomationSettingsUseCase корректно обновляет существующие настройки

#### Deliverables
- domain/use_cases/get_user_automation_settings.py - use case для получения настроек
- domain/use_cases/update_user_automation_settings.py - use case для обновления настроек

---

### Этап 4: Создание API endpoints для настроек автоматизации

#### Описание
Создание REST API endpoints для получения и обновления настроек автоматизации пользователя. Endpoints аналогичны endpoints для Telegram settings.

#### Подзадачи
1. Создать DTO для запросов и ответов
   - Технологии: Pydantic
   - Ресурсы: presentation/dto/automation_request.py, presentation/dto/automation_response.py
   - Детали: Создать UpdateUserAutomationSettingsRequest с полем auto_reply_to_questions_in_chats (bool | None). Создать UserAutomationSettingsResponse с полями из доменной сущности и методом from_entity. Структура аналогична Telegram DTO

2. Создать роутер для настроек автоматизации
   - Технологии: FastAPI
   - Ресурсы: presentation/routers/automation_router.py
   - Детали: Создать роутер с prefix="/api/settings/automation". Добавить GET /settings/automation для получения настроек (использует GetUserAutomationSettingsUseCase). Добавить PUT /settings/automation для обновления настроек (использует UpdateUserAutomationSettingsUseCase). Оба endpoint требуют аутентификации через get_current_active_user

3. Зарегистрировать роутер в приложении
   - Технологии: FastAPI
   - Ресурсы: presentation/app.py
   - Детали: Импортировать automation_router и добавить app.include_router(automation_router)

#### Зависимости
- Завершение этапа: Этап 3
- Требуемые ресурсы: Use cases для настроек автоматизации
- Внешние зависимости: FastAPI, аутентификация

#### Критерии завершения
- [ ] Создан файл presentation/dto/automation_request.py с UpdateUserAutomationSettingsRequest
- [ ] Создан файл presentation/dto/automation_response.py с UserAutomationSettingsResponse
- [ ] Создан файл presentation/routers/automation_router.py с GET и PUT endpoints
- [ ] Роутер зарегистрирован в presentation/app.py
- [ ] Endpoints корректно работают и возвращают правильные данные

#### Deliverables
- presentation/dto/automation_request.py - DTO для запросов
- presentation/dto/automation_response.py - DTO для ответов
- presentation/routers/automation_router.py - роутер с endpoints
- Обновленный файл: presentation/app.py

---

### Этап 5: Добавление поля sended в AgentAction.data и миграция БД

#### Описание
Добавление поля sended (bool) в структуру данных AgentAction.data для отслеживания статуса отправки сообщения. Это поле будет храниться в JSON колонке data таблицы agent_actions.

#### Подзадачи
1. Обновить доменную сущность AgentAction
   - Технологии: Python dataclasses
   - Ресурсы: domain/entities/agent_action.py
   - Детали: Обновить документацию поля data, указать что для типа "send_message" поле data должно содержать sended: bool (по умолчанию False при создании). Обновить описание структуры data в docstring

2. Обновить логику создания AgentAction в воркере
   - Технологии: Python
   - Ресурсы: backend/infrastructure/agents/messages_agent.py, backend/workers/chat_analysis_worker.py
   - Детали: При создании AgentAction типа "send_message" в messages_agent или chat_analysis_worker, убедиться что в data добавляется поле "sended": False. Проверить все места где создаются AgentAction с типом send_message

3. Обновить DTO AgentActionResponse
   - Технологии: Pydantic
   - Ресурсы: presentation/dto/agent_action_response.py
   - Детали: Убедиться что AgentActionResponse корректно сериализует поле data со всеми полями включая sended. Проверить метод from_entity

#### Зависимости
- Завершение этапа: -
- Требуемые ресурсы: Доменная сущность AgentAction
- Внешние зависимости: -

#### Критерии завершения
- [ ] Обновлена документация AgentAction.data с указанием поля sended для типа send_message
- [ ] При создании AgentAction типа send_message в data добавляется sended: False
- [ ] AgentActionResponse корректно сериализует поле data с sended
- [ ] Все существующие AgentAction типа send_message имеют sended: False в data (или null, что обрабатывается как False)

#### Deliverables
- Обновленные файлы: domain/entities/agent_action.py, backend/infrastructure/agents/messages_agent.py (если нужно), presentation/dto/agent_action_response.py

---

### Этап 6: Модификация воркера для автоматической отправки сообщений

#### Описание
Модификация chat_analysis_worker для автоматической отправки сообщений через ExecuteAgentActionUseCase когда у пользователя включена настройка auto_reply_to_questions_in_chats и создан AgentAction типа send_message.

#### Подзадачи
1. Получать настройки автоматизации в воркере через use case
   - Технологии: Python
   - Ресурсы: backend/workers/chat_analysis_worker.py
   - Детали: В функции process_chats_cycle после получения пользователя создавать GetUserAutomationSettingsUseCase с репозиторием из uow.user_automation_settings_repository. Вызывать execute(user.id) для получения настроек. Use case автоматически создаст настройки с дефолтными значениями если их нет (согласно логике GetUserAutomationSettingsUseCase). **Важно: использовать use case, а не напрямую репозиторий, для соблюдения чистой архитектуры**

2. Добавить логику автоматической отправки для send_message действий
   - Технологии: Python
   - Ресурсы: backend/workers/chat_analysis_worker.py
   - Детали: После сохранения AgentAction в БД, если настройка auto_reply_to_questions_in_chats=True и action.type == "send_message" и action.data.get("sended") != True, вызывать ExecuteAgentActionUseCase для отправки сообщения (передать action, headers, cookies, user_id, update_cookies_uc). При успешной отправке вызывать MarkAgentActionAsSentUseCase для обновления sended в БД. При ошибке логировать ошибку и продолжать работу (не прерывать цикл). **Важно: использовать use cases для всех операций с БД, не напрямую репозиторий**

3. Создать use case для обновления sended в AgentAction
   - Технологии: Python
   - Ресурсы: domain/use_cases/mark_agent_action_as_sent.py
   - Детали: Создать use case MarkAgentActionAsSentUseCase в domain/use_cases который принимает action: AgentAction (доменную сущность), обновляет data["sended"] = True, сохраняет через AgentActionRepositoryPort и возвращает обновленный AgentAction. Use case должен работать только с доменными сущностями и интерфейсами, без зависимостей от Infrastructure. Использовать этот use case в воркере после успешной отправки

4. Добавить необходимые зависимости в воркер
   - Технологии: Python
   - Ресурсы: backend/workers/chat_analysis_worker.py
   - Детали: Импортировать ExecuteAgentActionUseCase, SendChatMessageUseCase, GetUserAutomationSettingsUseCase, MarkAgentActionAsSentUseCase. Создать экземпляры use cases с необходимыми зависимостями: GetUserAutomationSettingsUseCase(uow.user_automation_settings_repository), ExecuteAgentActionUseCase(uow.agent_action_repository, send_chat_message_uc), SendChatMessageUseCase(hh_client), MarkAgentActionAsSentUseCase(uow.agent_action_repository). **Важно: все операции через use cases, не напрямую через репозитории**

#### Зависимости
- Завершение этапа: Этапы 2, 5
- Требуемые ресурсы: Настройки автоматизации, ExecuteAgentActionUseCase, AgentAction с полем sended
- Внешние зависимости: HH API для отправки сообщений

#### Критерии завершения
- [ ] Воркер получает настройки автоматизации через GetUserAutomationSettingsUseCase (не напрямую через репозиторий)
- [ ] При auto_reply_to_questions_in_chats=True автоматически отправляются сообщения для send_message действий через ExecuteAgentActionUseCase
- [ ] После успешной отправки sended обновляется на True в БД через MarkAgentActionAsSentUseCase
- [ ] При ошибке отправки ошибка логируется, но цикл продолжается
- [ ] Создан use case MarkAgentActionAsSentUseCase в domain/use_cases для обновления статуса отправки
- [ ] Все операции с БД выполняются через use cases, соблюдена чистая архитектура

#### Deliverables
- domain/use_cases/mark_agent_action_as_sent.py - use case для пометки как отправленного
- Обновленный файл: backend/workers/chat_analysis_worker.py

---

### Этап 7: Создание endpoint для ручной отправки AgentAction

#### Описание
Создание REST API endpoint POST /api/agent-actions/{id}/execute для ручной отправки сообщения из AgentAction типа send_message. Для этого потребуется добавить метод get_by_id в AgentActionRepositoryPort.

#### Подзадачи
1. Добавить метод get_by_id в AgentActionRepositoryPort
   - Технологии: Python ABC
   - Ресурсы: domain/interfaces/agent_action_repository_port.py
   - Детали: Добавить абстрактный метод get_by_id(action_id: UUID) -> AgentAction | None в интерфейс AgentActionRepositoryPort. Метод должен возвращать AgentAction по ID или None если не найдено

2. Реализовать метод get_by_id в AgentActionRepository
   - Технологии: SQLAlchemy
   - Ресурсы: infrastructure/database/repositories/agent_action_repository.py
   - Детали: Реализовать метод get_by_id который выполняет SELECT запрос по id, преобразует результат в доменную сущность через _to_domain и возвращает её или None

3. Создать use case ExecuteAgentActionByIdUseCase
   - Технологии: Python
   - Ресурсы: domain/use_cases/execute_agent_action_by_id.py
   - Детали: Создать use case в domain/use_cases который принимает в конструкторе: agent_action_repository (AgentActionRepositoryPort), execute_agent_action_uc (ExecuteAgentActionUseCase), mark_agent_action_as_sent_uc (MarkAgentActionAsSentUseCase). Метод execute принимает action_id (UUID), user_id (UUID), headers (Dict[str, str]), cookies (Dict[str, str]), update_cookies_uc (UpdateUserHhAuthCookiesUseCase). Use case получает AgentAction через agent_action_repository.get_by_id(action_id), проверяет что action существует (иначе ValueError), проверяет что action.user_id == user_id (валидация прав доступа, иначе ValueError), проверяет что action.type == "send_message" (иначе ValueError), проверяет что action.data.get("sended") != True (если уже отправлен, возвращает ValueError), вызывает execute_agent_action_uc.execute(action, headers=headers, cookies=cookies, user_id=user_id, update_cookies_uc=update_cookies_uc), при успехе вызывает mark_agent_action_as_sent_uc.execute(action), возвращает обновленный AgentAction. **Важно: use case работает только с интерфейсами из domain/interfaces, без зависимостей от Infrastructure**

4. Добавить endpoint в agent_actions_router
   - Технологии: FastAPI
   - Ресурсы: presentation/routers/agent_actions_router.py
   - Детали: Добавить POST /{action_id}/execute endpoint. Endpoint принимает action_id (UUID) из path, получает current_user через get_current_active_user, получает headers и cookies через get_headers и get_cookies, создает ExecuteAgentActionByIdUseCase через dependency injection (get_execute_agent_action_by_id_uc), вызывает execute с action_id, user_id, headers, cookies, update_cookies_uc. При успехе возвращает AgentActionResponse.from_entity(updated_action). При ошибках возвращает соответствующие HTTPException (404 если action не найден, 400 если action не типа send_message или уже отправлен, 403 если action принадлежит другому пользователю). **Важно: endpoint использует use case через dependency injection, не создает use case напрямую**

5. Обновить dependencies для создания use cases
   - Технологии: FastAPI Depends
   - Ресурсы: presentation/dependencies.py
   - Детали: Добавить функцию get_execute_agent_action_by_id_uc которая принимает unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work), send_chat_message_uc: SendChatMessageUseCase = Depends(get_send_chat_message_uc). Функция создает: ExecuteAgentActionUseCase(uow.agent_action_repository, send_chat_message_uc), MarkAgentActionAsSentUseCase(uow.agent_action_repository), ExecuteAgentActionByIdUseCase(uow.agent_action_repository, execute_agent_action_uc, mark_agent_action_as_sent_uc). Возвращает ExecuteAgentActionByIdUseCase. **Важно: все зависимости создаются через unit_of_work и существующие dependencies, соблюдена чистая архитектура**

#### Зависимости
- Завершение этапа: Этап 5
- Требуемые ресурсы: ExecuteAgentActionUseCase, MarkAgentActionAsSentUseCase, AgentAction репозиторий
- Внешние зависимости: FastAPI, аутентификация

#### Критерии завершения
- [ ] Добавлен метод get_by_id в AgentActionRepositoryPort интерфейс
- [ ] Реализован метод get_by_id в AgentActionRepository
- [ ] Создан файл domain/use_cases/execute_agent_action_by_id.py с ExecuteAgentActionByIdUseCase
- [ ] Добавлен endpoint POST /api/agent-actions/{id}/execute в agent_actions_router
- [ ] Endpoint проверяет права доступа (action принадлежит текущему пользователю)
- [ ] Endpoint проверяет тип действия (только send_message)
- [ ] Endpoint обновляет sended на True после успешной отправки
- [ ] Добавлена функция get_execute_agent_action_by_id_uc в dependencies.py

#### Deliverables
- Обновленные файлы: domain/interfaces/agent_action_repository_port.py, infrastructure/database/repositories/agent_action_repository.py
- domain/use_cases/execute_agent_action_by_id.py - use case для выполнения действия по ID
- Обновленные файлы: presentation/routers/agent_actions_router.py, presentation/dependencies.py

---

### Этап 8: Объединение страниц настроек на фронтенде

#### Описание
Создание единой страницы настроек /settings с двумя разделами: "Уведомления" (текущие настройки Telegram) и "Автоматизация" (новые настройки автоматической отправки ответов).

#### Подзадачи
1. Создать API функции для работы с настройками автоматизации
   - Технологии: TypeScript, Axios
   - Ресурсы: frontend/src/api/automation.ts
   - Детали: Создать функции getAutomationSettings() и updateAutomationSettings(auto_reply_to_questions_in_chats: boolean) для работы с API endpoints /api/settings/automation. Использовать apiClient из utils/api

2. Добавить типы для настроек автоматизации
   - Технологии: TypeScript
   - Ресурсы: frontend/src/types/api.ts
   - Детали: Добавить интерфейсы UserAutomationSettings и UpdateUserAutomationSettingsRequest в types/api.ts по аналогии с TelegramNotificationSettings

3. Создать компонент SettingsPage
   - Технологии: React, TypeScript, Ant Design
   - Ресурсы: frontend/src/pages/SettingsPage.tsx
   - Детали: Создать новую страницу SettingsPage с двумя Card компонентами: "Уведомления" (содержит весь функционал из TelegramSettingsPage) и "Автоматизация" (содержит переключатель для auto_reply_to_questions_in_chats). Использовать Tabs или два отдельных Card для разделения. Страница должна загружать оба типа настроек при монтировании

4. Обновить роутинг в App.tsx
   - Технологии: React Router
   - Ресурсы: frontend/src/App.tsx
   - Детали: Добавить маршрут /settings который ведет на SettingsPage. Обновить ссылку в MainLayout с /settings/telegram на /settings. Можно оставить /settings/telegram как редирект на /settings для обратной совместимости

5. Обновить навигацию в MainLayout
   - Технологии: React
   - Ресурсы: frontend/src/components/Layout/MainLayout.tsx
   - Детали: Изменить ключ меню с /settings/telegram на /settings, обновить label на "Настройки"

#### Зависимости
- Завершение этапа: Этап 4
- Требуемые ресурсы: API endpoints для настроек автоматизации
- Внешние зависимости: React Router, Ant Design

#### Критерии завершения
- [ ] Создан файл frontend/src/api/automation.ts с функциями для работы с API
- [ ] Добавлены типы UserAutomationSettings и UpdateUserAutomationSettingsRequest в types/api.ts
- [ ] Создан файл frontend/src/pages/SettingsPage.tsx с двумя разделами настроек
- [ ] Страница SettingsPage корректно загружает и отображает оба типа настроек
- [ ] Обновлен роутинг в App.tsx для маршрута /settings
- [ ] Обновлена навигация в MainLayout для ссылки на /settings
- [ ] Страница /settings/telegram редиректит на /settings (опционально)

#### Deliverables
- frontend/src/api/automation.ts - API функции
- frontend/src/pages/SettingsPage.tsx - объединенная страница настроек
- Обновленные файлы: frontend/src/types/api.ts, frontend/src/App.tsx, frontend/src/components/Layout/MainLayout.tsx

---

### Этап 9: Обновление компонента ActionCard для работы с sended

#### Описание
Обновление компонента ActionCard для проверки поля sended и отображения кнопки отправки только если sended === false. При клике на кнопку вызывать новый endpoint для выполнения действия.

#### Подзадачи
1. Добавить API функцию для выполнения AgentAction
   - Технологии: TypeScript, Axios
   - Ресурсы: frontend/src/api/agentActions.ts
   - Детали: Добавить функцию executeAgentAction(actionId: string) которая вызывает POST /api/agent-actions/{actionId}/execute. Функция должна возвращать обновленный AgentAction

2. Обновить компонент ActionCard
   - Технологии: React, TypeScript
   - Ресурсы: frontend/src/components/ActionCard.tsx
   - Детали: Проверять action.data.sended перед отображением кнопки отправки. Если sended === true (или undefined/null обрабатывать как false для обратной совместимости), не показывать кнопку или показывать её в disabled состоянии с текстом "Отправлено". При клике на кнопку вызывать executeAgentAction вместо прямого вызова sendChatMessage. После успешного выполнения обновлять локальное состояние или вызывать onSent callback

3. Обновить типы AgentAction
   - Технологии: TypeScript
   - Ресурсы: frontend/src/types/api.ts
   - Детали: Убедиться что интерфейс AgentAction.data содержит поле sended?: boolean в описании типа. Обновить документацию типа если нужно

#### Зависимости
- Завершение этапа: Этап 7
- Требуемые ресурсы: Endpoint для выполнения AgentAction
- Внешние зависимости: -

#### Критерии завершения
- [ ] Добавлена функция executeAgentAction в frontend/src/api/agentActions.ts
- [ ] ActionCard проверяет action.data.sended перед отображением кнопки
- [ ] Кнопка отправки скрыта или disabled если sended === true
- [ ] При клике на кнопку вызывается executeAgentAction вместо sendChatMessage
- [ ] После успешного выполнения action обновляется и кнопка скрывается
- [ ] Типы AgentAction.data содержат поле sended

#### Deliverables
- Обновленные файлы: frontend/src/api/agentActions.ts, frontend/src/components/ActionCard.tsx, frontend/src/types/api.ts

---

## История изменений
- v1.2 - Добавлен метод get_by_id в AgentActionRepositoryPort для получения AgentAction по ID, уточнены зависимости use cases (2024-12-19)
- v1.1 - Добавлены инструкции по созданию миграций через `alembic revision --autogenerate`, исправлена архитектура воркера для использования use cases вместо прямого обращения к репозиториям (2024-12-19)
- v1.0 - Первоначальный план (2024-12-19)
