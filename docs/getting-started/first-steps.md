# Первые шаги

Руководство по запуску проекта "AutoOffer" после установки.

## Запуск проекта локально

### 1. Запуск базы данных

#### Вариант 1: Docker Compose (рекомендуется)

```bash
# Из корня проекта
docker-compose up -d postgres

# Проверка
docker-compose ps
```

#### Вариант 2: Локальный PostgreSQL

Убедитесь, что PostgreSQL запущен:

```bash
# macOS
brew services start postgresql@16

# Linux
sudo systemctl start postgresql
```

### 2. Применение миграций

```bash
cd backend

# Применение всех миграций
alembic upgrade head

# Проверка текущей версии
alembic current
```

Если возникли ошибки, убедитесь, что:
- База данных создана
- Переменные окружения настроены правильно
- Подключение к БД работает

### 3. Запуск backend

```bash
cd backend

# Активация виртуального окружения (если используете)
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Запуск сервера
uvicorn presentation.app:app --host 0.0.0.0 --port 8000 --reload
```

Или используя `main.py`:

```bash
python main.py
```

Backend будет доступен по адресу: `http://localhost:8000`

Проверка работоспособности:
```bash
curl http://localhost:8000/health
# Должен вернуть: {"status":"ok"}
```

### 4. Запуск frontend

Откройте новый терминал:

```bash
cd frontend

# Запуск dev сервера
npm run dev
```

Frontend будет доступен по адресу: `http://localhost:5173`

### 5. Проверка работоспособности

1. Откройте браузер: `http://localhost:5173`
2. Должна открыться главная страница
3. Проверьте API: `http://localhost:8000/docs` (Swagger UI)

## Создание первого пользователя

### Через API

```bash
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Вход
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "testpassword123"
  }'
```

### Через веб-интерфейс

1. Откройте `http://localhost:5173`
2. Нажмите "Регистрация"
3. Заполните форму
4. Войдите в систему

## Базовые операции

### 1. Создание резюме

#### Через API

```bash
# Получите токен из ответа на /auth/login
TOKEN="your-jwt-token"

# Создание резюме
curl -X POST http://localhost:8000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Ваше резюме здесь...",
    "user_parameters": "Дополнительные параметры"
  }'
```

#### Через веб-интерфейс

1. Войдите в систему
2. Перейдите в раздел "Резюме"
3. Нажмите "Создать резюме"
4. Заполните форму и сохраните

### 2. Импорт резюме из HeadHunter

Для импорта резюме из HeadHunter необходимо:

1. Авторизоваться через HeadHunter (см. [Настройка HH авторизации](../user-guide/registration.md))
2. Использовать эндпоинт импорта резюме

### 3. Поиск вакансий

#### Через API

```bash
# Получение списка вакансий для резюме
RESUME_ID="your-resume-id"

curl -X GET "http://localhost:8000/api/resumes/$RESUME_ID/vacancies" \
  -H "Authorization: Bearer $TOKEN"
```

#### Через веб-интерфейс

1. Откройте резюме
2. Перейдите на вкладку "Вакансии"
3. Настройте фильтры
4. Нажмите "Поиск"

### 4. Настройка фильтров

Фильтры позволяют настроить критерии поиска вакансий:

- Зарплата
- Локация
- Ключевые слова
- Стоп-слова
- Исключаемые компании

```bash
# Обновление фильтров резюме
curl -X PUT "http://localhost:8000/api/resumes/$RESUME_ID/filter-settings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "salary_min": 100000,
    "area": "Москва",
    "keywords": ["Python", "FastAPI"],
    "stop_words": ["стажер", "junior"]
  }'
```

## Проверка работы воркеров

Воркеры запускаются автоматически вместе с backend. Проверьте логи:

```bash
# Логи backend (в консоли где запущен uvicorn)
# Должны быть сообщения:
# "Запуск воркеров в lifecycle FastAPI..."
# "Воркеры запущены"
```

Воркеры:
- **Auto Reply Worker** — автоматические отклики
- **Chat Analysis Worker** — анализ чатов
- **Telegram Bot Worker** — Telegram бот

## Следующие шаги

После успешного запуска:

1. Изучите [Архитектуру проекта](../architecture/README.md) для понимания структуры
2. Прочитайте [Руководство по разработке](../development/README.md)
3. Ознакомьтесь с [API документацией](../api/README.md)
4. Настройте [Среду разработки](development-setup.md)

## Полезные команды

### Остановка сервисов

```bash
# Остановка frontend: Ctrl+C в терминале

# Остановка backend: Ctrl+C в терминале

# Остановка БД (Docker)
docker-compose down
```

### Просмотр логов

```bash
# Логи backend
tail -f backend/logs/*.log

# Логи Docker
docker-compose logs -f
```

### Перезапуск после изменений

Backend перезапускается автоматически при изменении кода (благодаря `--reload`).

Frontend перезапускается автоматически при изменении кода (Vite HMR).

## Проблемы?

Если что-то не работает:

1. Проверьте логи приложения
2. Убедитесь, что все сервисы запущены
3. Проверьте переменные окружения
4. См. [Troubleshooting](../troubleshooting/common-issues.md)
