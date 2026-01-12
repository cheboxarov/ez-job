# План: Автоматическая передача resume_text в sub-agents

## Проблема

Сейчас в промпте главного DeepAgent написано:

> "При вызове `task` ты ОБЯЗАН передать `resume_text` из `state["resume_text"]`"

Это означает, что LLM оркестратора должен **генерировать весь текст резюме заново** при каждом вызове sub-agent tool:

```json
{
  "tool": "generate_resume_questions",
  "args": {
    "resume_text": "Иван Иванов\nPython разработчик\n...(весь текст)...",
    "user_message": "Добавь достижения",
    ...
  }
}
```

**Проблемы:**

1. **Траты токенов** — LLM генерирует сотни/тысячи токенов для копирования резюме
2. **Искажение текста** — LLM может случайно изменить/потерять части резюме
3. **Ненадёжность** — если LLM забудет передать resume_text, sub-agent не сможет работать

---

## Решение

Создать обёртки для tools, которые **автоматически инжектят resume_text из LangGraph state**, чтобы оркестратору не нужно было его передавать явно.

**До:**

```
Оркестратор: task(resume_text="<весь текст>", user_message="...")
```

**После:**

```
Оркестратор: task(user_message="...")
Tool wrapper: автоматически добавляет resume_text из state
```

---

## Архитектура решения

### Текущая архитектура

```
DeepAgent (оркестратор)
    ↓
    tool call: generate_resume_questions(resume_text="...", user_message="...")
    ↓
Tool function: принимает resume_text как аргумент
```

### Новая архитектура

```
DeepAgent (оркестратор)
    ↓
    tool call: generate_resume_questions(user_message="...")  // БЕЗ resume_text
    ↓
StateInjectorWrapper: добавляет resume_text из state["resume_text"]
    ↓
Tool function: получает resume_text автоматически
```

---

## Что нужно сделать

### 1. Создать базовый класс StateInjectorTool

**Файл:** `backend/infrastructure/agents/resume_edit/tools/state_injector.py` (новый)

**Описание:**

- Обёртка для LangChain tools
- Перехватывает вызов tool и добавляет параметры из state
- Конфигурируется: какие параметры инжектить и откуда

**Интерфейс:**

```python
class StateInjectorTool:
    def __init__(
        self,
        original_tool: BaseTool,
        injections: dict[str, str],  # {"resume_text": "resume_text", "user_id": "user_id"}
    ):
        ...

    async def __call__(self, state: dict, **kwargs):
        # Добавить параметры из state в kwargs
        # Вызвать original_tool с расширенными kwargs
        ...
```

### 2. Создать обёртки для существующих tools

**Файлы для изменения:**

- `deepagents_question_tool.py`
- `deepagents_patch_tool.py`

**Что сделать:**

- Создать две версии schema: полную (с resume_text) и сокращённую (без resume_text)
- Обернуть tools в StateInjectorTool
- Экспортировать обёрнутые версии

### 3. Изменить schema для tool inputs

**Сейчас:**

```python
class GenerateQuestionsInput(BaseModel):
    resume_text: str = Field(..., description="Текст резюме.")  # ОБЯЗАТЕЛЬНЫЙ
    user_message: str = Field(...)
    user_id: UUID | None = Field(default=None)
    current_task: dict | None = Field(default=None)
    history: list[dict] | None = Field(default=None)
```

**Нужно:**

```python
class GenerateQuestionsInput(BaseModel):
    # resume_text НЕТ — будет инжектирован автоматически
    user_message: str = Field(...)
    current_task: dict | None = Field(default=None)
    history: list[dict] | None = Field(default=None)
```

### 4. Изменить промпт DeepAgent

**Файл:** `backend/infrastructure/agents/prompts/resume_edit_deep_agent.md`

**Удалить:**

> "При вызове `task` ты ОБЯЗАН передать `resume_text` из `state["resume_text"]`"

**Добавить:**

> "resume_text передаётся автоматически, тебе НЕ нужно его указывать"

**Обновить примеры:**

```json
// Было (НЕПРАВИЛЬНО теперь):
{
  "resume_text": "<ВЗЯТЬ ИЗ state['resume_text']>",
  "user_message": "..."
}

// Стало (ПРАВИЛЬНО):
{
  "user_message": "Добавь достижения в раздел опыта",
  "current_task": {...}
}
```

### 5. Интегрировать обёртки в create_resume_edit_deep_agent

**Файл:** `backend/infrastructure/agents/resume_edit/deepagents/resume_edit_deep_agent.py`

**Что сделать:**

- Импортировать StateInjectorTool
- Обернуть patch_tool и question_tool
- Передать обёрнутые tools в create_deep_agent

### 6. Обновить state_mapper для передачи контекста

**Файл:** `backend/infrastructure/agents/resume_edit/deepagents/state_mapper.py`

**Что сделать:**

- Убедиться что `resume_text` всегда есть в state
- Добавить `user_id` в state если нужно для инжекции

---

## Детали реализации

### StateInjectorTool — примерная структура

```python
from langchain_core.tools import BaseTool
from typing import Any, Callable

class StateInjectorTool(BaseTool):
    """Обёртка для автоматической инжекции параметров из state."""

    name: str
    description: str
    original_tool: BaseTool
    injections: dict[str, str]  # param_name -> state_key

    async def _arun(self, **kwargs) -> Any:
        # Получить state из контекста (RunnableConfig)
        state = self._get_current_state()

        # Инжектировать параметры
        for param_name, state_key in self.injections.items():
            if param_name not in kwargs and state_key in state:
                kwargs[param_name] = state[state_key]

        # Вызвать оригинальный tool
        return await self.original_tool._arun(**kwargs)

    def _get_current_state(self) -> dict:
        # Получить state из LangGraph контекста
        # Использовать RunnableConfig или contextvars
        ...
```

### Альтернатива: использовать LangGraph state injection

LangGraph поддерживает передачу state в tools через `InjectedState`:

```python
from langgraph.prebuilt import InjectedState
from typing import Annotated

@tool
async def generate_resume_questions(
    user_message: str,
    current_task: dict | None = None,
    state: Annotated[dict, InjectedState],  # ← АВТОМАТИЧЕСКИ ИНЖЕКТИТСЯ
) -> dict:
    resume_text = state["resume_text"]  # ← ПОЛУЧАЕМ ИЗ STATE
    ...
```

**Преимущества:**

- Нативная поддержка LangGraph
- Не нужно писать свои обёртки
- Чище архитектура

---

## Порядок выполнения

1. Исследовать поддержку `InjectedState` в используемой версии LangGraph
2. Если поддерживается — использовать нативный подход
3. Если нет — создать StateInjectorTool
4. Обновить схемы входных данных tools (убрать resume_text)
5. Обновить промпт DeepAgent (убрать инструкцию про resume_text)
6. Обновить примеры в промптах
7. Интегрировать в create_resume_edit_deep_agent
8. Тестирование

---

## Файлы для изменения

| Файл | Что изменить |

|------|--------------|

| `tools/state_injector.py` | Создать новый файл с обёрткой |

| `tools/deepagents_question_tool.py` | Убрать resume_text из schema, добавить InjectedState |

| `tools/deepagents_patch_tool.py` | Убрать resume_text из schema, добавить InjectedState |

| `prompts/resume_edit_deep_agent.md` | Убрать инструкцию про передачу resume_text |

| `deepagents/resume_edit_deep_agent.py` | Интегрировать обёртки |

---

## Риски

1. **Совместимость LangGraph** — нужно проверить версию и поддержку InjectedState
2. **Отладка** — сложнее понять откуда пришли данные при implicit injection
3. **Документация** — нужно обновить все промпты и примеры

---

## Ожидаемый результат

**До:**

- Оркестратор генерирует ~500 токенов для копирования резюме
- Возможны ошибки и искажения текста
- Промпт содержит сложные инструкции

**После:**

- Оркестратор генерирует ~50 токенов (только user_message и current_task)
- resume_text передаётся без изменений
- Промпт проще и понятнее