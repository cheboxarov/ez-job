# Паттерны проектирования

Описание паттернов проектирования, используемых в проекте "AutoOffer".

## Repository Pattern

**Назначение:** Абстракция доступа к данным.

**Применение:**
- Все операции с БД через репозитории
- Интерфейсы в Domain, реализации в Infrastructure

**Пример:**

```python
# Domain интерфейс
class ResumeRepositoryPort(ABC):
    @abstractmethod
    async def create(self, resume: Resume) -> Resume:
        pass

# Infrastructure реализация
class ResumeRepository(ResumeRepositoryPort):
    async def create(self, resume: Resume) -> Resume:
        # Реализация с SQLAlchemy
        pass
```

**Преимущества:**
- Легко тестировать (можно использовать моки)
- Можно заменить БД без изменения бизнес-логики

## Unit of Work Pattern

**Назначение:** Управление транзакциями и координация репозиториев.

**Применение:**
- Все операции с БД через UnitOfWork
- Гарантирует атомарность операций

**Пример:**

```python
async with unit_of_work:
    resume = await unit_of_work.resume_repository.create(resume)
    match = await unit_of_work.match_repository.create(match)
    await unit_of_work.commit()
```

**Преимущества:**
- Централизованное управление транзакциями
- Все репозитории используют одну сессию

## Factory Pattern

**Назначение:** Создание сложных объектов и зависимостей.

**Применение:**
- Фабрики в Application слое
- Создание Use Cases с зависимостями

**Пример:**

```python
def create_search_and_get_filtered_vacancy_list_usecase(
    unit_of_work: UnitOfWorkPort,
    hh_client: HHClientPort,
) -> SearchAndGetFilteredVacancyListUseCase:
    return SearchAndGetFilteredVacancyListUseCase(
        resume_repository=unit_of_work.resume_repository,
        hh_client=hh_client,
        # ...
    )
```

## Strategy Pattern

**Назначение:** Различные алгоритмы для одной задачи.

**Применение:**
- Разные агенты для разных задач (фильтрация, генерация)
- Разные стратегии аутентификации

**Пример:**

```python
# Интерфейс стратегии
class LLMAgentPort(ABC):
    @abstractmethod
    async def process(self, data: dict) -> dict:
        pass

# Разные реализации
class VacancyFilterAgent(LLMAgentPort):
    async def process(self, data: dict) -> dict:
        # Стратегия фильтрации
        pass

class CoverLetterGeneratorAgent(LLMAgentPort):
    async def process(self, data: dict) -> dict:
        # Стратегия генерации
        pass
```

## Observer Pattern

**Назначение:** Уведомление о событиях.

**Применение:**
- Event Bus для событий
- WebSocket уведомления
- Telegram уведомления

**Пример:**

```python
# Публикация события
event_publisher.publish(VacancyResponseCreatedEvent(response))

# Подписчики получают уведомление
@event_subscriber(VacancyResponseCreatedEvent)
async def handle_response_created(event):
    # Отправка уведомления
    pass
```

## Dependency Injection

**Назначение:** Внедрение зависимостей вместо их создания.

**Применение:**
- FastAPI dependencies
- Конструкторы Use Cases
- Конструкторы Services

**Пример:**

```python
# FastAPI dependency
def get_unit_of_work() -> UnitOfWorkPort:
    return UnitOfWork(session_factory)

# Использование в роутере
@router.post("")
async def create_resume(
    unit_of_work: UnitOfWorkPort = Depends(get_unit_of_work),
):
    pass
```

## Связанные разделы

- [Чистая архитектура](clean-architecture.md) — архитектурные принципы
- [Описание слоев](layers.md) — структура слоев
