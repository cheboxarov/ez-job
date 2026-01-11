# AI агенты

Документация AI агентов для работы с LLM в системе "AutoOffer".

## Обзор агентов

### Vacancy Filter Agent

**Назначение:** Фильтрация вакансий по релевантности резюме.

**Как работает:**

1. Получает резюме и список вакансий
2. Формирует промпт для LLM с описанием резюме и вакансий
3. Отправляет запрос в LLM
4. Получает оценку релевантности для каждой вакансии
5. Возвращает отфильтрованный список вакансий

**Использование:**

```python
agent = VacancyFilterAgent(config.openai, unit_of_work=uow)
filtered = await agent.filter_vacancies(resume, vacancies, user_id=user_id)
```

### Cover Letter Generator Agent

**Назначение:** Генерация сопроводительных писем для вакансий.

**Как работает:**

1. Получает резюме и описание вакансии
2. Формирует промпт для LLM
3. Отправляет запрос в LLM
4. Получает сгенерированное письмо
5. Возвращает готовое письмо

**Использование:**

```python
agent = CoverLetterGeneratorAgent(config.openai, unit_of_work=uow)
letter = await agent.generate(resume, vacancy_description, user_id=user_id)
```

### Messages Agent

**Назначение:** Анализ сообщений в чатах и генерация ответов.

**Как работает:**

1. Получает историю чата
2. Анализирует контекст через LLM
3. Генерирует предложения по ответам
4. Создает действия агента

**Использование:**

```python
agent = MessagesAgent(config.openai, unit_of_work=uow)
actions = await agent.analyze_chats_and_generate_responses(
    chats=chats, resume=resume, user_id=user_id
)
```

### Resume Evaluator Agent

**Назначение:** Оценка резюме и предоставление рекомендаций.

**Как работает:**

1. Получает текст резюме
2. Анализирует резюме через LLM
3. Выставляет оценку
4. Предоставляет обратную связь и рекомендации

**Использование:**

```python
agent = ResumeEvaluatorAgent(config.openai, unit_of_work=uow)
evaluation = await agent.evaluate(resume, user_id=user_id)
```

### Vacancy Test Agent

**Назначение:** Генерация ответов на тестовые задания вакансий.

**Как работает:**

1. Получает тестовое задание из вакансии
2. Анализирует задание через LLM
3. Генерирует ответы на вопросы
4. Возвращает готовые ответы

**Использование:**

```python
agent = VacancyTestAgent(config.openai, unit_of_work=uow)
answers = await agent.generate_test_answers(test, resume, user_id=user_id)
```

### Resume Edit DeepAgent

**Назначение:** Интерактивное редактирование резюме с планированием, под-агентами и стримингом.

**Как работает:**

1. Главный DeepAgent строит todo-план и управляет статусами задач.
2. Делегирует выполнение под-агентам:
   - question-agent — уточняющие вопросы
   - patch-agent — генерация патчей
   - chat-agent — общий диалог
3. Возвращает структурированный результат (questions/patches/warnings) и обновленный план.

**Использование:**

```python
from infrastructure.agents.resume_edit.deepagents.resume_edit_deep_agent import (
    ResumeEditDeepAgentAdapter,
)

agent = ResumeEditDeepAgentAdapter(config.openai)
```

**Формат todo-плана:**

```json
[
  {
    "id": "todo-1",
    "title": "Уточнить детали опыта",
    "status": "in_progress",
    "description": "Собрать цифры, метрики, стек"
  }
]
```

## Интеграция с LLM

Все агенты наследуются от `BaseAgent`, который предоставляет единый интерфейс для работы с LLM через OpenAI-совместимое API (BotHub).

### Логирование вызовов

Все вызовы LLM автоматически логируются в таблицу `llm_calls` с полной информацией:
- Промпт и ответ
- Метрики производительности (время выполнения, токены, размер ответа)
- Информация об ошибках (если были)
- Контекст вызова (use_case, resume_id, vacancy_id и т.д.)
- Каждая попытка retry логируется отдельно с общим `call_id`

Логирование происходит автоматически на уровне `BaseAgent._call_llm_with_retry` и не требует дополнительной настройки в агентах.

## Настройка агентов

### Конфигурация LLM

Настраивается через переменные окружения:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://bothub.chat/api/v2/openai/v1
OPENAI_MODEL=gpt-oss-120b:exacto
OPENAI_MIN_CONFIDENCE=0.0
```

### Параметры генерации

Каждый агент может иметь свои параметры:
- Temperature
- Max tokens
- Top P

## Связанные разделы

- [Архитектура](../architecture/layers.md) — структура системы
- [Development](../development/adding-features.md) — добавление новых агентов
