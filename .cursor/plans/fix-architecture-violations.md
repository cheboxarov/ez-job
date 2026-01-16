# План: Исправление архитектурных нарушений Clean Architecture

## Проблема

В бэкенде обнаружено 13 архитектурных нарушений Clean Architecture:
- 6 критических
- 5 major
- 2 minor

Главная проблема: **Domain слой зависит от Infrastructure**, что нарушает Dependency Inversion Principle.

---

## Фаза 1: Создание недостающих портов (интерфейсов)

### 1.1 Порт для HH клиента с обновлением cookies

**Файл:** `domain/interfaces/hh_client_with_cookie_update_port.py`

```python
from abc import ABC, abstractmethod
from domain.interfaces.hh_client_port import HHClientPort

class HHClientWithCookieUpdatePort(HHClientPort):
    """Порт для HH клиента с автоматическим обновлением cookies."""
    pass
```

**Зачем:** Сейчас use cases импортируют `HHHttpClientWithCookieUpdate` напрямую из infrastructure.

### 1.2 Порт для LLM агентов

**Файл:** `domain/interfaces/llm_agent_port.py`

```python
from abc import ABC, abstractmethod
from typing import Any

class LLMAgentPort(ABC):
    @abstractmethod
    async def execute(self, prompt: str, **kwargs) -> Any: ...

class CoverLetterGeneratorPort(LLMAgentPort):
    @abstractmethod
    async def generate(self, resume: Resume, vacancy: Vacancy) -> str: ...

class ResumeEvaluatorPort(LLMAgentPort):
    @abstractmethod
    async def evaluate(self, resume: Resume, vacancy: Vacancy) -> Evaluation: ...
```

### 1.3 Порт для Event Publisher

**Файл:** `domain/interfaces/event_publisher_port.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID

class EventPublisherPort(ABC):
    @abstractmethod
    async def publish(self, user_id: UUID, event: WebSocketEvent) -> None: ...
```

---

## Фаза 2: Рефакторинг Use Cases

### 2.1 Удаление импортов из Infrastructure

**Затронутые файлы (11 штук):**
- `domain/use_cases/fetch_hh_resume_detail.py`
- `domain/use_cases/fetch_hh_resumes.py`
- `domain/use_cases/fetch_user_chats.py`
- `domain/use_cases/fetch_vacancies.py`
- `domain/use_cases/fetch_chat_detail.py`
- `domain/use_cases/fetch_chats_details.py`
- `domain/use_cases/mark_chat_message_read.py`
- `domain/use_cases/respond_to_vacancy.py`
- `domain/use_cases/get_areas.py`
- `domain/use_cases/get_vacancy_list.py`
- `domain/use_cases/send_chat_message.py`

**Изменение:**

До:
```python
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate

class FetchHHResumeDetailUseCase:
    def __init__(self, hh_client: HHClientPort, ...):
        ...

    async def execute(self, user_id: UUID, ...):
        client = HHHttpClientWithCookieUpdate(self._hh_client, user_id, update_cookies_uc)
```

После:
```python
from domain.interfaces.hh_client_port import HHClientPort

class FetchHHResumeDetailUseCase:
    def __init__(self, hh_client: HHClientPort, ...):
        # Клиент уже должен быть сконфигурирован с cookie update
        self._hh_client = hh_client

    async def execute(self, user_id: UUID, ...):
        # Используем клиент напрямую
        return await self._hh_client.fetch_resume_detail(...)
```

### 2.2 Рефакторинг process_auto_replies.py

**Проблемы:**
1. Импорт `create_session_factory` из infrastructure
2. Импорт `UserHhAuthDataRepository` напрямую
3. Импорт `create_event_publisher` из application
4. Использование `hasattr()` для duck typing

**Решение:**

```python
# До
from infrastructure.database.session import create_session_factory
from infrastructure.database.repositories.user_hh_auth_data_repository import UserHhAuthDataRepository
from config import DatabaseConfig

class ProcessAutoRepliesUseCase:
    def __init__(self, ..., database_config: DatabaseConfig | None = None):
        self._database_config = database_config

# После
from domain.interfaces.unit_of_work_port import UnitOfWorkPort

class ProcessAutoRepliesUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWorkPort,
        standalone_unit_of_work_factory: Callable[[], UnitOfWorkPort],
        event_publisher: EventPublisherPort,
        ...
    ):
        self._uow = unit_of_work
        self._create_standalone_uow = standalone_unit_of_work_factory
        self._event_publisher = event_publisher
```

### 2.3 Удаление SQLAlchemy из Domain

**Файлы:**
- `domain/use_cases/save_resume_evaluation.py`
- `domain/use_cases/get_filtered_vacancy_list_with_cache.py`
- `domain/use_cases/get_filtered_vacancies_with_cache.py`

**Решение для IntegrityError:**

```python
# domain/exceptions/repository_exceptions.py
class DuplicateEntityError(Exception):
    """Сущность уже существует."""
    pass

# infrastructure/database/repositories/base_repository.py
from sqlalchemy.exc import IntegrityError
from domain.exceptions.repository_exceptions import DuplicateEntityError

class BaseRepository:
    async def _execute_with_error_handling(self, operation):
        try:
            return await operation()
        except IntegrityError:
            raise DuplicateEntityError()
```

**Решение для async_sessionmaker:**

```python
# До
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

class GetFilteredVacanciesWithCacheUseCase:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], ...):
        ...

# После
from domain.interfaces.unit_of_work_port import UnitOfWorkPort
from typing import Callable

class GetFilteredVacanciesWithCacheUseCase:
    def __init__(self, create_unit_of_work: Callable[[], UnitOfWorkPort], ...):
        self._create_uow = create_unit_of_work
```

### 2.4 Перенос login_trust_flags в Domain

**Файлы:**
- `domain/use_cases/generate_otp.py`
- `domain/use_cases/login_by_code.py`

**Решение:**

```python
# Переместить application/utils/login_trust_flags_generator.py
# в domain/utils/login_trust_flags_generator.py

# Или создать порт если это внешняя зависимость
```

---

## Фаза 3: Рефакторинг Factories

### 3.1 Фабрика для HH клиента с cookies

**Файл:** `application/factories/hh_client_factory.py`

```python
from infrastructure.clients.hh_client import HHHttpClient
from infrastructure.clients.hh_client_with_cookie_update import HHHttpClientWithCookieUpdate

def create_hh_client_with_cookie_update(
    config: HHConfig,
    user_id: UUID,
    update_cookies_uc: UpdateUserCookiesUseCase,
) -> HHClientPort:
    base_client = HHHttpClient(config)
    return HHHttpClientWithCookieUpdate(base_client, user_id, update_cookies_uc)
```

### 3.2 Централизованная фабрика Use Cases

**Файл:** `application/factories/use_case_factory.py`

```python
class UseCaseFactory:
    def __init__(self, config: AppConfig, unit_of_work: UnitOfWorkPort):
        self._config = config
        self._uow = unit_of_work

    def create_fetch_hh_resume_detail(self, user_id: UUID) -> FetchHHResumeDetailUseCase:
        hh_client = create_hh_client_with_cookie_update(
            self._config.hh,
            user_id,
            UpdateUserCookiesUseCase(self._uow.user_hh_auth_data_repository)
        )
        return FetchHHResumeDetailUseCase(hh_client)

    def create_evaluate_resume_with_cache(self) -> EvaluateResumeWithCacheUseCase:
        agent = ResumeEvaluatorAgent(self._config.openai, self._uow)
        return EvaluateResumeWithCacheUseCase(
            GetResumeEvaluationFromCacheUseCase(self._uow.resume_evaluation_repository),
            EvaluateResumeUseCase(agent),
            SaveResumeEvaluationUseCase(self._uow.resume_evaluation_repository),
        )
```

---

## Фаза 4: Рефакторинг Presentation Layer

### 4.1 Убрать inline создание Use Cases из роутеров

**Файл:** `presentation/routers/resumes_router.py`

До:
```python
@router.post("/evaluate")
async def evaluate_resume(...):
    from domain.use_cases.evaluate_resume import EvaluateResumeUseCase
    from infrastructure.agents.resume_evaluator_agent import ResumeEvaluatorAgent

    config = load_config()
    agent = ResumeEvaluatorAgent(config.openai, unit_of_work=unit_of_work)
    evaluate_resume_uc = EvaluateResumeUseCase(agent)
```

После:
```python
# presentation/dependencies.py
def get_use_case_factory(
    config: AppConfig = Depends(get_config),
    uow: UnitOfWorkPort = Depends(get_unit_of_work),
) -> UseCaseFactory:
    return UseCaseFactory(config, uow)

# presentation/routers/resumes_router.py
@router.post("/evaluate")
async def evaluate_resume(
    ...,
    factory: UseCaseFactory = Depends(get_use_case_factory),
):
    use_case = factory.create_evaluate_resume_with_cache()
    return await use_case.execute(...)
```

### 4.2 Убрать прямые вызовы Repository из роутеров

**Файл:** `presentation/routers/resumes_router.py:185-187`

До:
```python
settings = await unit_of_work.resume_filter_settings_repository.get_by_resume_id(resume_id)
```

После:
```python
# Через сервис
settings = await resumes_service.get_filter_settings(resume_id)
```

---

## Фаза 5: Удаление duck typing

### 5.1 Заменить hasattr на явные интерфейсы

**Файлы:**
- `domain/use_cases/process_auto_replies.py`
- `domain/use_cases/generate_test_answers.py`

До:
```python
if hasattr(self._cover_letter_generator, 'set_unit_of_work'):
    self._cover_letter_generator.set_unit_of_work(llm_unit_of_work_letter)
```

После:
```python
# Вариант 1: Передавать UoW через конструктор
class CoverLetterAgent(CoverLetterGeneratorPort):
    def __init__(self, config: OpenAIConfig, unit_of_work: UnitOfWorkPort):
        ...

# Вариант 2: Создать отдельный интерфейс
class UnitOfWorkAwarePort(ABC):
    @abstractmethod
    def set_unit_of_work(self, uow: UnitOfWorkPort) -> None: ...

class CoverLetterAgent(CoverLetterGeneratorPort, UnitOfWorkAwarePort):
    ...
```

---

## Фаза 6: Тестирование

### 6.1 Unit тесты для портов

```python
# tests/domain/test_use_cases.py
class TestFetchHHResumeDetailUseCase:
    async def test_execute_calls_client(self):
        mock_client = Mock(spec=HHClientPort)
        use_case = FetchHHResumeDetailUseCase(mock_client)

        await use_case.execute(user_id=uuid4(), resume_id="123")

        mock_client.fetch_resume_detail.assert_called_once()
```

### 6.2 Интеграционные тесты

```python
# tests/integration/test_factories.py
class TestUseCaseFactory:
    async def test_creates_configured_use_case(self):
        factory = UseCaseFactory(config, unit_of_work)
        use_case = factory.create_fetch_hh_resume_detail(user_id)

        assert isinstance(use_case, FetchHHResumeDetailUseCase)
```

---

## Порядок выполнения

| Шаг | Фаза | Описание | Риск |
|-----|------|----------|------|
| 1 | 1.1-1.3 | Создать недостающие порты | Низкий |
| 2 | 2.4 | Перенести utils в domain | Низкий |
| 3 | 2.3 | Создать доменные исключения | Низкий |
| 4 | 3.1-3.2 | Создать фабрики | Средний |
| 5 | 2.1 | Рефакторинг use cases (HH client) | Высокий |
| 6 | 2.2 | Рефакторинг process_auto_replies | Высокий |
| 7 | 4.1-4.2 | Рефакторинг presentation | Средний |
| 8 | 5.1 | Удаление duck typing | Средний |
| 9 | 6.1-6.2 | Тестирование | Низкий |

---

## Файлы для изменения

### Domain layer (создать)
- `domain/interfaces/hh_client_with_cookie_update_port.py`
- `domain/interfaces/llm_agent_port.py`
- `domain/interfaces/event_publisher_port.py`
- `domain/exceptions/repository_exceptions.py`

### Domain layer (изменить)
- `domain/use_cases/fetch_hh_resume_detail.py`
- `domain/use_cases/fetch_hh_resumes.py`
- `domain/use_cases/fetch_user_chats.py`
- `domain/use_cases/fetch_vacancies.py`
- `domain/use_cases/fetch_chat_detail.py`
- `domain/use_cases/fetch_chats_details.py`
- `domain/use_cases/mark_chat_message_read.py`
- `domain/use_cases/respond_to_vacancy.py`
- `domain/use_cases/get_areas.py`
- `domain/use_cases/get_vacancy_list.py`
- `domain/use_cases/send_chat_message.py`
- `domain/use_cases/process_auto_replies.py`
- `domain/use_cases/save_resume_evaluation.py`
- `domain/use_cases/get_filtered_vacancy_list_with_cache.py`
- `domain/use_cases/get_filtered_vacancies_with_cache.py`
- `domain/use_cases/generate_otp.py`
- `domain/use_cases/login_by_code.py`
- `domain/use_cases/generate_test_answers.py`

### Domain layer (переместить)
- `application/utils/login_trust_flags_generator.py` → `domain/utils/`

### Application layer (создать)
- `application/factories/hh_client_factory.py`
- `application/factories/use_case_factory.py`

### Infrastructure layer (изменить)
- `infrastructure/database/repositories/base_repository.py`

### Presentation layer (изменить)
- `presentation/dependencies.py`
- `presentation/routers/resumes_router.py`

---

## Ожидаемый результат

После выполнения плана:

1. **Domain слой** не будет иметь импортов из infrastructure и application
2. **Use Cases** будут получать все зависимости через конструктор
3. **Фабрики** будут централизованно создавать сложные объекты
4. **Презентационный слой** будет использовать DI для получения use cases
5. **Тесты** смогут легко мокать зависимости через интерфейсы

```
Domain ←── Application ←── Presentation
   ↑              ↑
   │              │
   └── Infrastructure (implements ports)
```
