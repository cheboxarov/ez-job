# Глоссарий

Определения терминов и аббревиатур, используемых в документации проекта "Вкатился".

## Архитектурные термины

### Clean Architecture

Подход к проектированию программного обеспечения с четким разделением на слои и правилами зависимостей.

### Domain Layer

Слой домена — ядро приложения, содержит бизнес-логику и не зависит ни от чего.

### Infrastructure Layer

Слой инфраструктуры — реализация интерфейсов из Domain, работа с внешними системами.

### Application Layer

Слой приложения — оркестрация Use Cases, управление транзакциями.

### Presentation Layer

Слой представления — входная точка приложения, обработка HTTP запросов.

### Use Case

Единица бизнес-логики, решающая конкретную задачу.

### Repository Pattern

Паттерн проектирования для абстракции доступа к данным.

### Unit of Work

Паттерн для управления транзакциями и координации репозиториев.

## Бизнес-термины

### Резюме (Resume)

Документ пользователя с описанием опыта и навыков.

### Вакансия (Vacancy)

Предложение работы от работодателя на HeadHunter.

### Отклик (Vacancy Response)

Действие пользователя по отправке резюме на вакансию.

### Подписка (Subscription)

Тарифный план пользователя с определенными лимитами.

### План подписки (Subscription Plan)

Тарифный план с лимитами откликов и ценой.

### Автоотклик

Автоматическая отправка откликов на релевантные вакансии без участия пользователя.

### Порог совпадения (Autolike Threshold)

Минимальная оценка релевантности вакансии для автоматического отклика (0-100).

## Технические термины

### JWT (JSON Web Token)

Токен для аутентификации пользователей.

### WebSocket

Протокол для real-time двусторонней коммуникации.

### LLM (Large Language Model)

Большая языковая модель для генерации текстов и анализа.

### API (Application Programming Interface)

Интерфейс программирования приложений.

### REST (Representational State Transfer)

Архитектурный стиль для веб-сервисов.

### ORM (Object-Relational Mapping)

Технология для работы с БД через объекты.

### Migration

Миграция — изменение структуры базы данных.

### Docker

Платформа для контейнеризации приложений.

### Docker Compose

Инструмент для оркестрации Docker контейнеров.

## Аббревиатуры

- **HH** — HeadHunter
- **API** — Application Programming Interface
- **JWT** — JSON Web Token
- **LLM** — Large Language Model
- **ORM** — Object-Relational Mapping
- **REST** — Representational State Transfer
- **SQL** — Structured Query Language
- **HTTP** — HyperText Transfer Protocol
- **HTTPS** — HTTP Secure
- **SSL** — Secure Sockets Layer
- **TLS** — Transport Layer Security
- **CORS** — Cross-Origin Resource Sharing
- **CSRF** — Cross-Site Request Forgery
- **UUID** — Universally Unique Identifier
- **JSON** — JavaScript Object Notation
- **DTO** — Data Transfer Object
- **FK** — Foreign Key
- **PK** — Primary Key

## Связанные разделы

- [Архитектура](../architecture/README.md) — архитектурные концепции
- [Reference: Таблицы БД](database-tables.md) — структура БД
