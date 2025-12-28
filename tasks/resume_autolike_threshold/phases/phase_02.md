# Этап 2: Domain layer

## Описание
Обновление доменной сущности Resume для добавления поля `autolike_threshold` с дефолтным значением 50.

## Подзадачи

1. **Обновление доменной сущности Resume**
   - Технологии: Python dataclasses
   - Файл: `backend/domain/entities/resume.py`
   - Добавить поле `autolike_threshold: int = 50`
   - Обновить docstring с описанием нового поля

## Зависимости
- Завершение этапа: Этап 1 (миграция БД должна быть применена)

## Критерии завершения
- [ ] Поле `autolike_threshold` добавлено в класс Resume
- [ ] Дефолтное значение установлено на 50
- [ ] Docstring обновлен

## Deliverables
- Обновленный файл `backend/domain/entities/resume.py`
