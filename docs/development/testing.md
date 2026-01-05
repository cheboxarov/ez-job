# Тестирование

Руководство по тестированию в проекте "Вкатился".

## Типы тестов

### Unit тесты

Тестирование отдельных компонентов изолированно.

**Пример:**

```python
# tests/domain/test_create_resume_use_case.py
import pytest
from domain.use_cases.create_resume import CreateResumeUseCase
from domain.entities.resume import Resume

class MockResumeRepository:
    async def create(self, resume: Resume) -> Resume:
        return resume

@pytest.mark.asyncio
async def test_create_resume():
    repository = MockResumeRepository()
    use_case = CreateResumeUseCase(repository)
    
    resume = await use_case.execute(
        user_id=uuid4(),
        content="Test resume"
    )
    
    assert resume.content == "Test resume"
```

### Integration тесты

Тестирование взаимодействия компонентов.

**Пример:**

```python
# tests/integration/test_resume_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resume_api(client: AsyncClient, token: str):
    response = await client.post(
        "/api/resumes",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Test resume"}
    )
    
    assert response.status_code == 201
    assert response.json()["content"] == "Test resume"
```

### E2E тесты

Тестирование полных сценариев использования.

## Написание тестов

### Структура тестов

```
tests/
├── domain/
│   └── test_use_cases/
├── infrastructure/
│   └── test_repositories/
├── integration/
│   └── test_api/
└── conftest.py
```

### Моки и стабы

Используйте моки для изоляции тестируемых компонентов:

```python
from unittest.mock import AsyncMock, Mock

# Мок репозитория
mock_repository = AsyncMock()
mock_repository.create.return_value = Resume(...)

# Мок HTTP клиента
mock_client = Mock()
mock_client.get.return_value = {"data": "..."}
```

## Запуск тестов

### Backend

```bash
cd backend
pytest tests/
```

### Frontend

```bash
cd frontend
npm test
```

### С покрытием

```bash
# Backend
pytest --cov=backend tests/

# Frontend
npm test -- --coverage
```

## Покрытие кода

Цель: **80%+ покрытие** для критичных компонентов.

Проверка покрытия:
```bash
pytest --cov=backend --cov-report=html tests/
```

## Связанные разделы

- [Добавление фич](adding-features.md) — разработка с тестами
