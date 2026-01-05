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
agent = VacancyFilterAgent(llm_client)
filtered = await agent.filter_vacancies(resume, vacancies)
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
agent = CoverLetterGeneratorAgent(llm_client)
letter = await agent.generate_cover_letter(resume, vacancy)
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
agent = MessagesAgent(llm_client)
actions = await agent.analyze_chat(chat)
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
agent = ResumeEvaluatorAgent(llm_client)
evaluation = await agent.evaluate_resume(resume)
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
agent = VacancyTestAgent(llm_client)
answers = await agent.generate_answers(vacancy_test)
```

## Интеграция с LLM

Все агенты используют единый интерфейс для работы с LLM:

```python
class LLMClientPort(ABC):
    @abstractmethod
    async def chat_completion(self, messages: list[dict]) -> dict:
        pass
```

Реализация использует OpenAI-совместимое API (BotHub).

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
