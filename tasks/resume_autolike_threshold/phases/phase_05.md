# Этап 5: Presentation layer (Backend)

## Описание
Обновление DTO (Data Transfer Objects) и роутера для поддержки поля `autolike_threshold` в API.

## Подзадачи

1. **Обновление ResumeResponse DTO**
   - Технологии: Pydantic
   - Файл: `backend/presentation/dto/resume_response.py`
   - Добавить поле `autolike_threshold: int = Field(50, description="Порог автолика в процентах (0-100)")`
   - Обновить метод `from_entity`: добавить `autolike_threshold=resume.autolike_threshold`

2. **Обновление UpdateResumeRequest DTO**
   - Технологии: Pydantic
   - Файл: `backend/presentation/dto/resume_request.py`
   - Добавить поле `autolike_threshold: int | None = Field(None, description="Порог автолика в процентах (0-100)")`
   - Добавить валидацию: если значение передано, проверить диапазон 0-100

3. **Обновление ResumesService**
   - Технологии: Python
   - Файл: `backend/application/services/resumes_service.py`
   - В методе `update_resume` добавить параметр `autolike_threshold: int | None = None`
   - Передать параметр в use case: `autolike_threshold=autolike_threshold`

4. **Обновление роутера resumes_router**
   - Технологии: FastAPI
   - Файл: `backend/presentation/routers/resumes_router.py`
   - В эндпоинте `update_resume` передать `autolike_threshold=request.autolike_threshold` в service

## Зависимости
- Завершение этапа: Этап 4 (use cases должны быть обновлены)

## Критерии завершения
- [ ] ResumeResponse содержит поле `autolike_threshold`
- [ ] UpdateResumeRequest содержит поле `autolike_threshold` с валидацией
- [ ] ResumesService передает `autolike_threshold` в use case
- [ ] Роутер передает `autolike_threshold` из request в service
- [ ] API корректно возвращает и принимает новое поле

## Deliverables
- Обновленный файл `backend/presentation/dto/resume_response.py`
- Обновленный файл `backend/presentation/dto/resume_request.py`
- Обновленный файл `backend/application/services/resumes_service.py`
- Обновленный файл `backend/presentation/routers/resumes_router.py`
