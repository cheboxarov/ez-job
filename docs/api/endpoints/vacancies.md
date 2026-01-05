# Эндпоинты: Вакансии

Документация эндпоинтов для работы с вакансиями.

## Базовый путь

```
/api/vacancies
```

## Поиск вакансий

**Endpoint:** `GET /api/vacancies`

**Описание:** Поиск вакансий с фильтрацией.

**Аутентификация:** Требуется

**Query Parameters:**
- `text` (string, optional) — поисковый запрос
- `area` (int, optional) — ID региона
- `salary` (int, optional) — желаемая зарплата
- `page` (int, optional) — номер страницы

**Response:** `200 OK`
```json
{
  "vacancies": [...],
  "total": 100,
  "page": 1
}
```

## Получение деталей вакансии

**Endpoint:** `GET /api/vacancies/{vacancy_id}`

**Описание:** Получение детальной информации о вакансии.

**Аутентификация:** Требуется

**Response:** `200 OK` — детали вакансии

## Генерация сопроводительного письма

**Endpoint:** `POST /api/vacancies/{vacancy_id}/cover-letter`

**Описание:** Генерация сопроводительного письма для вакансии.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** `200 OK`
```json
{
  "cover_letter": "Уважаемый работодатель...",
  "vacancy_id": "12345678",
  "resume_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Отклик на вакансию

**Endpoint:** `POST /api/vacancies/{vacancy_id}/respond`

**Описание:** Отправка отклика на вакансию.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440000",
  "cover_letter": "Текст сопроводительного письма"
}
```

**Response:** `201 Created`

## Связанные разделы

- [Резюме](resumes.md) — работа с резюме
- [API Overview](../README.md) — обзор API
