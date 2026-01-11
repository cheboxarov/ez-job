# План: интерактивное редактирование резюме в деталке

## Цели и ограничения (MVP)
- Добавить вкладку в детальной странице резюме с интерактивным чатом и предпросмотром правок.
- Агент меняет только конкретные строки/фразы (patch-операции), а не переписывает все резюме целиком.
- Агент обязан следовать правилам из `docs/hh/resume_rules.md` и тем же принципам, что использует `ResumeEvaluatorAgent`.
- Агент задает уточняющие вопросы при нехватке данных (метрики, проекты, стек, контекст).
- Сохранение только на фронте (мок): изменения живут в состоянии страницы и сбрасываются при перезагрузке.
- Работаем только с текстовым резюме (контент из HH).
- Без реальных запросов в HH на сохранение (до отдельного этапа интеграции).

## Гипотеза работы (user flow)
1. Пользователь открывает `/resumes/:id` и переключается на вкладку "Редактирование".
2. Слева чат: пользователь пишет "Улучши блок опыта в компании X".
3. Бэкенд получает: текущий текст резюме, сообщение пользователя, краткую историю диалога.
4. LLM-оркестратор:
   - анализирует резюме и правила HH,
   - формирует список уточняющих вопросов (если надо),
   - предлагает patch-операции (замена/вставка/удаление строк).
5. Фронтенд применяет patch локально и показывает дифф/подсветку правок в правой колонке.
6. Пользователь подтверждает/отклоняет изменения. "Сохранить" пока работает как фиксация в состоянии.
7. Повторный цикл: ответы пользователя на вопросы -> новые patch-операции.

## Детализация поведения агента
- Режим "диалог": если не хватает метрик, контекста, стека, агент задает вопросы до генерации правок.
- Режим "правка": если данных достаточно, агент сразу предлагает правки и короткое объяснение.
- Агент не добавляет сомнительные метрики: если нет цифр, предлагает варианты формулировок и просит подтверждение.
- Агент запрещает длинное тире и шаблонные формулировки из баз "накрутки".
- Агент избегает переписывания целых секций: максимум N% строк или ограничение на размер patch.

## Архитектура по Clean Architecture (куда что кладем)

### Domain
- Сущности:
  - `ResumeEditPatch` (type: replace/insert/delete, start_line, end_line, new_text, reason).
  - `ResumeEditResult` (assistant_message, questions, patches, warnings).
  - (опционально) `ResumeEditSession` для истории диалога.
- Порты:
  - `ResumeEditorPort` (generate_edits(resume_text, user_message, history, user_id) -> ResumeEditResult).
  - `ResumeEditSessionRepositoryPort` (если решим хранить историю на бэке).
- Use case:
  - `GenerateResumeEditsUseCase` (валидации + вызов ResumeEditorPort).
  - (опционально) `ApplyResumePatchesUseCase` для серверной валидации/применения patch в будущем.

### Application
- `ResumeEditService` (оркестратор):
  - Загружает резюме через `GetResumeUseCase`.
  - Передает контент и сообщение в `GenerateResumeEditsUseCase`.
  - Возвращает DTO для фронта.
- (опционально) `ResumeEditSessionService` для хранения/обновления истории.
  - (опционально) `ResumeEditPreviewService` если потребуется серверный предпросмотр diff.

### Infrastructure
- DeepAgents (LangGraph) в `infrastructure/agents/resume_edit/deepagents/`:
  - главный DeepAgent (todo list + task tool).
  - sub-agents: question-agent, patch-agent, chat-agent.
- Инструменты (tools) для агентов:
  - `extract_sections` (выделение блоков "О себе", "Опыт", "Навыки").
  - `rule_check` (прогон правил из `docs/hh/resume_rules.md`).
  - `build_patch` (генерация line-based операций).
  - `validate_patch` (запрет на переписывание всего резюме: лимит на % измененных строк).
  - `question_generator` (уточняющие вопросы про метрики, стек, контекст).
- Лимиты и правила:
  - max_changed_lines_percent (например 20-30%).
  - max_patch_items (например 10-15).
  - запрет на массовую замену, если user_message про маленький блок.
- Повторно использовать правила из `docs/hh/resume_rules.md` и промпт-правила `ResumeEvaluatorAgent`.
  - Лучше вынести правила в общий источник (например, `infrastructure/agents/prompts/resume_rules.md`).
- Логирование LLM вызовов через `LlmCall` (callback LangChain -> репозиторий).

### Presentation (API)
- Новый endpoint, например:
  - `POST /api/resumes/{resume_id}/edit`
    - request: `{ message, resume_text, history }`
    - response: `{ assistant_message, questions[], patches[], warnings[] }`
- DTO для patch-операций и сообщений.
  - `ResumeEditPatchResponse` (type, start_line, end_line, new_text, reason).
  - `ResumeEditQuestionResponse` (id, text, required).
  - `ResumeEditResultResponse`.

### Frontend
- Новая вкладка на `frontend/src/pages/ResumeDetailPage.tsx`:
  - добавить key `edit` и роут `/resumes/:id/edit`.
- Новая страница `ResumeEditPage`:
  - layout: слева чат, справа резюме.
  - чат отображает вопросы/ответы агента.
  - блок резюме показывает подсветку изменений (diff view).
  - кнопки: "Применить", "Отклонить", "Сохранить (локально)".
  - состояние в памяти (zustand/store) без сохранения в БД.
- UI детали:
  - лента сообщений с типами: user / assistant / question / system.
  - панель "Изменения" с кратким списком patch-операций.
  - подсветка строк и маркеры вставок/удалений.
  - кнопки "Отменить последнее", "Сбросить все".

## План работ (итерации)
1. Дизайн формата patch-операций и правил валидации:
   - выбрать line-based операции или anchors.
   - определить лимиты: % строк, max_patches, max_chars.
2. Domain:
   - сущности `ResumeEditPatch`, `ResumeEditResult`, `ResumeEditQuestion`.
   - порт `ResumeEditorPort`.
   - use case `GenerateResumeEditsUseCase`.
3. Infrastructure:
   - базовый промпт агента с правилами `docs/hh/resume_rules.md`.
   - LangChain агент-оркестратор (planner -> patch -> reviewer).
   - инструменты: extract_sections, build_patch, validate_patch, question_generator.
   - fallback: если агент не уверен, возвращать вопросы вместо patch.
4. Application:
   - `ResumeEditService` с зависимостями на UoW и use case.
   - логирование LLM вызовов через `BaseAgent`/callback.
5. Presentation:
   - новый router endpoint `/api/resumes/{resume_id}/edit`.
   - DTO request/response, валидация входа (message, history size).
6. Frontend:
   - вкладка "Редактирование".
   - страница с чат-интерфейсом и preview.
   - локальный store для draft и applied patches.
7. Тесты:
   - юнит: patch apply/rollback, validate_patch.
   - интеграционные: use case -> port mock.
   - фронт: snapshot/interaction тесты для diff панели.

## Риски и вопросы
- Как стабильно привязывать patch к строкам (line numbers vs. якоря текста).
- Ограничение переписывания всего резюме: какой порог считать допустимым.
- Где хранить историю диалога (пока на фронте, потом сервис/БД).
- Нужны ли стриминг-ответы (можно позже через WebSocket).
- Как аккуратно выделять секции в сыром тексте HH (формат не всегда стабильный).
- Нужен ли отдельный "словарь" допустимых формулировок и фильтр шаблонов.
