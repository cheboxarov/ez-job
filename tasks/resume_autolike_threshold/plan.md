# План проекта: Порог автолика для резюме

## Обзор проекта
- **Тип**: Расширение функциональности существующего приложения
- **Цель**: Добавить настраиваемый порог автолика (confidence threshold) для каждого резюме с дефолтным значением 50%
- **Технологии**: Python, FastAPI, PostgreSQL, Alembic, React, TypeScript, Ant Design
- **Статус**: Планирование
- **Версия плана**: 1.0

## Принятые решения
- Формат порога: проценты (0-100), хранится как INTEGER в БД
- Дефолтное значение: 50% для всех новых и существующих резюме
- Валидация: минимум 0%, максимум 100%
- UI элемент: слайдер (Slider) в плашке "Автоотклик" на странице детального просмотра резюме
- Обратная совместимость: не требуется

## Этапы работы

| Этап | Название | Статус | Зависимости | Прогресс |
|------|----------|--------|-----------|----------|
| 1 | Миграция БД | Не начато | - | 0% |
| 2 | Domain layer | Не начато | Этап 1 | 0% |
| 3 | Infrastructure layer | Не начато | Этап 2 | 0% |
| 4 | Use cases | Не начато | Этап 3 | 0% |
| 5 | Presentation layer (Backend) | Не начато | Этап 4 | 0% |
| 6 | Frontend | Не начато | Этап 5 | 0% |

## Архитектура системы

### Изменения в таблице БД
```
resumes
├── ... (существующие поля)
└── autolike_threshold (INTEGER, NOT NULL, DEFAULT 50)
    └── Ограничение: CHECK (autolike_threshold >= 0 AND autolike_threshold <= 100)
```

### Изменения в доменной модели
```
Resume
├── ... (существующие поля)
└── autolike_threshold: int = 50
```

### Логика использования порога
- В `ProcessAutoRepliesUseCase` вместо жестко закодированного `confidence >= 0.5` используется `confidence >= (resume.autolike_threshold / 100.0)`
- Порог применяется при фильтрации вакансий перед отправкой автооткликов

### Структура изменений

#### Backend
```
backend/
├── domain/
│   └── entities/
│       └── resume.py (добавить поле autolike_threshold)
├── infrastructure/
│   └── database/
│       ├── models/
│       │   └── resume_model.py (добавить поле autolike_threshold)
│       └── repositories/
│           └── resume_repository.py (обновить методы create, update, _to_domain)
├── domain/
│   └── use_cases/
│       ├── update_resume.py (добавить параметр autolike_threshold)
│       └── process_auto_replies.py (использовать порог из резюме)
├── presentation/
│   ├── dto/
│   │   ├── resume_response.py (добавить поле autolike_threshold)
│   │   └── resume_request.py (добавить поле autolike_threshold в UpdateResumeRequest)
│   └── routers/
│       └── resumes_router.py (передать autolike_threshold в service)
└── application/
    └── services/
        └── resumes_service.py (передать autolike_threshold в use case)
```

#### Frontend
```
frontend/
├── src/
│   ├── types/
│   │   └── api.ts (добавить autolike_threshold в Resume и UpdateResumeRequest)
│   └── pages/
│       └── ResumeDetailPage.tsx (добавить слайдер в плашку "Автоотклик")
```

## История изменений
- v1.0 - Первоначальный план (2025-01-27)
