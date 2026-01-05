# Потоки данных

Описание основных потоков данных в системе "Вкатился".

## Создание резюме

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant UseCase
    participant Repository
    participant DB
    
    Client->>Router: POST /api/resumes
    Router->>UseCase: CreateResumeUseCase.execute()
    UseCase->>UseCase: Validate resume
    UseCase->>Repository: create(resume)
    Repository->>DB: INSERT INTO resumes
    DB-->>Repository: ResumeModel
    Repository-->>UseCase: Resume entity
    UseCase-->>Router: Resume
    Router->>Client: ResumeResponse
```

## Поиск и фильтрация вакансий

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant UseCase
    participant HHClient
    participant Agent
    participant Repository
    participant DB
    
    Client->>Router: GET /api/resumes/{id}/vacancies
    Router->>UseCase: SearchAndGetFilteredVacancyListUseCase.execute()
    UseCase->>HHClient: get_vacancies()
    HHClient->>HHClient: HTTP request to HH API
    HHClient-->>UseCase: List[Vacancy]
    UseCase->>Agent: filter_vacancies(resume, vacancies)
    Agent->>Agent: LLM request
    Agent-->>UseCase: Filtered vacancies
    UseCase->>Repository: save_matches()
    Repository->>DB: INSERT matches
    UseCase-->>Router: FilteredVacancyList
    Router->>Client: VacancyListResponse
```

## Генерация сопроводительного письма

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant UseCase
    participant Agent
    participant LLM
    
    Client->>Router: POST /api/vacancies/{id}/cover-letter
    Router->>UseCase: GenerateCoverLetterUseCase.execute()
    UseCase->>UseCase: Get resume and vacancy
    UseCase->>Agent: generate_cover_letter(resume, vacancy)
    Agent->>LLM: Generate letter prompt
    LLM-->>Agent: Cover letter text
    Agent-->>UseCase: Cover letter
    UseCase-->>Router: CoverLetterResponse
    Router->>Client: Cover letter
```

## Автоотклик на вакансию

```mermaid
sequenceDiagram
    participant Worker
    participant UseCase
    participant HHClient
    participant Agent
    participant Repository
    participant DB
    participant WebSocket
    
    Worker->>UseCase: ProcessAutoRepliesUseCase.execute()
    UseCase->>Repository: get_pending_matches()
    Repository->>DB: SELECT matches
    DB-->>Repository: Matches
    UseCase->>Agent: generate_cover_letter()
    Agent-->>UseCase: Cover letter
    UseCase->>HHClient: respond_to_vacancy()
    HHClient->>HHClient: HTTP POST to HH API
    HHClient-->>UseCase: Success
    UseCase->>Repository: create_vacancy_response()
    Repository->>DB: INSERT response
    UseCase->>WebSocket: Send notification
    WebSocket->>Client: Real-time update
```

## Обработка платежа

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant UseCase
    participant YooKassa
    participant Repository
    participant DB
    
    Client->>Router: POST /api/subscription/change-plan
    Router->>UseCase: CreatePaymentUseCase.execute()
    UseCase->>Repository: create_payment()
    Repository->>DB: INSERT payment
    UseCase->>YooKassa: create_payment()
    YooKassa-->>UseCase: Payment URL
    UseCase-->>Router: Payment URL
    Router->>Client: Redirect to YooKassa
    
    Note over Client,YooKassa: User pays
    
    YooKassa->>Router: Webhook notification
    Router->>UseCase: ProcessSuccessfulPaymentUseCase.execute()
    UseCase->>Repository: update_payment_status()
    UseCase->>UseCase: ChangeUserSubscriptionUseCase.execute()
    UseCase->>Repository: update_subscription()
    Repository->>DB: UPDATE subscription
```

## Отправка Telegram уведомления

```mermaid
sequenceDiagram
    participant Worker
    participant UseCase
    participant Repository
    participant TelegramBot
    participant TelegramAPI
    
    Worker->>UseCase: SendTelegramNotificationUseCase.execute()
    UseCase->>Repository: get_telegram_settings()
    Repository->>DB: SELECT settings
    UseCase->>UseCase: Check notification settings
    UseCase->>TelegramBot: send_notification()
    TelegramBot->>TelegramAPI: sendMessage()
    TelegramAPI-->>TelegramBot: Success
    TelegramBot-->>UseCase: Sent
```

## Анализ чатов

```mermaid
sequenceDiagram
    participant Worker
    participant UseCase
    participant HHClient
    participant Agent
    participant Repository
    participant DB
    
    Worker->>UseCase: AnalyzeChatsAndRespondUseCase.execute()
    UseCase->>HHClient: fetch_user_chats()
    HHClient->>HHClient: HTTP GET to HH API
    HHClient-->>UseCase: List[Chat]
    UseCase->>HHClient: fetch_chat_details()
    UseCase->>Agent: analyze_chat(chat)
    Agent->>Agent: LLM analysis
    Agent-->>UseCase: AgentAction
    UseCase->>Repository: create_agent_action()
    Repository->>DB: INSERT action
```

## Связанные разделы

- [Архитектура слоев](layers.md) — описание слоев
- [Доменная модель](domain-model.md) — сущности
