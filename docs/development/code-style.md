# Стиль кода

Стандарты кодирования для проекта "AutoOffer".

## Python

### PEP 8

Следуйте [PEP 8](https://pep8.org/) с некоторыми дополнениями.

### Типизация

Используйте type hints везде:

```python
def process_data(data: dict[str, int]) -> list[str]:
    return [str(v) for v in data.values()]
```

### Docstrings

Используйте Google style docstrings:

```python
def create_resume(user_id: UUID, content: str) -> Resume:
    """Создать резюме для пользователя.
    
    Args:
        user_id: UUID пользователя.
        content: Текст резюме.
    
    Returns:
        Созданное резюме.
    
    Raises:
        ValueError: Если резюме невалидно.
    """
    pass
```

### Именование

- **Классы:** `PascalCase` — `ResumeRepository`
- **Функции/методы:** `snake_case` — `create_resume`
- **Константы:** `UPPER_SNAKE_CASE` — `MAX_RETRIES`
- **Переменные:** `snake_case` — `user_id`

## TypeScript

### ESLint

Следуйте правилам из `frontend/eslint.config.js`.

### Форматирование

Используйте Prettier с настройками проекта.

### Именование

- **Компоненты:** `PascalCase` — `ResumeCard`
- **Функции:** `camelCase` — `createResume`
- **Константы:** `UPPER_SNAKE_CASE` — `API_BASE_URL`
- **Переменные:** `camelCase` — `userId`

## Комментарии

### Когда комментировать

- Сложная бизнес-логика
- Неочевидные решения
- TODO/FIXME

### Когда НЕ комментировать

- Очевидный код
- Повторение того, что уже в коде

## Примеры

### Хороший код

```python
async def create_resume(
    user_id: UUID,
    content: str,
) -> Resume:
    """Создать резюме с валидацией."""
    if not content.strip():
        raise ValueError("Resume content cannot be empty")
    
    resume = Resume(id=uuid4(), user_id=user_id, content=content)
    return await repository.create(resume)
```

### Плохой код

```python
def cr(u, c):  # Плохие имена
    r = Resume(u, c)  # Неочевидные переменные
    return r  # Нет валидации
```

## Связанные разделы

- [Добавление фич](adding-features.md) — разработка
- [Git workflow](git-workflow.md) — процесс работы
