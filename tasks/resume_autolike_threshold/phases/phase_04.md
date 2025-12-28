# Этап 4: Use cases

## Описание
Обновление use cases для работы с полем `autolike_threshold`: UpdateResumeUseCase (добавление параметра) и ProcessAutoRepliesUseCase (использование порога из резюме).

## Подзадачи

1. **Обновление UpdateResumeUseCase**
   - Технологии: Python
   - Файл: `backend/domain/use_cases/update_resume.py`
   - Добавить параметр `autolike_threshold: int | None = None` в метод `execute`
   - Обновить создание `updated_resume`: добавить логику обновления `autolike_threshold` (если передан, использовать новое значение, иначе оставить существующее)
   - Обновить docstring метода `execute`

2. **Обновление ProcessAutoRepliesUseCase**
   - Технологии: Python
   - Файл: `backend/domain/use_cases/process_auto_replies.py`
   - В методе `_process_resume` найти строку с фильтрацией `confidence >= 0.5`
   - Заменить жестко закодированное значение на динамическое: `confidence >= (resume.autolike_threshold / 100.0)`
   - Обновить логирование: вместо "confidence >= 50%" использовать значение из резюме
   - Обновить docstring класса с описанием использования порога из резюме

## Зависимости
- Завершение этапа: Этап 3 (инфраструктурный слой должен быть обновлен)

## Критерии завершения
- [ ] UpdateResumeUseCase принимает параметр `autolike_threshold`
- [ ] UpdateResumeUseCase корректно обновляет поле при передаче значения
- [ ] ProcessAutoRepliesUseCase использует порог из резюме вместо жестко закодированного 0.5
- [ ] Логирование обновлено для отображения актуального порога

## Deliverables
- Обновленный файл `backend/domain/use_cases/update_resume.py`
- Обновленный файл `backend/domain/use_cases/process_auto_replies.py`
