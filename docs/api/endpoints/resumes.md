# Эндпоинты: Резюме

Документация эндпоинтов для работы с резюме.

## Базовый путь

```
/api/resumes
```

## Создание резюме

**Endpoint:** `POST /api/resumes`

**Описание:** Создание нового резюме для текущего пользователя.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "content": "Текст резюме...",
  "user_parameters": "Дополнительные параметры (опционально)"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "content": "Текст резюме...",
  "user_parameters": "Дополнительные параметры",
  "external_id": null,
  "headhunter_hash": null,
  "is_auto_reply": false,
  "autolike_threshold": 50
}
```

**Пример:**
```bash
curl -X POST http://localhost:8000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Опытный Python разработчик...",
    "user_parameters": "Ищу удаленную работу"
  }'
```

## Получение списка резюме

**Endpoint:** `GET /api/resumes`

**Описание:** Получение списка всех резюме текущего пользователя.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "resumes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "content": "Текст резюме...",
      "is_auto_reply": false,
      "autolike_threshold": 50
    }
  ]
}
```

## Получение резюме по ID

**Endpoint:** `GET /api/resumes/{resume_id}`

**Описание:** Получение детальной информации о резюме.

**Аутентификация:** Требуется

**Path Parameters:**
- `resume_id` (UUID) — ID резюме

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440001",
  "content": "Текст резюме...",
  "user_parameters": "Дополнительные параметры",
  "external_id": "12345678",
  "headhunter_hash": "abc123",
  "is_auto_reply": true,
  "autolike_threshold": 70
}
```

## Обновление резюме

**Endpoint:** `PUT /api/resumes/{resume_id}`

**Описание:** Обновление существующего резюме.

**Аутентификация:** Требуется

**Path Parameters:**
- `resume_id` (UUID) — ID резюме

**Request Body:**
```json
{
  "content": "Обновленный текст резюме...",
  "user_parameters": "Новые параметры"
}
```

**Response:** `200 OK` — обновленное резюме

## Удаление резюме

**Endpoint:** `DELETE /api/resumes/{resume_id}`

**Описание:** Удаление резюме.

**Аутентификация:** Требуется

**Path Parameters:**
- `resume_id` (UUID) — ID резюме

**Response:** `204 No Content`

## Оценка резюме

**Endpoint:** `POST /api/resumes/{resume_id}/evaluate`

**Описание:** Оценка резюме AI агентом.

**Аутентификация:** Требуется

**Path Parameters:**
- `resume_id` (UUID) — ID резюме

**Response:** `200 OK`
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": 85,
  "feedback": "Резюме хорошо структурировано...",
  "suggestions": ["Добавьте больше деталей о проектах"]
}
```

## Импорт резюме из HeadHunter

**Endpoint:** `POST /api/resumes/import-from-hh`

**Описание:** Импорт резюме из HeadHunter.

**Аутентификация:** Требуется (с HH авторизацией)

**Request Body:**
```json
{
  "hh_resume_id": "12345678"
}
```

**Response:** `201 Created` — созданное резюме

## Получение вакансий для резюме

**Endpoint:** `GET /api/resumes/{resume_id}/vacancies`

**Описание:** Поиск и фильтрация вакансий для резюме.

**Аутентификация:** Требуется

**Path Parameters:**
- `resume_id` (UUID) — ID резюме

**Query Parameters:**
- `page` (int, optional) — номер страницы (default: 1)
- `per_page` (int, optional) — элементов на странице (default: 20)

**Response:** `200 OK`
```json
{
  "vacancies": [
    {
      "id": "12345678",
      "name": "Python Developer",
      "url": "https://hh.ru/vacancy/12345678",
      "salary": {"from": 150000, "to": 250000},
      "employer": {"name": "Company Name"},
      "match_score": 85
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

## Настройки фильтрации резюме

### Получение настроек

**Endpoint:** `GET /api/resumes/{resume_id}/filter-settings`

**Описание:** Получение настроек фильтрации для резюме.

**Аутентификация:** Требуется

**Response:** `200 OK`
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440000",
  "salary_min": 150000,
  "area": "Москва",
  "keywords": "Python, FastAPI",
  "stop_words": "стажер, junior",
  "excluded_companies": "Company1, Company2"
}
```

### Обновление настроек

**Endpoint:** `PUT /api/resumes/{resume_id}/filter-settings`

**Описание:** Обновление настроек фильтрации.

**Аутентификация:** Требуется

**Request Body:**
```json
{
  "salary_min": 200000,
  "area": "Санкт-Петербург",
  "keywords": "Python, Django, PostgreSQL",
  "stop_words": "стажер",
  "excluded_companies": "BadCompany"
}
```

**Response:** `200 OK` — обновленные настройки

## Коды ошибок

- `400 Bad Request` — неверные данные запроса
- `401 Unauthorized` — требуется аутентификация
- `403 Forbidden` — резюме принадлежит другому пользователю
- `404 Not Found` — резюме не найдено
- `500 Internal Server Error` — внутренняя ошибка сервера

## Связанные разделы

- [API Overview](../README.md) — обзор API
- [Вакансии](vacancies.md) — работа с вакансиями
