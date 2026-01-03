---
alwaysApply: true
---

Создавать миграции нужно с помощью алембик автогенерейт
Запускать python и остальные скрипты нужно с помощью uv

## Архитектура проекта

Проект использует чистую архитектуру (Clean Architecture) с разделением на слои:

### Структура слоёв:

1. **Domain слой** (`backend/domain/`) — ядро приложения, не зависит ни от чего:
   - `entities/` — доменные сущности (Resume, User, VacancyResponse и т.д.)
   - `interfaces/` — порты (интерфейсы) для всего, что нужно из инфраструктуры
   - `use_cases/` — use cases с бизнес-логикой
   - `exceptions/` — доменные исключения

2. **Infrastructure слой** (`backend/infrastructure/`) — реализация интерфейсов:
   - `database/` — репозитории, модели, UnitOfWork
   - `clients/` — HTTP клиенты (HHClient и т.д.)
   - `agents/` — LLM агенты
   - `telegram/` — Telegram бот
   - `events/` — Event Bus, Event Publisher
   - `websocket/` — WebSocket менеджер

3. **Application слой** (`backend/application/`) — оркестрация:
   - `services/` — сервисы, оркестрирующие use cases
   - `factories/` — фабрики для создания зависимостей

4. **Presentation слой** (`backend/presentation/`) — входная точка:
   - `routers/` — FastAPI роутеры
   - `dto/` — DTO для запросов/ответов
   - `dependencies.py` — FastAPI dependencies

### Правила разработки фич:

1. **Интерфейсы в Domain, реализации в Infrastructure**
   - Все интерфейсы определяются в `domain/interfaces/` (порты)
   - Реализации находятся в `infrastructure/`
   - Use cases работают только с интерфейсами, не с конкретными реализациями

2. **Use cases — единицы бизнес-логики**
   - Каждый use case в `domain/use_cases/` решает одну задачу
   - Принимает зависимости через конструктор (интерфейсы из `domain/interfaces/`)
   - Не зависит от Infrastructure напрямую
   - **Декомпозиция логики**: Use cases должны быть чистыми и не содержать слишком много логики
     - Если use case становится слишком большим (>200 строк), разбить на несколько более мелких use cases
     - Сложная логика должна быть вынесена в отдельные use cases, которые вызываются из основного
     - Use case должен делать одну вещь хорошо, а не пытаться решить все задачи сразу
     - Если use case делает несколько шагов, каждый шаг должен быть либо простым, либо вынесен в отдельный use case

3. **Infrastructure не общается с Application**
   - Infrastructure реализует интерфейсы из Domain
   - Infrastructure НЕ вызывает use cases или сервисы из Application
   - Связь только через интерфейсы Domain

4. **Application оркестрирует use cases**
   - Сервисы в `application/services/` могут вызывать несколько use cases
   - Управляют транзакциями через UnitOfWork
   - Не содержат бизнес-логику (она в use cases)

5. **Presentation использует use cases и сервисы**
   - Роутеры получают use cases через dependencies
   - Могут создавать use cases внутри endpoint'ов, если нужны репозитории из UnitOfWork
   - Преобразуют DTO ↔ Entity

6. **UnitOfWork для транзакций**
   - Все операции с БД через UnitOfWork
   - Репозитории получаются из UnitOfWork
   - Используется как async context manager: `async with unit_of_work:`

7. **Порядок разработки новой фичи:**
   - Определить доменные сущности (если нужны) → `domain/entities/`
   - Определить интерфейсы → `domain/interfaces/`
   - Реализовать интерфейсы → `infrastructure/`
   - Создать use cases → `domain/use_cases/`
   - Создать сервисы (если нужна оркестрация) → `application/services/`
   - Создать роутеры и DTO → `presentation/`

8. **Запрещено:**
   - Infrastructure импортирует что-либо из Application
   - Domain импортирует что-либо из Infrastructure или Application
   - Use cases напрямую используют конкретные классы из Infrastructure
   - Presentation напрямую обращается к Infrastructure (только через use cases)

9. **Разрешено:**
   - Use cases вызывают другие use cases
   - Application сервисы вызывают use cases
   - Presentation создаёт use cases и вызывает их
   - Infrastructure реализует интерфейсы из Domain
