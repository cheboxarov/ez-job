# Этап 3: Infrastructure layer

## Описание
Обновление SQLAlchemy модели ResumeModel и репозитория ResumeRepository для работы с полем `autolike_threshold`.

## Подзадачи

1. **Обновление SQLAlchemy модели ResumeModel**
   - Технологии: SQLAlchemy
   - Файл: `backend/infrastructure/database/models/resume_model.py`
   - Добавить поле `autolike_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=50)`
   - Обновить docstring

2. **Обновление репозитория ResumeRepository**
   - Технологии: SQLAlchemy, AsyncSession
   - Файл: `backend/infrastructure/database/repositories/resume_repository.py`
   - Обновить метод `create`: добавить `autolike_threshold=resume.autolike_threshold` при создании модели
   - Обновить метод `update`: добавить `model.autolike_threshold = resume.autolike_threshold`
   - Обновить метод `_to_domain`: добавить `autolike_threshold=model.autolike_threshold` при преобразовании

## Зависимости
- Завершение этапа: Этап 2 (доменная сущность должна быть обновлена)

## Критерии завершения
- [ ] Поле `autolike_threshold` добавлено в ResumeModel
- [ ] Метод `create` обновлен для работы с новым полем
- [ ] Метод `update` обновлен для работы с новым полем
- [ ] Метод `_to_domain` обновлен для преобразования нового поля

## Deliverables
- Обновленный файл `backend/infrastructure/database/models/resume_model.py`
- Обновленный файл `backend/infrastructure/database/repositories/resume_repository.py`
